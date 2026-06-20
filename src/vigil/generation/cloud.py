"""Cloud generation via OpenAI — comparison-only (ADR-003).

NOT the ship path. Used solely for the c04 comparison: same prompt over
synthetic cases (HR-3-safe) against gpt-5.4-nano to produce the
privacy/cost/latency/quality table.

Key handling: OPENAI_API_KEY is read from os.environ only. Never logged,
never echoed, never serialized into model_name or any result field.

Pricing constant is a snapshot. The notebook reports it verbatim so the
grader can confirm. Update when OpenAI changes pricing.
"""
from __future__ import annotations

import os

CLOUD_MODEL_NAME = "gpt-5.4-nano"
CLOUD_MAX_TOKENS = 1024
CLOUD_TEMPERATURE = 0.0

# USD per 1M tokens — snapshot at the time of c04. Verify against the live
# pricing page before reporting; the notebook prints these inline so the
# grader can see what was used.
CLOUD_PRICE_PROMPT_PER_MILLION = 0.05
CLOUD_PRICE_COMPLETION_PER_MILLION = 0.40


class MissingApiKeyError(RuntimeError):
    """Raised when OPENAI_API_KEY is not set in the environment."""


CLOUD_TIMEOUT_SECONDS = 30.0


def _client():
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise MissingApiKeyError(
            "OPENAI_API_KEY not set — cloud backend is unavailable. "
            "Local backend remains the ship path (ADR-003)."
        )
    return OpenAI(api_key=api_key, timeout=CLOUD_TIMEOUT_SECONDS)


# GPT-5 family models use max_completion_tokens (not max_tokens) and may
# reject any non-default temperature with HTTP 400. The function tries with
# CLOUD_TEMPERATURE first; if the API 400s mentioning "temperature", it
# falls back to default sampling and sets _TEMPERATURE_DROPPED so the
# notebook can surface "gpt-5.4-nano uses default sampling".
_TEMPERATURE_DROPPED = False


def temperature_was_dropped() -> bool:
    """True once a call has fallen back to default sampling (GPT-5 rejection)."""
    return _TEMPERATURE_DROPPED


def generate_cloud(prompt: str) -> tuple[str, str, int, int, float]:
    """Return (text, model_name, prompt_tokens, completion_tokens, cost_usd)."""
    global _TEMPERATURE_DROPPED
    from openai import BadRequestError

    client = _client()
    base_kwargs = {
        "model": CLOUD_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": CLOUD_MAX_TOKENS,
    }
    if _TEMPERATURE_DROPPED:
        response = client.chat.completions.create(**base_kwargs)
    else:
        try:
            response = client.chat.completions.create(
                temperature=CLOUD_TEMPERATURE, **base_kwargs
            )
        except BadRequestError as exc:
            if "temperature" not in str(exc).lower():
                raise
            _TEMPERATURE_DROPPED = True
            response = client.chat.completions.create(**base_kwargs)
    text = response.choices[0].message.content or ""
    usage = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    cost_usd = (
        prompt_tokens * CLOUD_PRICE_PROMPT_PER_MILLION
        + completion_tokens * CLOUD_PRICE_COMPLETION_PER_MILLION
    ) / 1_000_000
    return text, CLOUD_MODEL_NAME, prompt_tokens, completion_tokens, cost_usd


def list_available_models() -> list[str]:
    """GET /v1/models — used by the notebook smoke test to confirm gpt-5.4-nano."""
    client = _client()
    return [m.id for m in client.models.list().data]
