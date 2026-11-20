"""Local receipt OCR and conservative extraction; never writes financial records."""

import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageOps, UnidentifiedImageError


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
EXPENSE_CATEGORIES = (
    "Food", "Transportation", "Shopping", "Bills", "Education",
    "Entertainment", "Health", "Other",
)


class ReceiptError(ValueError):
    """An actionable upload, OCR, or extraction error."""


@dataclass(frozen=True)
class ReceiptDraft:
    merchant: str
    amount: Optional[Decimal]
    transaction_date: Optional[date]
    currency: Optional[str]
    warnings: Tuple[str, ...]
    raw_text: str


def prepare_image(data: bytes) -> bytes:
    """Validate content, apply phone orientation, strip metadata, and bound OCR size."""
    if not data:
        raise ReceiptError("Choose a receipt photo first.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ReceiptError("The receipt photo is too large. Choose an image under 10 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise ReceiptError("Use a JPG, PNG, or WebP receipt photo.")
                if source.width * source.height > MAX_IMAGE_PIXELS:
                    raise ReceiptError("The photo is too large to scan. Resize it to under 20 megapixels.")
                image = ImageOps.exif_transpose(source).convert("RGBA")
                background = Image.new("RGBA", image.size, "white")
                image = Image.alpha_composite(background, image).convert("RGB")
                image.thumbnail((2600, 3600))
                output = io.BytesIO()
                image.save(output, format="PNG")
                return output.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning, ValueError) as exc:
        if isinstance(exc, ReceiptError):
            raise
        raise ReceiptError("This photo cannot be read. Upload a valid JPG, PNG, or WebP image.") from exc


def ocr_backend() -> Optional[str]:
    if sys.platform == "darwin" and shutil.which("swift"):
        return "Apple Vision"
    if shutil.which("tesseract"):
        return "Tesseract"
    return None


def recognize_text(image: bytes) -> str:
    backend = ocr_backend()
    if backend is None:
        raise ReceiptError("Receipt scanning needs a local OCR engine. See Scanner setup below.")
    if backend == "Apple Vision":
        command = [
            shutil.which("swift"), "-module-cache-path",
            str(Path(tempfile.gettempdir()) / "smart-budget-swift-cache"),
            str(Path(__file__).with_name("receipt_ocr.swift")),
        ]
    else:
        command = [shutil.which("tesseract"), "stdin", "stdout", "-l", "eng", "--psm", "6"]
    try:
        result = subprocess.run(command, input=image, capture_output=True, timeout=45, check=True)
        text = result.stdout.decode("utf-8")
        if backend == "Apple Vision":
            text = json.loads(text)["text"]
    except subprocess.TimeoutExpired as exc:
        raise ReceiptError("Scanning took too long. Try a smaller, clearly cropped receipt photo.") from exc
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError, KeyError) as exc:
        raise ReceiptError("The local scanner could not read this photo. Try a clearer photo or check Scanner setup.") from exc
    if not text.strip():
        raise ReceiptError("No text was found. Try a sharp, upright photo with the full receipt in good light.")
    return text


_MONEY = re.compile(r"(?<![\w.,])(-?\s*(?:\d{1,3}(?:,\d{3})+|\d+)[.,]\d{2})(?![\d.,])")
_TOTAL = re.compile(r"\b(grand\s+total|total\s+(?:amount|due|paid|payable)|amount\s+(?:due|paid|payable)|net\s+total|jumlah\s+bayar|jumlah|total)\b", re.I)
_NON_TOTAL = re.compile(r"\b(sub\s*total|tax\s+total|total\s+(?:tax|savings?|discount|items?|qty|quantity)|cash|tendered|change|balance|discount|tax|sst|gst|vat)\b", re.I)


def _amount_on_line(line: str) -> Optional[Decimal]:
    line = re.sub(r"\b(RM|MYR|USD|SGD|EUR|GBP|AUD|JPY|THB|IDR|RP)(?=\d)", r"\1 ", line, flags=re.I)
    if re.search(r"\([\d.,]+\)", line):
        return None  # Parentheses often mean a refund/negative amount.
    matches = _MONEY.findall(line)
    if matches:
        token = matches[-1].replace(" ", "")
        token = token.replace(",", "") if "." in token else token.replace(",", ".")
    else:
        # Whole ringgit amounts are accepted only on a total/value-only line.
        match = re.search(r"(?:^|\b(?:RM|MYR)\s*|:\s*|\s)(-?\d+)\s*$", line, re.I)
        if not match:
            return None
        token = match.group(1)
    try:
        amount = Decimal(token)
    except InvalidOperation:
        return None
    return amount if Decimal("0") < amount <= Decimal("1000000000000") else None


