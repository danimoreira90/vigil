"""One-off inspector for data/raw/sparkov/fraudTrain.csv.

Reports row count, fraud rate, time span, and column type inference.
Stdlib only — no pandas/numpy install. Streams the file in one pass.

HR-3: prints only structural facts, never raw row values.
HR-4: does not touch fraudTest.csv.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

PATH = Path("data/raw/sparkov/fraudTrain.csv")
UNIQUE_CAP = 100_000  # stop tracking exact uniques past this; mark high-cardinality


def classify(values: list[str]) -> str:
    """Pick the narrowest type that fits every non-empty sample value."""
    non_empty = [v for v in values if v != ""]
    if not non_empty:
        return "empty"

    def all_match(pred) -> bool:
        try:
            return all(pred(v) for v in non_empty)
        except (ValueError, TypeError):
            return False

    if all_match(lambda v: v in ("0", "1")):
        return "bool(0/1)"
    if all_match(lambda v: int(v) or True):
        return "int"
    if all_match(lambda v: float(v) or True):
        return "float"
    # Sparkov timestamp format: 2019-01-01 00:00:18
    if all_match(lambda v: len(v) == 19 and v[4] == "-" and v[10] == " "):
        return "datetime(YYYY-MM-DD HH:MM:SS)"
    # Sparkov dob format: 1988-03-09
    if all_match(lambda v: len(v) == 10 and v[4] == "-" and v[7] == "-"):
        return "date(YYYY-MM-DD)"
    return "string"


def main() -> int:
    if not PATH.exists():
        print(f"MISSING: {PATH}", file=sys.stderr)
        return 1

    row_count = 0
    fraud_count = 0
    time_min: str | None = None
    time_max: str | None = None

    columns: list[str] = []
    non_null: dict[str, int] = {}
    uniques: dict[str, set[str]] = {}
    overflow: dict[str, bool] = {}
    samples: dict[str, list[str]] = {}  # first 500 non-empty for type inference

    with PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        # First column has empty header (pandas-style row index export); name it.
        columns = ["_row_index" if h == "" else h for h in header]
        for c in columns:
            non_null[c] = 0
            uniques[c] = set()
            overflow[c] = False
            samples[c] = []

        ts_idx = columns.index("trans_date_trans_time")
        fraud_idx = columns.index("is_fraud")

        for row in reader:
            row_count += 1
            for c, v in zip(columns, row):
                if v != "":
                    non_null[c] += 1
                    if not overflow[c]:
                        uniques[c].add(v)
                        if len(uniques[c]) > UNIQUE_CAP:
                            overflow[c] = True
                            uniques[c] = set()  # release memory
                    if len(samples[c]) < 500:
                        samples[c].append(v)

            ts = row[ts_idx]
            if ts:
                if time_min is None or ts < time_min:
                    time_min = ts
                if time_max is None or ts > time_max:
                    time_max = ts

            if row[fraud_idx] == "1":
                fraud_count += 1

    fraud_rate = fraud_count / row_count if row_count else 0.0

    print(f"ROW_COUNT|{row_count}")
    print(f"FRAUD_COUNT|{fraud_count}")
    print(f"FRAUD_RATE|{fraud_rate:.6f}")
    print(f"TIME_MIN|{time_min}")
    print(f"TIME_MAX|{time_max}")
    print("--COLUMNS--")
    for c in columns:
        if overflow[c]:
            nu = f">{UNIQUE_CAP}"
        else:
            nu = str(len(uniques[c]))
        print(f"{c}|{classify(samples[c])}|non_null={non_null[c]}|nunique={nu}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
