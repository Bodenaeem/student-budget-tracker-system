"""Latest reference rates with a local cache and explicit manual overrides."""

import json
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.error import URLError
from urllib.request import Request, urlopen

from currency_support import CURRENCIES

API_URL = "https://api.frankfurter.dev/v2/rates?base="


def valid_rate(value):
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Enter a positive, finite exchange rate.") from None
    if not rate.is_finite() or not Decimal("1e-18") <= rate <= Decimal("1e18"):
        raise ValueError("Enter a positive, finite exchange rate between 1e-18 and 1e18.")
    return rate


def fetch_rates(target):
    """The provider quotes 1 target in source units; invert for source → target."""
    request = Request(API_URL + target, headers={"User-Agent": "SmartBudgetTracker/2.0"})
    with urlopen(request, timeout=8) as response:
        payload = json.loads(response.read(1_000_000))
    if not isinstance(payload, list) or not payload:
        raise ValueError("The exchange-rate provider returned no rates.")
    rates = {}
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError("The exchange-rate provider returned invalid data.")
        source = row.get("quote")
        if row.get("base") != target or source not in CURRENCIES or source == target:
            continue
        as_of = date.fromisoformat(row["date"]).isoformat()
        rates[source] = (Decimal(1) / valid_rate(row["rate"]), as_of)
    if not rates:
        raise ValueError("The exchange-rate provider returned no supported rates.")
    return rates


def init_rate_storage(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS exchange_rates (
        source_currency TEXT NOT NULL, target_currency TEXT NOT NULL,
        rate TEXT NOT NULL, as_of TEXT NOT NULL, fetched_at REAL NOT NULL,
        origin TEXT NOT NULL, PRIMARY KEY(source_currency, target_currency)
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS exchange_rate_updates (
        target_currency TEXT PRIMARY KEY, attempted_at REAL NOT NULL, error TEXT
    )""")


def save_manual_rate(conn, source, target, rate, as_of):
    if source not in CURRENCIES or target not in CURRENCIES or source == target:
        raise ValueError("Choose two different supported currencies.")
    rate = valid_rate(rate)
    as_of = date.fromisoformat(str(as_of)).isoformat()
    with conn:
        conn.execute("""INSERT INTO exchange_rates VALUES(?,?,?,?,?, 'manual')
            ON CONFLICT(source_currency,target_currency) DO UPDATE SET
            rate=excluded.rate, as_of=excluded.as_of, fetched_at=excluded.fetched_at, origin='manual'
        """, (source, target, str(rate), as_of, time.time()))


def load_rates(conn, target, sources, force=False, now=None):
    """Refresh daily when needed; failed requests retry at most once per hour.

    Manual overrides persist until the user explicitly refreshes automatic rates.
    Missing rates remain missing: callers must never substitute a rate of 1.
    """
    now = time.time() if now is None else now

    def read_cache():
        return {row[0]: {"rate": valid_rate(row[1]), "date": row[2],
                         "fetched_at": row[3], "origin": row[4]}
                for row in conn.execute(
                    "SELECT source_currency,rate,as_of,fetched_at,origin FROM exchange_rates WHERE target_currency=?",
                    (target,))}

    cached = read_cache()
    needed = set(sources) - {target}
    refresh = any(code not in cached or (
        cached[code]["origin"] != "manual" and now - cached[code]["fetched_at"] >= 86400)
        for code in needed)
    last = conn.execute("SELECT attempted_at,error FROM exchange_rate_updates WHERE target_currency=?", (target,)).fetchone()
    error = last[1] if last else None
    if force or (refresh and (not last or now - last[0] >= 3600)):
        try:
            received = fetch_rates(target)
            with conn:
                for source, (rate, as_of) in received.items():
                    if not force and source in cached and cached[source]["origin"] == "manual":
                        continue
                    conn.execute("""INSERT INTO exchange_rates VALUES(?,?,?,?,?, 'Frankfurter')
                        ON CONFLICT(source_currency,target_currency) DO UPDATE SET
                        rate=excluded.rate,as_of=excluded.as_of,fetched_at=excluded.fetched_at,origin=excluded.origin
                    """, (source, target, str(rate), as_of, now))
            error = None
        except (URLError, OSError, ValueError, KeyError, TypeError, ArithmeticError):
            error = "Automatic rates could not be loaded. Cached rates remain available; you can enter a manual rate."
        with conn:
            conn.execute("""INSERT INTO exchange_rate_updates VALUES(?,?,?)
                ON CONFLICT(target_currency) DO UPDATE SET attempted_at=excluded.attempted_at,error=excluded.error
            """, (target, now, error))
        cached = read_cache()
    cached[target] = {"rate": Decimal(1), "date": "", "fetched_at": now, "origin": "same currency"}
    return cached, error


def convert_records(records, fields, target, rates):
    """Preserve native values for editing/export; missing conversions are explicit."""
    converted = []
    for record in records:
        source = record["currency"]
        result = {**record, "original_currency": source, "currency": target}
        for field in fields:
            result["original_" + field] = record[field]
            result[field] = (float(Decimal(str(record[field])) * rates[source]["rate"])
                             if source in rates else None)
        result["rate"] = float(rates[source]["rate"]) if source in rates else None
        result["rate_date"] = rates[source]["date"] if source in rates else ""
        converted.append(result)
    return converted
