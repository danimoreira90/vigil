"""Tests for the case-body loader (HR-4 anti-leak guard).

Every eval that grades recommendation_match depends on the gold disposition
NEVER reaching the prompt. load_case_body strips the `## Disposition`
section. If the header is missing, the function raises — silent return of
the full file would leak the gold answer into the prompt and turn the
recommendation_match score into theater.
"""
from __future__ import annotations

import pytest

from vigil.generation.case_loader import (
    DISPOSITION_HEADER,
    MissingDispositionHeader,
    load_case_body,
    split_case_body,
)


def test_split_strips_everything_from_the_disposition_header_onward():
    raw = (
        "# Case — TX-X\n"
        "- card_token: TKN-x\n"
        "## Disposition\n"
        "- recommendation: block\n"
        "- rationale: card-testing burst\n"
    )
    body = split_case_body(raw)
    assert "TKN-x" in body
    assert DISPOSITION_HEADER not in body
    assert "recommendation: block" not in body
    assert "card-testing burst" not in body


def test_split_raises_when_disposition_header_absent():
    # The anti-leak guard: silent return of the full file would feed the
    # gold answer into the prompt and make recommendation_match theater.
    raw = "# Case — TX-X\n- card_token: TKN-x\n"
    with pytest.raises(MissingDispositionHeader):
        split_case_body(raw, source="phantom-case.md")


def test_split_error_message_names_the_source():
    raw = "no disposition here"
    with pytest.raises(MissingDispositionHeader) as excinfo:
        split_case_body(raw, source="bad-case.md")
    assert "bad-case.md" in str(excinfo.value)


def test_load_case_body_reads_and_splits_a_file(tmp_path):
    case = tmp_path / "case.md"
    case.write_text(
        "# Case — TX-X\n- foo: bar\n## Disposition\n- recommendation: allow\n",
        encoding="utf-8",
    )
    body = load_case_body(case)
    assert "- foo: bar" in body
    assert DISPOSITION_HEADER not in body
    assert "recommendation: allow" not in body


def test_load_case_body_raises_when_real_file_missing_header(tmp_path):
    case = tmp_path / "no_disposition.md"
    case.write_text("# Case — TX-X\n- foo: bar\n", encoding="utf-8")
    with pytest.raises(MissingDispositionHeader) as excinfo:
        load_case_body(case)
    assert "no_disposition.md" in str(excinfo.value)
