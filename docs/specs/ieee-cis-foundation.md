# Spec: IEEE-CIS Foundation — leakage-safe time-based split

**Status:** Draft v0.1 (pending Daniel approval before STEP 2 implementation)
**Date:** 2026-06-11
**Branch:** `data/ieee-cis-foundation`
**Role:** `data/*`
**Owner:** Daniel
**Authors:** Claude (agent), reporting per HR-1

> This spec produces the **honest split** that the rest of the modeling work depends on.
> No modeling, no features, no thresholds in scope here — only: load → join → time-order → write three Parquet artifacts.

---

## 1 — Objective

Establish a reproducible, leakage-safe, **time-based** train / validation / held-out split of the IEEE-CIS competition `train_*` files, written as Parquet under `data/processed/` (train + validation) and `data/test/` (sacred held-out — HR-4).

The split MUST satisfy:
1. Ordering by `TransactionDT` (ascending). No random shuffling, ever (HR-4, CONTEXT.md "Time-Based Split").
2. No `TransactionID` overlap across slices.
3. The sacred held-out slice is the **latest** time window — fraud tactics shift, so the latest data is the closest stand-in for "future production traffic."
4. Code paths that train or tune cannot import or read from `data/test/` (enforced by tests in STEP 2).

What this spec does NOT do: select features, define metrics, propose thresholds, touch `test_transaction.csv` / `test_identity.csv` (those are the Kaggle competition test set — unlabeled, irrelevant for honest evaluation).

---

## 2 — Inventory (measured 2026-06-11)

All numbers from `scripts/inspect_ieee_cis.py` against `data/raw/ieee-cis/train_*.csv`.

### 2.1 Source files

| File | Rows | Cols | Notes |
|---|---:|---:|---|
| `train_transaction.csv` | 590,540 | 394 | Labeled (`isFraud`). Authoritative time column: `TransactionDT`. |
| `train_identity.csv` | 144,233 | 41 | Subset of TransactionIDs. LEFT-joined; absent rows are normal. |

### 2.2 After LEFT join on `TransactionID`

| Metric | Value |
|---|---|
| Joined rows | **590,540** (= transaction count; left-join is non-multiplying) |
| Joined columns | **434** (394 + 41 − 1 join key) |
| Fraud count (`isFraud == 1`) | **20,663** |
| Fraud rate | **3.499%** |
| Identity-row match rate | **24.42%** (144,233 / 590,540) |
| `TransactionDT` min | **86,400 s** (= day 1 exactly; reference is day 0) |
| `TransactionDT` max | **15,811,131 s** |
| Time span | **182.00 days** (≈ 6 months) |
| In-memory footprint (joined, deep) | **2,514 MB** |

Avg ~3,245 transactions/day, ~114 fraud/day. Matches the CLAUDE.md "build data" facts (~590k tx, ~3.5% fraud, 431 features — column count differs by 3 because IEEE-CIS adds three columns over the figure cited).

### 2.3 Null density by column family

Families inferred by regex on column name. Null rate = nulls across the family / (rows × family size).

| Family | Pattern | Cols | Null rate |
|---|---|---:|---:|
| `core` | `TransactionID`, `isFraud`, `TransactionDT`, `TransactionAmt`, `ProductCD` | 5 | **0.0000** |
| `card` | `card1…card6` | 6 | 0.0051 |
| `addr` | `addr1`, `addr2` | 2 | 0.1113 |
| `dist` | `dist1`, `dist2` | 2 | 0.7664 |
| `email` | `P_emaildomain`, `R_emaildomain` | 2 | 0.4637 |
| `C` | `C1…C14` | 14 | **0.0000** |
| `D` | `D1…D15` | 15 | **0.5815** |
| `M` | `M1…M9` | 9 | 0.4992 |
| `V` | `V1…V339` | 339 | 0.4304 |
| `id_` | `id_01…id_38` | 38 | **0.8482** (consistent with 24% identity-row match) |
| `device` | `DeviceType`, `DeviceInfo` | 2 | 0.7803 |

`card` and `addr` detail:

```
card1  null=0.0000  int64
card2  null=0.0151  float64
card3  null=0.0027  float64
card4  null=0.0027  str
card5  null=0.0072  float64
card6  null=0.0027  str
addr1  null=0.1113  float64
addr2  null=0.1113  float64
```

### 2.4 Memory note

The joined frame is ~2.5 GB resident in pandas. The splitter must not hold three copies simultaneously. STEP 2 implementation strategy: read once → sort by `TransactionDT` → slice via boolean masks → write each slice to Parquet → drop reference before the next slice. We do NOT need streaming; one full load + write fits in 8 GB RAM with margin.