def _extract_amount(lines):
    candidates = []
    for index, line in enumerate(lines):
        match = _TOTAL.search(line)
        if not match or _NON_TOTAL.search(line):
            continue
        amount = _amount_on_line(line[match.end():])
        if amount is None and not line[match.end():].strip(" :.-") and index + 1 < len(lines):
            following = lines[index + 1]
            if not re.search(r"[A-Za-z]", re.sub(r"\b(?:RM|MYR)\b", "", following, flags=re.I)):
                amount = _amount_on_line(following)
        if amount is not None:
            priority = 1 if match.group().lower() in {"total", "jumlah"} else 2
            candidates.append((priority, index, amount))
    if not candidates:
        return None, []
    priority = max(item[0] for item in candidates)
    best = [item for item in candidates if item[0] == priority]
    notes = []
    if len({item[2] for item in candidates}) > 1:
        notes.append("Several totals were found. Check that the amount is the final amount paid.")
    return best[-1][2], notes


def _extract_date(lines):
    candidates = []
    for line in lines:
        # Do not mistake a card's expiry date or an offer deadline for the purchase date.
        if re.search(r"\b(expir\w*|valid\s+(?:until|thru)|due\s+date)\b", line, re.I):
            continue
        found = None
        ambiguous = False
        iso = re.search(r"\b(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})\b", line)
        numeric = re.search(r"\b(\d{1,2})[-/.](\d{1,2})[-/.](20\d{2}|\d{2})\b", line)
        try:
            if iso:
                found = date(*map(int, iso.groups()))
            elif numeric:
                day, month, year = map(int, numeric.groups())
                year += 2000 if year < 100 else 0
                # Malaysian receipts normally use day/month/year.
                if month > 12 and day <= 12:
                    day, month = month, day
                ambiguous = day <= 12 and month <= 12 and day != month
                found = date(year, month, day)
            else:
                named = re.search(r"\b(\d{1,2})[- /]([A-Za-z]{3,9})[- ,/]+(20\d{2}|\d{2})\b", line)
                if named:
                    token = " ".join(named.groups())
                    for fmt in ("%d %b %Y", "%d %B %Y", "%d %b %y", "%d %B %y"):
                        try:
                            found = datetime.strptime(token, fmt).date()
                            break
                        except ValueError:
                            continue
        except ValueError:
            continue
        if found:
            candidates.append((found, ambiguous))
    if not candidates:
        return None, []
    chosen, ambiguous = candidates[0]
    notes = []
    if ambiguous:
        notes.append("The numeric date is ambiguous; day/month/year was assumed. Check the transaction date.")
    if len({item[0] for item in candidates}) > 1:
        notes.append("Several dates were found. Check the purchase date against the receipt.")
    return chosen, notes


def _extract_merchant(lines):
    excluded = re.compile(
        r"\b(receipt|invoice|welcome|thank|date|time|tel|phone|fax|cashier|table|order|"
        r"sst|gst|vat|reg|registration|no|address|jalan|street|road|www)\b|https?://|@", re.I)
    for line in lines[:10]:
        if len(line) >= 3 and re.search(r"[A-Za-z]{2}", line) and not excluded.search(line):
            if _TOTAL.search(line) or _MONEY.search(line):
                continue
            return line[:200]
    return ""


def extract_receipt(text: str) -> ReceiptDraft:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ReceiptError("No receipt text was found. Try another photo.")
    amount, amount_notes = _extract_amount(lines)
    when, date_notes = _extract_date(lines)
    merchant = _extract_merchant(lines)
    currencies = set()
    currency_patterns = {
        "MYR": r"\b(?:RM|MYR)(?![A-Za-z])", "USD": r"\bUSD(?![A-Za-z])|US\$",
        "SGD": r"\bSGD(?![A-Za-z])|S\$", "EUR": r"\bEUR(?![A-Za-z])|€",
        "GBP": r"\bGBP(?![A-Za-z])|£", "AUD": r"\bAUD(?![A-Za-z])|A\$",
        "JPY": r"\bJPY(?![A-Za-z])|¥", "THB": r"\bTHB(?![A-Za-z])|฿", "IDR": r"\b(?:IDR|Rp)(?![A-Za-z])",
    }
    for currency, pattern in currency_patterns.items():
        if re.search(pattern, text, re.I):
            currencies.add(currency)
    currency = next(iter(currencies)) if len(currencies) == 1 else None
    notes = amount_notes + date_notes
    if not merchant:
        notes.append("Merchant was not found. Enter the merchant name.")
    if amount is None:
        notes.append("A reliable final total was not found. Enter the amount paid.")
    if when is None:
        notes.append("Transaction date was not found. Choose the purchase date.")
    if currency is None:
        notes.append("Currency is unclear. Confirm the amount is in Malaysian Ringgit (RM).")
    elif currency != "MYR":
        notes.append(f"This receipt appears to use {currency}. Enter its RM equivalent; currency conversion is not automatic.")
    return ReceiptDraft(merchant, amount, when, currency, tuple(notes), text)


def scan_receipt(data: bytes) -> Tuple[ReceiptDraft, bytes]:
    image = prepare_image(data)
    return extract_receipt(recognize_text(image)), image
