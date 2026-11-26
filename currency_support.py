"""Offline ISO 4217 currency metadata and backwards-compatible storage migration."""

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


CATALOG = json.loads((Path(__file__).resolve().parent / "assets" / "currencies.json").read_text(encoding="utf-8"))
CURRENCIES = CATALOG["currencies"]


def currency_label(code):
    return f"{code} — {CURRENCIES[code]['name']}"


def currency_unit(code):
    return "RM" if code == "MYR" else code


def currency_digits(code):
    return CURRENCIES[code]["digits"]


def currency_step(code):
    return float(Decimal(1).scaleb(-currency_digits(code)))


def format_money(amount, code="MYR"):
    return f"{currency_unit(code)} {amount:,.{currency_digits(code)}f}"


def rounded_amount(amount, code):
    return float(Decimal(str(amount)).quantize(
        Decimal(1).scaleb(-currency_digits(code)), rounding=ROUND_HALF_UP))


def migrate_currencies(conn):
    """Run inside a transaction; preserve every legacy amount as MYR."""
    for table in ("transactions", "savings_goals", "budgets"):
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if "currency" not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN currency TEXT NOT NULL DEFAULT 'MYR'")
    conn.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY, value TEXT NOT NULL
    )""")