---

## 3 — Split proposal

### 3.1 Sizes & cutoffs

Time-based, contiguous, non-overlapping. **No random shuffle.** Cutoffs are exact quantiles of `TransactionDT`.

| Slice | Share | Quantile range | Cutoff (TransactionDT seconds) | Rows | Fraud | Fraud rate | Calendar days |
|---|---:|---|---:|---:|---:|---:|---:|
| **train** | 65% | `[0, 0.65)` | `< 9,614,666` | 383,851 | 13,126 | 3.420% | day 1 → day 111 (span 110.28) |
| **validation** | 15% | `[0.65, 0.80)` | `9,614,666 ≤ DT < 12,192,853` | 88,581 | 3,473 | 3.921% | day 112 → day 142 (span 29.84) |
| **test_sacred** | 20% | `[0.80, 1.0]` | `≥ 12,192,853` | 118,108 | 4,064 | 3.441% | day 142 → day 183 (span 41.88) |

Rows sum to 590,540 ✓. The contiguous time intervals are disjoint by construction.

### 3.2 Why these sizes

- **20% sacred held-out** matches the user-supplied target ("last ~20% by time → `data/test/`").
- **15% validation** matches the user-supplied target ("next-last ~15% → `data/processed/`").
- Train gets the remaining 65% — the **earliest** time window. This is the correct direction in fraud: we train on the past, validate on the recent past, evaluate on the most-recent slice (the closest analog to future production traffic).
- Validation gets ~30 days, held-out gets ~42 days. Both windows are long enough to absorb intra-week and intra-month seasonality (weekday/weekend, payday cycles).

### 3.3 Fraud-rate observation

Validation's fraud rate (3.92%) is slightly elevated vs train (3.42%) and held-out (3.44%). Two readings, neither blocking:
1. **Real concept drift** within these 6 months — fraud rate is non-stationary, which is exactly why we split by time.
2. **Coincidence on a 30-day window** — small enough to be sampling noise.

We do NOT adjust the split to flatten this. Flattening would require either random shuffling (HR-4 violation) or stratified time sampling (which secretly mixes time into the rule and is dishonest). Live model deployment will face exactly this kind of drift; the eval set should reflect it.

### 3.4 Storage layout

```
data/processed/
  train.parquet          # 65% earliest
  validation.parquet     # next 15%
data/test/
  test.parquet           # latest 20% — SACRED, HR-4
```

Parquet via pyarrow. CSV stays in `data/raw/` untouched. The CSV → Parquet conversion is one-way and reproducible from the script.

> **pyarrow note (CS-13):** pyarrow is dev tooling for our data layer, not a runtime / latency-path dep. Per the project's relaxed-deps wording in `CLAUDE.md`, no ADR required — only Daniel's diff review when added to `pyproject.toml`'s `dev` group.

### 3.5 Reproducibility

