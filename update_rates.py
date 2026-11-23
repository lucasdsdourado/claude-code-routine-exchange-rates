"""Fetch USD exchange rates and maintain a CSV history + markdown summary."""

import csv
import io
import json
import os
import urllib.request
from datetime import datetime, timezone

API_URL = "https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,GBP,BRL"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_PATH = os.path.join(DATA_DIR, "rates.csv")
SUMMARY_PATH = os.path.join(DATA_DIR, "summary.md")
FIELDNAMES = ["date", "currency", "rate", "updated_at"]


def fetch_rates():
    """Fetch latest rates from the Frankfurter API."""
    with urllib.request.urlopen(API_URL) as resp:
        data = json.loads(resp.read().decode())
    return data["date"], data["rates"]


def load_csv():
    """Load existing CSV rows. Returns a list of dicts."""
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(rows):
    """Write all rows back to the CSV."""
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def upsert_rates(existing_rows, date, rates, now_utc):
    """Insert or update rows. Returns (updated_rows, inserted_count, updated_count)."""
    rows_by_key = {(r["date"], r["currency"]): r for r in existing_rows}
    inserted = 0
    updated = 0

    for currency, rate in sorted(rates.items()):
        key = (date, currency)
        row = {"date": date, "currency": currency, "rate": str(rate), "updated_at": now_utc}
        if key in rows_by_key:
            rows_by_key[key] = row
            updated += 1
        else:
            rows_by_key[key] = row
            inserted += 1

    all_rows = list(rows_by_key.values())
    all_rows.sort(key=lambda r: (r["date"], r["currency"]))
    return all_rows, inserted, updated


def write_summary(rows, now_utc):
    """Write a markdown summary with the latest rate per currency."""
    latest = {}
    for r in rows:
        cur = r["currency"]
        if cur not in latest or r["date"] > latest[cur]["date"]:
            latest[cur] = r

    lines = [
        "# Exchange Rate Summary",
        "",
        f"Last updated: {now_utc}",
        "",
        "| Currency | Rate (per 1 USD) | Date |",
        "|----------|-----------------|------|",
    ]
    for cur in sorted(latest):
        r = latest[cur]
        lines.append(f"| {r['currency']} | {r['rate']} | {r['date']} |")
    lines.append("")

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    date, rates = fetch_rates()
    existing = load_csv()
    all_rows, inserted, updated = upsert_rates(existing, date, rates, now_utc)

    save_csv(all_rows)
    write_summary(all_rows, now_utc)

    print(f"Rows inserted: {inserted}, updated: {updated}")


if __name__ == "__main__":
    main()
