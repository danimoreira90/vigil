"""Tests for the IEEE-CIS time-based split (data/ieee-cis-foundation).

Spec: docs/specs/ieee-cis-foundation.md §5.
Verifies the three invariants:
  1. train < validation < held-out by TransactionDT (no row overlap in time)
  2. TransactionID sets are pairwise disjoint across splits
  3. load_for_training() refuses any data/test/ path — ADR-001 LEAK-1
"""
from __future__ import annotations

import pandas as pd
import pytest

from vigil.data.split import (
    SACRED_PATH,
    TIME_COLUMN,
    TIE_BREAK_COLUMN,
    TRAIN_PATH,
    VALIDATION_PATH,
    load_for_training,
    write_splits,
)


@pytest.fixture(scope="session", autouse=True)
def _ensure_splits_exist() -> None:
    if not (TRAIN_PATH.exists() and VALIDATION_PATH.exists() and SACRED_PATH.exists()):
        write_splits()


def test_split_is_time_ordered() -> None:
    train_dt = pd.read_parquet(TRAIN_PATH, columns=[TIME_COLUMN])[TIME_COLUMN]
    validation_dt = pd.read_parquet(VALIDATION_PATH, columns=[TIME_COLUMN])[TIME_COLUMN]
    held_out_dt = pd.read_parquet(SACRED_PATH, columns=[TIME_COLUMN])[TIME_COLUMN]

    assert train_dt.max() < validation_dt.min(), (
        "train must end strictly before validation begins"
    )
    assert validation_dt.max() < held_out_dt.min(), (
        "validation must end strictly before held-out begins"
    )


def test_no_transaction_id_overlap() -> None:
    train_ids = set(pd.read_parquet(TRAIN_PATH, columns=[TIE_BREAK_COLUMN])[TIE_BREAK_COLUMN])
    validation_ids = set(
        pd.read_parquet(VALIDATION_PATH, columns=[TIE_BREAK_COLUMN])[TIE_BREAK_COLUMN]
    )
    held_out_ids = set(pd.read_parquet(SACRED_PATH, columns=[TIE_BREAK_COLUMN])[TIE_BREAK_COLUMN])

    assert not (train_ids & validation_ids), "train and validation share TransactionID"
    assert not (train_ids & held_out_ids), "train and held-out share TransactionID"
    assert not (validation_ids & held_out_ids), "validation and held-out share TransactionID"


def test_train_path_cannot_load_sacred() -> None:
    with pytest.raises(PermissionError, match="LEAK-1"):
        load_for_training(SACRED_PATH)
