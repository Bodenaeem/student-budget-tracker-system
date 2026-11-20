"""Receipt upload, review, and explicit expense confirmation for Streamlit."""

import hashlib
import sqlite3
from decimal import Decimal

import streamlit as st

from receipt_scanner import (
    EXPENSE_CATEGORIES, MAX_UPLOAD_BYTES, ReceiptError, extract_receipt,
    ocr_backend, prepare_image, recognize_text,
)


def clear_receipt_session():
    """Discard the upload and draft, including widget values, for this session."""
    epoch = st.session_state.get("receipt_upload_epoch", 0) + 1
    for key in list(st.session_state):
        if key.startswith("receipt_") and key != "receipt_saved_notice":
            del st.session_state[key]
    st.session_state.receipt_upload_epoch = epoch


def _scanner_setup():
    with st.expander("Scanner setup"):
        st.write("Scanning runs on the computer hosting this app and needs a local OCR engine.")
        st.markdown(
            "- **macOS:** Apple Vision is used when Swift is available through Apple's Command Line Tools.\n"
            "- **Windows/Linux:** install Tesseract with English language data and add `tesseract` to PATH.\n"
            "- Restart Streamlit after installing an engine. You can also use **Manual entry**."
        )


def render_receipt_scanner(transactions, save_expense):
    if st.session_state.get("receipt_reset_pending"):
        clear_receipt_session()
    notice = st.session_state.pop("receipt_saved_notice", None)
    if notice:
        st.success(notice)

    st.markdown("### Receipt scanner")
    st.caption("Upload → Extract → Review → Confirm expense")
    st.caption(
        "Photos are processed locally on the app server, kept in this session, and aren't saved "
        "to the database or sent to an external OCR service. Only the expense details you confirm are saved."
    )
    epoch = st.session_state.get("receipt_upload_epoch", 0)
    uploaded = st.file_uploader(
        "Upload a receipt photo", type=["jpg", "jpeg", "png", "webp"],
        key=f"receipt_upload_{epoch}", help="JPG, PNG, or WebP. Maximum 10 MB and 20 megapixels.",
    )
    if uploaded is None:
        st.session_state.pop("receipt_scan_result", None)
        st.session_state.pop("receipt_source_id", None)
        st.session_state.pop("receipt_image", None)
        st.info("Choose a clear photo with the merchant, purchase date, and final total visible.")
        if ocr_backend() is None:
            st.warning("A local OCR engine is needed to scan receipts.")
            _scanner_setup()
        return
    if uploaded.size > MAX_UPLOAD_BYTES:
        st.error("The receipt photo is too large. Choose an image under 10 MB.")
        st.session_state.pop("receipt_scan_result", None)
        st.session_state.pop("receipt_image", None)
        st.session_state.pop("receipt_source_id", None)
        return

    data = uploaded.getvalue()
    source_id = hashlib.sha256(data).hexdigest()
    if st.session_state.get("receipt_source_id") != source_id:
        st.session_state.pop("receipt_scan_result", None)
        st.session_state.pop("receipt_image", None)
        st.session_state.pop("receipt_image_error", None)
        st.session_state.receipt_source_id = source_id
        try:
            st.session_state.receipt_image = prepare_image(data)
        except ReceiptError as exc:
            st.session_state.receipt_image_error = str(exc)
    if "receipt_image" not in st.session_state:
        st.error(st.session_state.get("receipt_image_error", "Choose another receipt photo."))
        return

    preview, review = st.columns([0.85, 1.15], gap="large")
    with preview:
        st.image(st.session_state.receipt_image, caption="Your receipt", width="stretch")
        st.button("Discard receipt", on_click=clear_receipt_session, use_container_width=True)

    with review:
        backend = ocr_backend()
        if st.button("Extract receipt details", type="primary", disabled=backend is None,
                     use_container_width=True):
            # A failed rescan cannot leave an earlier draft available for confirmation.
            st.session_state.pop("receipt_scan_result", None)
            with st.spinner("Reading your receipt… The first scan may take a little longer."):
                try:
                    text = recognize_text(st.session_state.receipt_image)
                    st.session_state.receipt_scan_result = extract_receipt(text)
                    st.session_state.receipt_review_revision = st.session_state.get("receipt_review_revision", 0) + 1
                except ReceiptError as exc:
                    st.error(str(exc))
                    _scanner_setup()
        if backend is None:
            st.warning("A local OCR engine is needed to scan receipts.")
            _scanner_setup()

        draft = st.session_state.get("receipt_scan_result")
        if draft is None:
            st.caption("Extract the details to prepare an expense. Nothing is saved until you confirm.")
            return

        st.markdown("#### Review expense")
        st.caption("Text recognition can make mistakes. Check every field against the photo.")
        for note in draft.warnings:
            st.warning(note)
        revision = st.session_state.get("receipt_review_revision", 0)
        form_id = f"receipt_review_{source_id[:12]}_{revision}"
        foreign_currency = draft.currency not in (None, "MYR")
        initial_amount = float(draft.amount) if draft.amount and not foreign_currency else 0.0

        with st.form(form_id):
            merchant = st.text_input("Merchant", value=draft.merchant, max_chars=200)
            amount = st.number_input(
                "Receipt amount (RM)", min_value=0.0, max_value=1_000_000_000_000.0,
                value=initial_amount, step=0.01, format="%.2f",
                help="Enter the final amount paid in Malaysian Ringgit, including any taxes.",
            )
            when = st.date_input("Receipt date", value=draft.transaction_date, format="DD/MM/YYYY")
            category = st.selectbox("Expense category", EXPENSE_CATEGORIES, index=len(EXPENSE_CATEGORIES) - 1)
            notes = st.text_input("Notes (optional)", placeholder="What was this for?", max_chars=500)
            duplicates = [
                transaction for transaction in transactions
                if transaction["type"] == "Expense" and when is not None
                and transaction["date"] == when.isoformat()
                and Decimal(str(transaction["amount"])).quantize(Decimal("0.01")) == Decimal(str(amount)).quantize(Decimal("0.01"))
            ]
            allow_duplicate = False
            if duplicates:
                st.warning("An expense with this date and amount already exists. Check Transaction History before saving again.")
                allow_duplicate = st.checkbox("I checked the existing expenses and want to save another.")
            confirmed = st.checkbox("I checked the receipt and confirm these details and the amount in RM.")
            submitted = st.form_submit_button("Confirm & save expense", type="primary", use_container_width=True)

        with st.expander("View extracted receipt text"):
            st.text(draft.raw_text)

        if submitted:
            if not merchant.strip():
                st.error("Enter the merchant name before saving.")
            elif amount < 0.01:
                st.error("Enter an amount of at least RM 0.01.")
            elif when is None:
                st.error("Choose the purchase date before saving.")
            elif not confirmed:
                st.error("Review the fields and tick the confirmation box before saving.")
            elif duplicates and not allow_duplicate:
                st.error("Confirm that this is a separate expense before saving another matching entry.")
            else:
                description = merchant.strip() + (f" — {notes.strip()}" if notes.strip() else "")
                try:
                    save_expense(amount=amount, category=category, description=description, when=when)
                except sqlite3.Error:
                    st.error("The expense could not be saved. Your draft is still here; try again.")
                else:
                    st.session_state.receipt_saved_notice = "Receipt expense saved successfully. You can view it in Transaction History."
                    st.session_state.receipt_reset_pending = True
                    st.rerun()
