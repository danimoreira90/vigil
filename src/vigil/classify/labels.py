"""The 13 classification labels: 12 fraud typologies + 1 legitimate.

The 12 fraud slugs are derived at runtime from ``corpus/typologies/`` filenames
— one source of truth, so the label set cannot drift from the corpus (CS-5).
The 13th label, :data:`LEGITIMATE`, has no typology file and is added in code
on purpose: a triage classifier that cannot say "this is clean" is broken
(``case-high-value-allowed-3ds`` is a confirmed-legit allow). Treating it as a
first-class label lets the comparison measure abstention, a real Vigil
capability (rubric #5).

Pure functions over the filesystem (CS-9). An empty typology dir raises rather
than returning a silent empty set (CS-6).
"""
from __future__ import annotations

from pathlib import Path

LEGITIMATE = "legitimate"


def load_typology_slugs(typologies_dir: Path | str) -> tuple[str, ...]:
    slugs = tuple(sorted(path.stem for path in Path(typologies_dir).glob("*.md")))
    if not slugs:
        raise ValueError(f"no typology files found under {typologies_dir}")
    return slugs


def load_labels(typologies_dir: Path | str) -> tuple[str, ...]:
    return load_typology_slugs(typologies_dir) + (LEGITIMATE,)


def slug_to_phrase(slug: str) -> str:
    return slug.replace("-", " ")
