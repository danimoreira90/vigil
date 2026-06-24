"""Load a synthetic Case body for eval, with the disposition stripped.

HR-4 anti-leak guard. The eval pipeline must never let the gold disposition
reach the prompt or the recommendation_match score is theater. load_case_body
splits each case markdown file on the `## Disposition` header and returns
ONLY the part above it. If the header is missing, the function raises —
silent return of the full file would leak the gold answer into the prompt
without anyone noticing (CS-6 — fail loudly).
"""
from __future__ import annotations

from pathlib import Path

DISPOSITION_HEADER = "## Disposition"


class MissingDispositionHeader(ValueError):
    """A case file did not contain the `## Disposition` boundary marker."""


def load_case_body(path: Path | str) -> str:
    path = Path(path)
    return split_case_body(path.read_text(encoding="utf-8"), source=str(path))


def split_case_body(raw: str, *, source: str = "<string>") -> str:
    if DISPOSITION_HEADER not in raw:
        raise MissingDispositionHeader(
            f"{source}: missing `{DISPOSITION_HEADER}` header — refusing to "
            "return the full file (would leak the gold disposition into the prompt)."
        )
    return raw.split(DISPOSITION_HEADER, 1)[0].rstrip() + "\n"
