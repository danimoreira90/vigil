"""Regression: the c04 probe prompt contains a JSON example with literal { }
braces. str.format() reads those as field placeholders and raises KeyError.
build_prompt() must use a substitution that ignores other braces, and the
returned string must keep the JSON schema example intact for the LLM to read.

If this test starts to fail, do NOT switch back to str.format — fix the
substitution. The probe prompt is the comparison anchor across engines;
mangling its braces would silently change what we're measuring.
"""
from __future__ import annotations

from vigil.generation.probe import PROBE_PROMPT_TEMPLATE, build_prompt


CASE_BODY = (
    "# Case — TX-2026-Q2-018734\n"
    "- card_token: TKN-d4a1...e9c2\n"
    "- reason_codes: [velocity_high]\n"
)


def test_build_prompt_does_not_raise_on_literal_json_braces():
    # The template embeds an example like { "recommendation": ... } verbatim;
    # str.format would treat those as fields. Must not raise.
    prompt = build_prompt(CASE_BODY)
    assert isinstance(prompt, str) and len(prompt) > len(CASE_BODY)


def test_build_prompt_contains_the_case_body():
    prompt = build_prompt(CASE_BODY)
    assert CASE_BODY in prompt


def test_build_prompt_preserves_literal_json_schema_braces():
    # The four field names from the schema example must survive substitution,
    # along with their surrounding quoted literals — that's the format
    # instruction the LLM relies on.
    prompt = build_prompt(CASE_BODY)
    assert '"recommendation":' in prompt
    assert '"confidence":' in prompt
    assert '"reason_codes":' in prompt
    assert '"cited_sources":' in prompt
    assert '"rationale":' in prompt
    # And the enclosing braces of the example must still be there.
    assert "{" in prompt and "}" in prompt


def test_build_prompt_substitutes_only_the_case_body_slot():
    # The template has exactly one substitution slot: {case_body}.
    # After substitution it must NOT contain that literal placeholder.
    prompt = build_prompt(CASE_BODY)
    assert "{case_body}" not in prompt


def test_template_constant_exposes_the_single_slot():
    # Guard the template against drift: must still contain exactly the slot
    # build_prompt expects.
    assert "{case_body}" in PROBE_PROMPT_TEMPLATE
