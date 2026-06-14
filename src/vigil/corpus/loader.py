"""Corpus loader: walks corpus/ and produces chunks for c03 to embed.

Pure functions over the filesystem (CS-9). No caching, no config — the corpus
is small and re-reads are cheap. If reading or chunking a file fails, the
exception is raised with the file path (CS-6: fail loud, no swallowing).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .chunker import Chunk, chunk_document


def iter_corpus_files(corpus_root: Path) -> Iterable[Path]:
    yield from sorted(corpus_root.rglob("*.md"))


def load_chunks(corpus_root: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in iter_corpus_files(corpus_root):
        text = path.read_text(encoding="utf-8")
        chunks.extend(chunk_document(text, path, corpus_root))
    return chunks
