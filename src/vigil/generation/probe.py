"""The c04 benchmark probe prompt.

Scope: this prompt exists ONLY to hold the prompt constant across engines
so the c04 local-vs-cloud comparison measures the engine, not the prompt.
The real disposition prompt — with few-shot examples, chain-of-thought,
and meta-prompt iteration — is c02's deliverable.

build_prompt uses str.replace, NOT str.format. The template embeds a JSON
schema example (literal { } and "field": tokens); str.format would read
the JSON braces as field placeholders and raise KeyError. The regression
guard lives in tests/generation/test_probe.py.
"""
from __future__ import annotations

PROBE_PROMPT_TEMPLATE = """You are a fraud-case analyst. Read the Case below and produce a Disposition.

Return ONLY a JSON object with these fields, no prose, no markdown:
{
  "recommendation": one of "allow" | "block" | "review-continue",
  "confidence":    one of "low" | "medium" | "high",
  "reason_codes":  list of short snake_case strings (required when recommendation is "block"),
  "cited_sources": non-empty list of corpus paths you relied on (e.g. "typologies/card-testing.md"),
  "rationale":     one short paragraph explaining the recommendation
}

--- CASE ---
{case_body}
--- END CASE ---"""


def build_prompt(case_body: str) -> str:
    return PROBE_PROMPT_TEMPLATE.replace("{case_body}", case_body)
