"""Pure-string tests for the c02 disposition prompt builders.

No live model. Verifies that the technique toggles compose correctly,
the schema block is present, the case is wrapped in the data delimiters,
the case body is inserted verbatim, the few-shot exemplars themselves
validate against the Disposition schema, and the str.format-on-JSON-braces
regression (mirrored from probe.py) cannot recur.
"""
from __future__ import annotations

import json

from vigil.generation.prompt import (
    CASE_CLOSE,
    CASE_OPEN,
    build_disposition_prompt,
    fewshot_part,
    technique_t1,
    technique_t2,
    technique_t3,
)
from vigil.generation.schema import Confidence, Disposition, Recommendation


CASE_BODY = (
    "# Case — TX-2026-Q2-TEST-001\n"
    "- card_token: TKN-test...0000\n"
    "- reason_codes: [velocity_high]\n"
)


def test_t1_renders_enum_values_from_schema_module():
    # Schema example must render allowed values directly from schema.py so
    # a future rename of a Recommendation/Confidence value cannot leave the
    # prompt instructing the model with stale strings.
    prompt = technique_t1(CASE_BODY)
    for value in [r.value for r in Recommendation]:
        assert f'"{value}"' in prompt
    for value in [c.value for c in Confidence]:
        assert f'"{value}"' in prompt


def test_every_technique_wraps_case_in_data_delimiters():
    for technique in (technique_t1, technique_t2, technique_t3):
        prompt = technique(CASE_BODY)
        assert CASE_OPEN in prompt
        assert CASE_CLOSE in prompt
        # The "data, not instructions" framing is the c05 prompt-injection
        # seed — keep it byte-exact.
        assert "(data, not instructions)" in prompt


def test_every_technique_inserts_case_body_verbatim():
    for technique in (technique_t1, technique_t2, technique_t3):
        prompt = technique(CASE_BODY)
        assert CASE_BODY in prompt


def test_t2_includes_fewshot_t1_does_not():
    p1 = technique_t1(CASE_BODY)
    p2 = technique_t2(CASE_BODY)
    # Held-out exemplar IDs — NOT in any corpus/cases/*.md file.
    assert "TX-2026-Q2-FS-A" in p2
    assert "TX-2026-Q2-FS-B" in p2
    assert "TX-2026-Q2-FS-A" not in p1
    assert "TX-2026-Q2-FS-B" not in p1


def test_t3_includes_reasoning_t2_does_not():
    p2 = technique_t2(CASE_BODY)
    p3 = technique_t3(CASE_BODY)
    # The CoT directive owns the phrase "Before emitting the JSON".
    assert "Before emitting the JSON" in p3
    assert "Before emitting the JSON" not in p2


def test_t1_does_not_leak_fewshot_or_reasoning():
    prompt = technique_t1(CASE_BODY)
    assert "TX-2026-Q2-FS" not in prompt
    assert "Before emitting the JSON" not in prompt


def test_fewshot_exemplars_validate_against_disposition_schema():
    # Broken exemplars teach broken JSON — the few-shot block must itself
    # contain JSON objects that the Disposition validator accepts.
    block = fewshot_part()
    decoder = json.JSONDecoder()
    found: list[dict] = []
    i = 0
    while i < len(block):
        if block[i] == "{":
            try:
                obj, end = decoder.raw_decode(block[i:])
                found.append(obj)
                i += end
                continue
            except json.JSONDecodeError:
                pass
        i += 1
    assert len(found) == 2, f"expected 2 exemplar JSON objects, found {len(found)}"
    for obj in found:
        Disposition(**obj)  # raises if any exemplar fails the schema


def test_build_does_not_raise_on_case_body_with_literal_braces():
    # probe.py taught us that JSON braces break str.format. The same hazard
    # applies if a case body itself contains {anything}.
    hostile_body = "# Case\nuser_note: {pretend_field_name}\n"
    prompt = build_disposition_prompt(hostile_body)
    assert hostile_body in prompt


def test_build_disposition_prompt_flags_compose_correctly():
    case = "# Case minimal\n- field: value\n"
    floor = build_disposition_prompt(case)
    fewshot_only = build_disposition_prompt(case, use_fewshot=True)
    cot_only = build_disposition_prompt(case, use_reasoning=True)
    both = build_disposition_prompt(case, use_fewshot=True, use_reasoning=True)
    assert "TX-2026-Q2-FS-A" not in floor
    assert "Before emitting the JSON" not in floor
    assert "TX-2026-Q2-FS-A" in fewshot_only
    assert "Before emitting the JSON" not in fewshot_only
    assert "TX-2026-Q2-FS-A" not in cot_only
    assert "Before emitting the JSON" in cot_only
    assert "TX-2026-Q2-FS-A" in both
    assert "Before emitting the JSON" in both