The splitter is deterministic — no RNG, no seed. Two runs from the same `data/raw/ieee-cis/train_*.csv` produce byte-identical Parquet (modulo Parquet timestamp metadata; we'll pin the engine/version in pyproject).

---

## 4 — Leakage risks (acknowledged and mitigated)

The split is one thing; honest training is another. These risks live downstream but must be flagged now so the splitter does the right thing.

| # | Risk | Status under this split | Carry into modeling |
|---|---|---|---|
| **L1** | **`TransactionID` is monotonically increasing in time.** It encodes the time-order it should not leak. | Confirmed by inspection (min/max line up with min/max `TransactionDT`). | Drop or hash `TransactionID` before feature derivation. Never feed it as a numeric feature. |
| **L2** | **`D` columns are time-delta features.** Community-documented as days-since-something (last-card-use, last-address, etc.). | Within a single transaction row they reach backwards; **per-row they are not look-ahead**. But aggregating them globally on the full dataset would leak future signal. | Compute any per-card / per-merchant aggregate **on training data only**, then apply (lookup, not recompute) on val / test. Enforced by code, not by hope. |
| **L3** | **`isFraud` is the target.** Any feature derived using `isFraud` directly is leakage. | Out of scope here (no features yet). | Lint rule for modeling work: no `isFraud` reference outside the training fit loop. |
| **L4** | **Identity columns (`id_*`) are NOT in the training set for 75.6% of rows.** A model that "uses" identity columns mostly trains on their absence. | The LEFT join already encodes this honestly (NaN where absent). | Handle NaN intentionally per family — no blanket `fillna(0)` (CS-6). Missingness IS the signal. |
| **L5** | **Concept drift within the 6-month span.** Fraud-rate non-stationarity (see §3.3) means metrics on a non-time split would be optimistic. | Resolved by the time-based split itself — drift is *measured*, not hidden. | Plan a drift-monitoring step in `infra/*` before any live deploy. |
| **L6** | **The Kaggle competition `test_transaction.csv` exists at `data/raw/ieee-cis/test_*.csv`.** It has no labels; it is irrelevant to our evaluation; touching it would only confuse the boundary. | Ignored. The loader reads `train_*` only. | If a future task wants the Kaggle test set for submission practice, that's a separate spec — not this one. |
| **L7** | **A duplicate copy of the raw Kaggle files currently sits at `data/test/`** (`test_transaction.csv`, `train_transaction.csv`, etc., dated 2019-12-11). This is leftover scaffolding from the download step, NOT the sacred held-out yet. | Surface and flag: this folder must be **cleared before STEP 2 writes `data/test/test.parquet`**. Doing it ourselves silently is risky (HR-4: that folder is sacred-by-policy). | Daniel: confirm deletion (or pre-move) of those 6 CSV files before STEP 2. The spec keeps STEP 2 from writing into a folder that already has unexplained content. |

Open question: **L7 is the only blocker** for STEP 2. Two clean resolutions, both Daniel's call:

> **Option A** — Daniel deletes `data/test/*.csv` (+ `.zip`) manually. STEP 2 writes a clean `data/test/test.parquet` into an empty sacred folder.
>
> **Option B** — STEP 2 writes the sacred slice to a sibling path (e.g. `data/test/processed/test.parquet`) leaving the raw dump untouched, and we revisit the path layout later.

Recommendation: **Option A.** `data/test/` should be exactly one thing (the sacred slice). Side-storing raw Kaggle CSVs there blurs HR-4. But this is Daniel's to decide.

---

## 5 — Definition of done for STEP 2 (preview, not in scope here)

When Daniel approves this spec, STEP 2 will:

1. RED — three failing tests:
   - `test_split_is_time_ordered`: every row in `train.parquet` has `TransactionDT` strictly less than every row in `validation.parquet`, which is strictly less than every row in `test.parquet`.
   - `test_no_transaction_id_overlap`: pairwise empty intersection of `TransactionID` sets across the three slices.
   - `test_train_path_cannot_load_test`: the loader function used by training code refuses (raises) when called with the held-out path; only an explicit `evaluate_on_sacred_set()` entry point can read it.

2. GREEN — implement in `src/vigil/data/split.py` (loader + splitter, pure transforms per CS-9), write the three Parquet files, paste full pytest output.

3. Self-check against CODE-SIMPLICITY (CS-1..CS-13), report any rule applied.

4. Show `git status` + `git diff --cached`, propose a conventional-commit message, hand off to Daniel (HR-1).

Nothing about features, models, thresholds, or metrics is in scope until the foundation is in place.

---

## 6 — Files touched / produced

This spec (STEP 1):
- ✅ `scripts/inspect_ieee_cis.py` — new, one-off inspector (mirrors `inspect_sparkov_train.py`).
- ✅ `docs/specs/ieee-cis-foundation.md` — this file.

STEP 2 (after approval):
- New: `src/vigil/__init__.py`, `src/vigil/data/__init__.py`, `src/vigil/data/split.py`.
- New: `tests/test_split.py`.
- New: `data/processed/train.parquet`, `data/processed/validation.parquet`, `data/test/test.parquet` (data — not committed; covered by `.gitignore`).
- Modified: `pyproject.toml` (`pyarrow`, `pytest` to dev group — only if not already there).

---

## 7 — Open questions for Daniel

1. **L7 / §4 — `data/test/` cleanup**: Option A (Daniel clears it) or Option B (write to a sibling path)? Recommendation: A.
2. **Split sizes — 65 / 15 / 20**: lock these, or prefer rounder calendar-day cutoffs (e.g. train = first 4 months, val = month 5, test = month 6)?
3. **Sort stability**: rows with identical `TransactionDT` exist (a same-second batch will show up). Tie-break by `TransactionID` ascending is the proposed deterministic rule. Acceptable, or prefer `kind="mergesort"` on `TransactionDT` only (stable but not strictly deterministic across pandas versions)?

---

## Changelog

- **2026-06-11** — Initial draft. Inventory + split proposal + leakage flags. Awaiting Daniel.
