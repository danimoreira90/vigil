"""Deterministic JSON recovery for LLM output, before pydantic validation.

Small local instruct models routinely wrap JSON in markdown fences, prepend
prose, or emit trailing commas. extract_json finds the first balanced JSON
object; repair_json then patches common syntactic damage. If both fail,
raise InvalidDispositionError — never silently default (CS-6).
"""
from __future__ import annotations

import json
import re


class InvalidDispositionError(ValueError):
    """Raised when LLM output cannot be coerced into a parseable JSON object."""


def extract_json(text: str) -> dict:
    """Find and parse the first balanced JSON object in `text`."""
    if not text or not text.strip():
        raise InvalidDispositionError("empty input")

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    candidate = _first_balanced_object(text)
    if candidate is None:
        raise InvalidDispositionError("no JSON object found in text")

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise InvalidDispositionError(f"failed to parse JSON object: {exc}") from exc


def repair_json(text: str) -> dict:
    """Extract, then patch common syntactic damage (trailing commas)."""
    candidate = (
        _first_balanced_object(text)
        or _first_brace_balanced_substring(text)
        or _strip_fence(text)
    )
    if candidate is None:
        raise InvalidDispositionError("no JSON object found in text")

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    patched = re.sub(r",(\s*[}\]])", r"\1", candidate)
    try:
        return json.loads(patched)
    except json.JSONDecodeError as exc:
        raise InvalidDispositionError(
            f"failed to repair JSON object: {exc}"
        ) from exc


def _first_balanced_object(text: str) -> str | None:
    """Return the first substring that parses as a JSON object.

    Scans each `{` left-to-right; at each candidate position, asks the JSON
    decoder to parse from there with raw_decode. The first success wins.
    This survives stray unbalanced braces in surrounding prose.
    """
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            _, end = decoder.raw_decode(text[i:])
        except json.JSONDecodeError:
            continue
        return text[i : i + end]
    return None


def _first_brace_balanced_substring(text: str) -> str | None:
    """Return the first substring spanning balanced { ... }, even if not valid JSON.

    Used by repair_json so the trailing-comma patch has a candidate to operate on
    when the substring isn't yet parseable. Brace counting respects string literals.
    """
    depth = 0
    start = -1
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    return text[start : i + 1]
    return None


def _strip_fence(text: str) -> str | None:
    match = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
    return match.group(1) if match else None
