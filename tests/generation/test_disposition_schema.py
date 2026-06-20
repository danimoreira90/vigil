"""Schema validation tests for the System 2 Disposition contract.

Spec: corpus/policies/case-disposition-guidelines.md
Enum strings: byte-exact match against corpus (allow/block/review-continue, low/medium/high).
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from vigil.generation.schema import Confidence, Disposition, Recommendation


def test_allow_with_one_source_and_no_reason_codes_is_valid():
    disposition = Disposition(
        recommendation=Recommendation.ALLOW,
        confidence=Confidence.MEDIUM,
        reason_codes=[],
        cited_sources=["policies/case-disposition-guidelines.md"],
        rationale="Profile and signals consistent with a normal high-value purchase.",
    )
    assert disposition.recommendation is Recommendation.ALLOW
    assert disposition.reason_codes == []


def test_block_with_reason_codes_and_sources_is_valid():
    disposition = Disposition(
        recommendation=Recommendation.BLOCK,
        confidence=Confidence.HIGH,
        reason_codes=["velocity_high", "bin_diversity_high"],
        cited_sources=["typologies/card-testing.md"],
        rationale="Card-testing typology fit with two strong reason codes.",
    )
    assert disposition.recommendation is Recommendation.BLOCK
    assert "velocity_high" in disposition.reason_codes


def test_review_continue_is_a_valid_recommendation():
    disposition = Disposition(
        recommendation=Recommendation.REVIEW_CONTINUE,
        confidence=Confidence.LOW,
        reason_codes=[],
        cited_sources=["policies/case-disposition-guidelines.md"],
        rationale="Evidence suggestive but a legitimate explanation is not ruled out.",
    )
    assert disposition.recommendation.value == "review-continue"


def test_block_with_empty_reason_codes_is_rejected():
    with pytest.raises(ValidationError) as excinfo:
        Disposition(
            recommendation=Recommendation.BLOCK,
            confidence=Confidence.HIGH,
            reason_codes=[],
            cited_sources=["typologies/card-testing.md"],
            rationale="Looks like card testing.",
        )
    assert "reason_code" in str(excinfo.value).lower()


def test_missing_cited_sources_is_rejected():
    with pytest.raises(ValidationError):
        Disposition(
            recommendation=Recommendation.ALLOW,
            confidence=Confidence.MEDIUM,
            reason_codes=[],
            cited_sources=[],
            rationale="No citations provided.",
        )


def test_empty_rationale_is_rejected():
    with pytest.raises(ValidationError):
        Disposition(
            recommendation=Recommendation.ALLOW,
            confidence=Confidence.MEDIUM,
            reason_codes=[],
            cited_sources=["policies/case-disposition-guidelines.md"],
            rationale="",
        )


def test_decline_is_not_a_valid_recommendation():
    # CONTEXT.md: "decline" is forbidden; "block" is the Vigil term.
    with pytest.raises(ValidationError):
        Disposition(
            recommendation="decline",  # type: ignore[arg-type]
            confidence=Confidence.HIGH,
            reason_codes=["velocity_high"],
            cited_sources=["typologies/card-testing.md"],
            rationale="Block this charge.",
        )


def test_unknown_confidence_label_is_rejected():
    with pytest.raises(ValidationError):
        Disposition(
            recommendation=Recommendation.ALLOW,
            confidence="very high",  # type: ignore[arg-type]
            reason_codes=[],
            cited_sources=["policies/case-disposition-guidelines.md"],
            rationale="Confident clean.",
        )


def test_enum_strings_match_corpus_byte_exact():
    """Guard against any future rename — the corpus is authoritative."""
    assert [r.value for r in Recommendation] == ["allow", "block", "review-continue"]
    assert [c.value for c in Confidence] == ["low", "medium", "high"]
