"""Structure-aware chunker: one H2 section per chunk (spec §5).

Pure functions; no class hierarchy, no config object (CS-1, CS-5, CS-9, CS-10).
Each .md file in the corpus follows: one H1 (doc title) + N H2 sections (concepts).
A chunk = the literal text of one H2 section, from `## title` through the line
before the next H2 (or end of file). The H1 stays out of the chunk text and is
carried in metadata; c03 decides whether to prepend it before embedding.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


H1_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)
H2_PATTERN = re.compile(r"^## (.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    text: str
    source_path: str       # POSIX-style path relative to corpus root, e.g. "typologies/card-testing.md"
    family: str            # top-level folder, or doc stem for root-level files (e.g. "typologies", "glossary")
    doc_title: str         # H1 of the source document
    section_title: str     # H2 of the section this chunk represents


def chunk_document(text: str, source: Path, corpus_root: Path) -> list[Chunk]:
    relative = source.relative_to(corpus_root)
    relative_posix = relative.as_posix()
    parts = relative.parts
    family = parts[0] if len(parts) > 1 else source.stem

    h1_match = H1_PATTERN.search(text)
    if h1_match is None:
        raise ValueError(f"missing H1 in {relative_posix}")
    doc_title = h1_match.group(1).strip()

    h2_matches = list(H2_PATTERN.finditer(text))
    if not h2_matches:
        raise ValueError(f"no H2 sections in {relative_posix}")

    chunks: list[Chunk] = []
    for i, match in enumerate(h2_matches):
        start = match.start()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(text)
        section_title = match.group(1).strip()
        section_text = text[start:end].rstrip()
        chunks.append(Chunk(
            text=section_text,
            source_path=relative_posix,
            family=family,
            doc_title=doc_title,
            section_title=section_title,
        ))
    return chunks
