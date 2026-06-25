"""Tests for the 13-label set (12 fraud typologies + 1 legitimate).

The 12 fraud slugs are derived at runtime from corpus/typologies/ filenames
(single source of truth — CS-5). The 13th label, LEGITIMATE, is added in code,
not derived: a triage classifier that cannot say "this is clean" is broken
(case-high-value-allowed-3ds is a confirmed-legit allow). These tests pin the
count, the membership, and the slug->phrase transform the encoder hypothesis
depends on.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from vigil.classify.labels import (
    LEGITIMATE,
    load_labels,
    load_typology_slugs,
    slug_to_phrase,
)


TYPOLOGIES_DIR = Path(__file__).resolve().parents[2] / "corpus" / "typologies"

# The 12 fraud typologies, derived independently of the code under test so a
# silent drift in either the corpus or the loader is caught here.
EXPECTED_TYPOLOGY_SLUGS = (
    "account-takeover",
    "bin-attack",
    "card-testing",
    "clean-fraud",
    "friendly-fraud",
    "merchant-collusion",
    "phishing-driven-fraud",
    "promo-abuse",
    "refund-fraud",
    "synthetic-identity-fraud",
    "triangulation-fraud",
    "velocity-attack",
)


def test_typology_slugs_match_the_corpus_filenames():
    assert load_typology_slugs(TYPOLOGIES_DIR) == EXPECTED_TYPOLOGY_SLUGS


def test_load_typology_slugs_raises_on_empty_dir(tmp_path):
    # CS-6: an empty typology dir is a broken corpus, not a silent empty set.
    with pytest.raises(ValueError):
        load_typology_slugs(tmp_path)


def test_load_labels_is_thirteen_typologies_plus_legitimate():
    labels = load_labels(TYPOLOGIES_DIR)
    assert len(labels) == 13
    assert labels[:12] == EXPECTED_TYPOLOGY_SLUGS
    assert labels[12] == LEGITIMATE
    assert LEGITIMATE == "legitimate"


def test_legitimate_is_not_one_of_the_corpus_slugs():
    # The 13th label has no typology file on purpose — guard against someone
    # later adding a legitimate.md and double-counting it.
    assert LEGITIMATE not in load_typology_slugs(TYPOLOGIES_DIR)


def test_slug_to_phrase_replaces_hyphens_with_spaces():
    assert slug_to_phrase("card-testing") == "card testing"
    assert slug_to_phrase("synthetic-identity-fraud") == "synthetic identity fraud"
    assert slug_to_phrase("legitimate") == "legitimate"
