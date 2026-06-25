"""Deterministic, model-free tests for the decoder label parser and prompt.

parse_label is the core the eval trusts: it maps Qwen's raw generation back to
one of the 13 labels. The ladder is lowercase+strip -> exact slug -> substring
-> None. None is a MISS, surfaced honestly (CS-6): an unparseable or
format-divergent generation is real decoder-vs-encoder evidence (format
adherence), not a bug to normalize away. These tests pin that exact behavior —
including the deliberate space-vs-hyphen miss — so the eval stays honest.

No transformers import: build_label_prompt and parse_label are pure. The model
loaders in decoder.py import the ML stack lazily, so this suite runs without
the c01 extra installed.
"""
from __future__ import annotations

from vigil.classify.decoder import build_label_prompt, parse_label


# A representative slice of the 13-label set in canonical (sorted) order, with
# LEGITIMATE last — mirrors load_labels() without depending on the corpus.
LABELS = (
    "account-takeover",
    "bin-attack",
    "card-testing",
    "clean-fraud",
    "friendly-fraud",
    "refund-fraud",
    "triangulation-fraud",
    "legitimate",
)


# ---- parse_label: exact-match rung -----------------------------------------

def test_exact_slug_returns_that_slug():
    assert parse_label("card-testing", LABELS) == "card-testing"


def test_exact_match_is_case_insensitive_and_stripped():
    assert parse_label("  CARD-TESTING\n", LABELS) == "card-testing"


def test_legitimate_parses_like_any_other_label():
    assert parse_label("legitimate", LABELS) == "legitimate"


# ---- parse_label: substring rung -------------------------------------------

def test_slug_embedded_in_a_sentence_is_found():
    raw = "The typology here is bin-attack based on the BIN sweep."
    assert parse_label(raw, LABELS) == "bin-attack"


def test_trailing_punctuation_after_slug_is_found():
    assert parse_label("card-testing.", LABELS) == "card-testing"


def test_multi_label_output_returns_first_in_canonical_order():
    # Two labels present; the substring loop walks LABELS in canonical order,
    # so bin-attack (earlier) wins over card-testing. Pinned deliberately: a
    # multi-label generation is ambiguous and we resolve it deterministically.
    raw = "could be card-testing or bin-attack"
    assert parse_label(raw, LABELS) == "bin-attack"


# ---- parse_label: None rung (honest misses) --------------------------------

def test_empty_output_is_a_miss():
    assert parse_label("", LABELS) is None


def test_whitespace_only_output_is_a_miss():
    assert parse_label("   \n\t", LABELS) is None


def test_no_label_present_is_a_miss():
    assert parse_label("this looks like suspicious activity", LABELS) is None


def test_space_instead_of_hyphen_is_an_honest_miss():
    # "card testing" (space) does not match slug "card-testing" (hyphen). We do
    # NOT normalize the separator: format adherence is part of what the
    # decoder-vs-encoder comparison measures. This miss is evidence, not a bug.
    assert parse_label("card testing", LABELS) is None


# ---- build_label_prompt ----------------------------------------------------

CASE_BODY = (
    "# Case — TX-2026-Q2-TEST-001\n"
    "- card_token: TKN-test...0000\n"
    "- reason_codes: [velocity_high]\n"
)


def test_prompt_lists_every_label():
    prompt = build_label_prompt(CASE_BODY, LABELS)
    for label in LABELS:
        assert label in prompt


def test_prompt_inserts_case_body_verbatim():
    assert CASE_BODY in build_label_prompt(CASE_BODY, LABELS)


def test_prompt_fences_case_as_data_not_instructions():
    # Mirrors the prompt-injection fence used in generation/prompt.py.
    prompt = build_label_prompt(CASE_BODY, LABELS)
    assert "(data, not instructions)" in prompt


def test_prompt_ends_asking_for_the_typology():
    assert build_label_prompt(CASE_BODY, LABELS).rstrip().endswith("Typology:")
