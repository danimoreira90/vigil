"""Parse raw LLM output into a validated Disposition (extract → repair → validate).

Extracted verbatim from tests/evals/run_c02_prompting.py (D2) so c02 and c05
share one parser. The three-stage recovery mirrors json_repair's contract:
try extract_json, fall back to repair_json, then hand the dict to the pydantic
Disposition validator. Returns (None, status) on any failure — never raises,
never silently defaults; the status string names the exact failure stage so the
eval row records why a generation did not yield a Disposition.
"""
from __future__ import annotations

from pydantic import ValidationError

from vigil.generation.json_repair import (
    InvalidDispositionError,
    extract_json,
    repair_json,
)
from vigil.generation.schema import Disposition


def parse_disposition(raw: str) -> tuple[Disposition | None, str]:
    try:
        parsed = extract_json(raw)
        status = "extract_ok"
    except InvalidDispositionError:
        try:
            parsed = repair_json(raw)
            status = "repair_ok"
        except InvalidDispositionError:
            return None, "invalid_json"
    try:
        return Disposition(**parsed), status
    except (ValidationError, TypeError, ValueError):
        return None, "schema_invalid"
