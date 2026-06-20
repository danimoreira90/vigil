"""JSON extract/repair tests.

The local LLM (GPT4All Llama-3.1-8B-Instruct) is known to wrap its JSON in
markdown fences, prepend prose, or emit trailing commas. extract_json and
repair_json are the deterministic recovery layer before pydantic validation.

If both fail, raise InvalidDispositionError — never silently default (CS-6).
"""
from __future__ import annotations

import pytest

from vigil.generation.json_repair import (
    InvalidDispositionError,
    extract_json,
    repair_json,
)


def test_clean_json_object_parses():
    text = '{"recommendation": "allow", "confidence": "medium"}'
    parsed = extract_json(text)
    assert parsed == {"recommendation": "allow", "confidence": "medium"}


def test_json_wrapped_in_markdown_fence_is_extracted():
    text = "Sure! Here is the JSON:\n```json\n{\"recommendation\": \"block\"}\n```\n"
    parsed = extract_json(text)
    assert parsed == {"recommendation": "block"}


def test_json_wrapped_in_bare_fence_is_extracted():
    text = "```\n{\"recommendation\": \"block\"}\n```"
    parsed = extract_json(text)
    assert parsed == {"recommendation": "block"}


def test_json_preceded_by_prose_is_extracted():
    text = (
        "Based on the case, my analysis follows. "
        '{"recommendation": "review-continue", "confidence": "low"} '
        "End of disposition."
    )
    parsed = extract_json(text)
    assert parsed == {"recommendation": "review-continue", "confidence": "low"}


def test_repair_fixes_trailing_comma():
    text = '{"recommendation": "block", "confidence": "high",}'
    parsed = repair_json(text)
    assert parsed == {"recommendation": "block", "confidence": "high"}


def test_repair_fixes_trailing_comma_in_list():
    text = '{"reason_codes": ["velocity_high", "bin_diversity_high",]}'
    parsed = repair_json(text)
    assert parsed == {"reason_codes": ["velocity_high", "bin_diversity_high"]}


def test_irrecoverable_garbage_raises():
    text = "I cannot produce JSON, sorry."
    with pytest.raises(InvalidDispositionError):
        extract_json(text)


def test_repair_of_irrecoverable_garbage_raises():
    text = "no json here at all"
    with pytest.raises(InvalidDispositionError):
        repair_json(text)


def test_extract_finds_first_balanced_object_not_a_fragment():
    text = 'noise { unbalanced {"recommendation": "block"} more noise'
    parsed = extract_json(text)
    assert parsed == {"recommendation": "block"}


def test_empty_input_raises():
    with pytest.raises(InvalidDispositionError):
        extract_json("")
