"""Integrity checks on the c01 gold typology set (model-free).

These assert the gold is well-formed BEFORE any model runs, so a typo'd slug or
a renamed case file fails loudly here rather than silently scoring every model
as a miss. Pure filesystem + label-set checks — no transformers import.
"""
from __future__ import annotations

from pathlib import Path

from vigil.classify.labels import load_labels
from vigil.generation.case_loader import load_case_body

from .c01_gold_typologies import GOLD_TYPOLOGIES


REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = REPO_ROOT / "corpus" / "cases"
TYPOLOGIES_DIR = REPO_ROOT / "corpus" / "typologies"


def test_gold_has_ten_cases():
    assert len(GOLD_TYPOLOGIES) == 10


def test_gold_case_files_are_unique():
    files = [gold.case_file for gold in GOLD_TYPOLOGIES]
    assert len(set(files)) == len(files)


def test_every_gold_typology_is_a_valid_label():
    labels = set(load_labels(TYPOLOGIES_DIR))
    for gold in GOLD_TYPOLOGIES:
        assert gold.typology in labels, f"{gold.case_file}: {gold.typology!r} not a label"


def test_every_gold_case_file_exists_and_loads_disposition_stripped():
    # Also exercises the HR-4 anti-leak guard on all 10 real cases: each must
    # carry a `## Disposition` header so load_case_body strips the gold answer.
    for gold in GOLD_TYPOLOGIES:
        body = load_case_body(CASES_DIR / gold.case_file)
        assert "## Disposition" not in body
        assert body.strip(), f"{gold.case_file}: empty body after strip"
