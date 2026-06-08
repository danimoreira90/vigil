# Data Dictionary

**Status:** Draft v0.1 | **Date:** 2026-06-06 | **Owner:** Daniel

> Schema reference for build datasets under `data/raw/`. Documents structure only — never values (HR-3).
>
> Only **fraudTrain.csv** has been inspected in this draft. **fraudTest.csv has not been opened** at Daniel's instruction (HR-4 hygiene — keeping a clean separation between the slice we explore and any potential held-out set).

---

## Source: `data/raw/sparkov/fraudTrain.csv`

Kaggle mirror `kartik2112/fraud-detection`, derived from the Sparkov synthetic generator. Used per CLAUDE.md as **feature-engineering practice** (readable column names, ~0.5% fraud, time-ranged 2019-2020).

The data is **synthetic** — no real cardholders, no real cards. We still treat the PII-shaped columns as PII for habit alignment with HR-3: never log, print, or commit row-level values.

### Summary

| Metric | Value |
|---|---|
| Row count | **1,296,675** |
| Fraud count (`is_fraud == 1`) | **7,506** |
| Fraud rate | **0.5789%** |
| Time span | **2019-01-01 00:00:18 → 2020-06-21 12:13:37** (538 days) |
| Avg transactions / day | ~2,410 |
| Avg fraud transactions / day | ~14 |
| Columns | 23 (incl. a pandas-exported row-index column) |
| Nulls | none (all 23 columns 100% non-null on all 1,296,675 rows) |

### Columns

Type column shows the narrowest type that fits the observed sample. `nunique` is exact up to 100,000; columns above the cap are marked `>100k`. PII flag follows the spirit of HR-3 (mask in logs / derived outputs).

| # | Column | Type | nunique | PII | Role | Notes |
|---|---|---|---|---|---|---|
| 0 | `_row_index` | int | >100k | — | artefact | Unnamed first column in CSV; pandas row index from the original export. **Drop on load.** |
| 1 | `trans_date_trans_time` | datetime `YYYY-MM-DD HH:MM:SS` | >100k | — | time | Authoritative event timestamp. Use this for the time-based split (HR-4). |
| 2 | `cc_num` | int (synthetic) | 983 | yes | identifier | One row per cardholder/card pairing. 983 distinct cards generate all 1.3M transactions. In production this is a `card_token`, never raw PAN (HR-3). |
| 3 | `merchant` | string | 693 | — | transaction | Merchant name. Mid-cardinality — target/frequency encoding candidate. |
| 4 | `category` | string | 14 | — | transaction | Merchant category. Low cardinality — safe to one-hot. |
| 5 | `amt` | float | 52,928 | — | transaction | Transaction amount. Heavy-tailed in fraud data — expect log-transform / robust scaling. |
| 6 | `first` | string | 352 | yes | cardholder | First name. Mask. |
| 7 | `last` | string | 481 | yes | cardholder | Last name. Mask. |
| 8 | `gender` | string | 2 | yes | cardholder | `M` / `F` as encoded. Treat as protected attribute when auditing fairness. |
| 9 | `street` | string | 983 | yes | cardholder | Cardholder street address. 1:1 with `cc_num`. Mask. |
| 10 | `city` | string | 894 | yes | cardholder | Cardholder city. |
| 11 | `state` | string | 51 | yes | cardholder | US states + DC (51 codes). |
| 12 | `zip` | int | 970 | yes | cardholder | Cardholder ZIP code. |
| 13 | `lat` | float | 968 | yes | cardholder | Cardholder home latitude. ~1:1 with cardholder. |
| 14 | `long` | float | 969 | yes | cardholder | Cardholder home longitude. ~1:1 with cardholder. |
| 15 | `city_pop` | int | 879 | — | cardholder | Population of cardholder city. |
| 16 | `job` | string | 494 | yes | cardholder | Occupational title. |
| 17 | `dob` | date `YYYY-MM-DD` | 968 | yes | cardholder | Date of birth. 1:1-ish with cardholder (a few shared birthdays among 983 cards). Mask; derive `age` if needed. |
| 18 | `trans_num` | string | >100k | — | identifier | Per-transaction unique id. Drop before training; keep for joins. |
| 19 | `unix_time` | int | >100k | — | time | Redundant with `trans_date_trans_time`. Use one or the other consistently. |
| 20 | `merch_lat` | float | >100k | — | transaction | Merchant latitude **at time of transaction**. High cardinality = Sparkov adds per-transaction jitter (not constant per merchant). See observations. |
| 21 | `merch_long` | float | >100k | — | transaction | Merchant longitude at time of transaction. Same jitter behavior. |
| 22 | `is_fraud` | bool (0/1) | 2 | — | **target** | Label. Never use in feature derivation (HR-4 leakage). |

---

## Observations worth carrying into modeling

1. **Cardholder cardinality.** 983 distinct cards across 1.3M transactions ≈ 1,320 transactions/card on average over 538 days. Strong basis for per-card velocity / behavioral features (`txns_last_hour`, `amt_zscore_per_card`, `distance_from_home`).
2. **Merchant geo is jittered per transaction, not constant per merchant.** `merchant` has 693 unique values but `merch_lat` / `merch_long` exceed 100k unique. This means `merch_lat`/`merch_long` are **transaction-time** signals, not merchant attributes. Useful as-is for distance-from-home features; not a substitute for a merchant location lookup.
3. **`cc_num` (983), `street` (983), and `dob` (~968) are all near-1:1 with the cardholder.** They carry identity, not signal. Use them to build per-card aggregates; do not feed raw to the model.
4. **Zero nulls.** Convenient, but unrealistic for production data. Do not let pipelines assume non-null inputs.
5. **`_row_index` is a CSV artefact** (pandas-style index from the source export). Drop on load — do not let it leak in as a "feature" (it correlates with time and would be label-adjacent).
6. **Fraud rate 0.58%** confirms the CONTEXT.md figure. Accuracy is meaningless at this base rate (CONTEXT.md forbidden terms) — design evals around recall@FPR or PR-AUC (HR-4 / EDD).
7. **Time span 538 days** gives room for a time-based train/validation/test cut. Whatever cut Daniel chooses, this file alone supplies enough span — no need to touch `fraudTest.csv` to define it.

---

## Provenance

- **Inspected:** `data/raw/sparkov/fraudTrain.csv` (351 MB, 1,296,675 rows).
- **NOT inspected:** `data/raw/sparkov/fraudTest.csv`. Per Daniel's instruction and HR-4 hygiene, this file was not opened.
- **Method:** stdlib `csv` streaming pass — see `scripts/inspect_sparkov_train.py`. Single read, no row values retained beyond the first 500 per column for type inference.
- **Environment:** Python 3.14.3 (Windows `py` launcher). No pandas / numpy install; project package manager (`uv` per CLAUDE.md) not yet adopted.
- **What this draft does NOT cover:** IEEE-CIS schema (separate dataset, separate dictionary), label leakage audit, feature derivation rules, train/val/test cut definition.
