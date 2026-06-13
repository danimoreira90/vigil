"""Time-based train/validation/held-out split for IEEE-CIS.

See docs/specs/ieee-cis-foundation.md for inventory and cutoff derivation.
HR-4 / ADR-001 LEAK-1: data/test/test.parquet is sacred. Only
evaluate_on_sacred_set() may read it; load_for_training() refuses any
path under data/test/.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ieee-cis"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SACRED_DIR = PROJECT_ROOT / "data" / "test"

TRAIN_PATH = PROCESSED_DIR / "train.parquet"
VALIDATION_PATH = PROCESSED_DIR / "validation.parquet"
SACRED_PATH = SACRED_DIR / "test.parquet"

TIME_COLUMN = "TransactionDT"
TIE_BREAK_COLUMN = "TransactionID"
TRAIN_CUTOFF_SECONDS = 9_614_666
VALIDATION_CUTOFF_SECONDS = 12_192_853


def load_raw_ieee_cis() -> pd.DataFrame:
    """LEFT-join train_transaction with train_identity and sort by time + id."""
    transactions = pd.read_csv(RAW_DIR / "train_transaction.csv")
    identity = pd.read_csv(RAW_DIR / "train_identity.csv")
    joined = transactions.merge(identity, how="left", on=TIE_BREAK_COLUMN)
    return joined.sort_values(
        [TIME_COLUMN, TIE_BREAK_COLUMN], kind="mergesort"
    ).reset_index(drop=True)


def split_by_time(
    transactions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Slice an already-sorted frame into (train, validation, held_out)."""
    dt = transactions[TIME_COLUMN]
    train = transactions.loc[dt < TRAIN_CUTOFF_SECONDS]
    validation = transactions.loc[
        (dt >= TRAIN_CUTOFF_SECONDS) & (dt < VALIDATION_CUTOFF_SECONDS)
    ]
    held_out = transactions.loc[dt >= VALIDATION_CUTOFF_SECONDS]
    return train, validation, held_out


def write_splits() -> None:
    """Read raw, time-order, write the three Parquet artifacts."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    SACRED_DIR.mkdir(parents=True, exist_ok=True)
    transactions = load_raw_ieee_cis()
    train, validation, held_out = split_by_time(transactions)
    train.to_parquet(TRAIN_PATH, index=False)
    validation.to_parquet(VALIDATION_PATH, index=False)
    held_out.to_parquet(SACRED_PATH, index=False)


def load_for_training(path: Path) -> pd.DataFrame:
    """Read a Parquet slice for training or validation.

    Refuses any path under data/test/. This is the LEAK-1 fitness function
    from ADR-001: the training code path can never touch the sacred slice.
    """
    resolved = Path(path).resolve()
    sacred = SACRED_DIR.resolve()
    if resolved == sacred or sacred in resolved.parents:
        raise PermissionError(
            f"refusing to load {path}: data/test/ is the sacred held-out set "
            "(HR-4 / ADR-001 LEAK-1). Use evaluate_on_sacred_set() instead."
        )
    return pd.read_parquet(resolved)


def evaluate_on_sacred_set() -> pd.DataFrame:
    """Read the sacred held-out slice. The only sanctioned entry point (HR-4)."""
    return pd.read_parquet(SACRED_PATH)


if __name__ == "__main__":
    write_splits()
