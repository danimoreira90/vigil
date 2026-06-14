"""Corpus loader + chunker tests (HR-3, CS-9).

Three assertions, one per spec STEP-2 test requirement:
  1. The corpus produces at least one chunk.
  2. Every chunk carries the source metadata needed for c05 grounding citations.
  3. No PII pattern (raw PAN, CVV value, email) appears in any chunk.

The PII guard enforces HR-3 at the chunk boundary — the unit that c03 will embed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from vigil.corpus.loader import load_chunks


CORPUS_ROOT = Path(__file__).resolve().parents[1] / "corpus"


# HR-3 forbidden patterns. The PAN detector tolerates single space or hyphen
# separators between digits so a pasted "4111 1111 1111 1111" or
# "4111-1111-1111-1111" is caught alongside the unbroken form. The 13-19 digit
# bound is the standard PAN length range; dates and short identifiers stay below it.
PAN_PATTERN = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CVV_VALUE_PATTERN = re.compile(r"\b[Cc][Vv][Vv]2?\b\s*[:=]?\s*\d{3,4}\b")

PII_CATEGORIES = (
    ("PAN", PAN_PATTERN),
    ("email", EMAIL_PATTERN),
    ("CVV", CVV_VALUE_PATTERN),
)


@pytest.fixture(scope="module")
def chunks():
    return load_chunks(CORPUS_ROOT)


def test_corpus_produces_chunks(chunks):
    assert len(chunks) > 0, "expected at least one chunk from corpus/"


def test_every_chunk_carries_source_metadata(chunks):
    for chunk in chunks:
        assert chunk.source_path, f"empty source_path on chunk: {chunk}"
        assert chunk.family, f"empty family on chunk: {chunk.source_path}"
        assert chunk.doc_title, f"empty doc_title on chunk: {chunk.source_path}"
        assert chunk.section_title, f"empty section_title on chunk: {chunk.source_path}"


def test_no_pii_pattern_in_any_chunk(chunks):
    findings: list[str] = []
    for chunk in chunks:
        for label, pattern in PII_CATEGORIES:
            for match in pattern.finditer(chunk.text):
                findings.append(
                    f"{label} in {chunk.source_path} :: {chunk.section_title} :: {match.group()!r}"
                )
    assert not findings, "PII patterns found:\n  " + "\n  ".join(findings)
