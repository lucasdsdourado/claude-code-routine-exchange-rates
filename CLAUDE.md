# Exchange Rate Tracker

A single-file Python script that fetches daily USD exchange rates (EUR, GBP, BRL) from the Frankfurter API and keeps a local CSV history.

## How to run

```bash
python update_rates.py
```

No dependencies beyond Python 3.6+ standard library.

## What it does

1. Fetches the latest USD rates for EUR, GBP, and BRL from `api.frankfurter.dev`.
2. Upserts rows into `data/rates.csv` (columns: date, currency, rate, updated_at).
3. Rewrites `data/summary.md` with a table of the latest rate per currency.
4. Prints how many rows were inserted vs updated.

## Project structure

- `update_rates.py` — main script
- `data/rates.csv` — rate history (auto-created)
- `data/summary.md` — human-readable summary (auto-created)
