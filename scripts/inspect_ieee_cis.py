"""One-off inspector for data/raw/ieee-cis/{train_transaction,train_identity}.csv.

Reports row count, column count, isFraud rate, TransactionDT span, null density
by column family (V/C/D/M/card/addr/id), and memory footprint after a LEFT join.

HR-3: prints only structural facts and aggregate nulls, never row values.
HR-4: does NOT touch test_transaction.csv / test_identity.csv (no labels there anyway).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/ieee-cis")
TRANSACTION_PATH = RAW / "train_transaction.csv"
IDENTITY_PATH = RAW / "train_identity.csv"

FAMILIES: dict[str, re.Pattern[str]] = {
    "card": re.compile(r"^card\d+$"),
    "addr": re.compile(r"^addr\d+$"),
    "dist": re.compile(r"^dist\d+$"),
    "C": re.compile(r"^C\d+$"),
    "D": re.compile(r"^D\d+$"),
    "M": re.compile(r"^M\d+$"),
    "V": re.compile(r"^V\d+$"),
    "id_": re.compile(r"^id_\d+$"),
    "email": re.compile(r"^[PR]_emaildomain$"),
    "device": re.compile(r"^Device(Type|Info)$"),
}


def family_of(column: str) -> str:
    for name, pattern in FAMILIES.items():
        if pattern.match(column):
            return name
    return "core"


def main() -> int:
    if not TRANSACTION_PATH.exists() or not IDENTITY_PATH.exists():
        print(f"MISSING: {TRANSACTION_PATH} or {IDENTITY_PATH}", file=sys.stderr)
        return 1

    transactions = pd.read_csv(TRANSACTION_PATH)
    identity = pd.read_csv(IDENTITY_PATH)

    joined = transactions.merge(identity, how="left", on="TransactionID")

    n_rows = len(joined)
    n_cols = joined.shape[1]
    n_fraud = int(joined["isFraud"].sum())
    fraud_rate = n_fraud / n_rows
    dt_min = int(joined["TransactionDT"].min())
    dt_max = int(joined["TransactionDT"].max())
    dt_span_seconds = dt_max - dt_min
    dt_span_days = dt_span_seconds / 86400.0

    identity_match = int(joined["id_01"].notna().sum())
    identity_match_rate = identity_match / n_rows

    tx_mem_mb = transactions.memory_usage(deep=True).sum() / 1024**2
    id_mem_mb = identity.memory_usage(deep=True).sum() / 1024**2
    joined_mem_mb = joined.memory_usage(deep=True).sum() / 1024**2

    print(f"TX_ROWS|{len(transactions)}")
    print(f"TX_COLS|{transactions.shape[1]}")
    print(f"ID_ROWS|{len(identity)}")
    print(f"ID_COLS|{identity.shape[1]}")
    print(f"JOINED_ROWS|{n_rows}")
    print(f"JOINED_COLS|{n_cols}")
    print(f"FRAUD_COUNT|{n_fraud}")
    print(f"FRAUD_RATE|{fraud_rate:.6f}")
    print(f"TXN_DT_MIN|{dt_min}")
    print(f"TXN_DT_MAX|{dt_max}")
    print(f"TXN_DT_SPAN_SECONDS|{dt_span_seconds}")
    print(f"TXN_DT_SPAN_DAYS|{dt_span_days:.4f}")
    print(f"IDENTITY_MATCH_COUNT|{identity_match}")
    print(f"IDENTITY_MATCH_RATE|{identity_match_rate:.6f}")
    print(f"MEM_TRANSACTION_MB|{tx_mem_mb:.2f}")
    print(f"MEM_IDENTITY_MB|{id_mem_mb:.2f}")
    print(f"MEM_JOINED_MB|{joined_mem_mb:.2f}")

    print("--FAMILY_TOTALS--")
    family_columns: dict[str, list[str]] = {}
    for column in joined.columns:
        family_columns.setdefault(family_of(column), []).append(column)
    for family, cols in family_columns.items():
        nulls = joined[cols].isna().sum().sum()
        cells = n_rows * len(cols)
        null_rate = nulls / cells if cells else 0.0
        print(f"{family}|cols={len(cols)}|null_rate={null_rate:.6f}")

    print("--CARD_FAMILY_DETAIL--")
    for column in [c for c in joined.columns if c.startswith("card") or c.startswith("addr")]:
        nulls = int(joined[column].isna().sum())
        null_rate = nulls / n_rows
        print(f"{column}|null_rate={null_rate:.6f}|dtype={joined[column].dtype}")

    print("--TIME_QUANTILES--")
    for label, q in [("p20", 0.20), ("p35", 0.35), ("p50", 0.50), ("p65", 0.65), ("p80", 0.80)]:
        value = int(joined["TransactionDT"].quantile(q))
        offset_days = (value - dt_min) / 86400.0
        print(f"{label}|TransactionDT={value}|offset_days={offset_days:.4f}")

    print("--SPLIT_PROPOSAL--")
    cutoff_train_val = int(joined["TransactionDT"].quantile(0.65))
    cutoff_val_test = int(joined["TransactionDT"].quantile(0.80))
    train_mask = joined["TransactionDT"] < cutoff_train_val
    val_mask = (joined["TransactionDT"] >= cutoff_train_val) & (joined["TransactionDT"] < cutoff_val_test)
    test_mask = joined["TransactionDT"] >= cutoff_val_test
    for name, mask in [("train", train_mask), ("validation", val_mask), ("test_sacred", test_mask)]:
        slice_ = joined.loc[mask]
        count = len(slice_)
        fraud = int(slice_["isFraud"].sum())
        share = count / n_rows
        dt_lo = int(slice_["TransactionDT"].min())
        dt_hi = int(slice_["TransactionDT"].max())
        span = (dt_hi - dt_lo) / 86400.0
        print(
            f"{name}|rows={count}|share={share:.6f}|fraud={fraud}"
            f"|fraud_rate={fraud / count:.6f}|dt_min={dt_lo}|dt_max={dt_hi}|span_days={span:.4f}"
        )
    print(f"CUTOFF_TRAIN_VAL|{cutoff_train_val}")
    print(f"CUTOFF_VAL_TEST|{cutoff_val_test}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
