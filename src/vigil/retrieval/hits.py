"""ChunkHit — the universal retrieval-result type.

A single dataclass shared by dense / bm25 / hybrid. Carries the Chunk (with its
citation metadata for c05), the raw strategy-specific score (interpretation
depends on the strategy: cosine for dense, BM25 for lexical, RRF for hybrid),
and the rank (1-based) it landed at in the result list.
"""

from __future__ import annotations

from dataclasses import dataclass

from vigil.corpus.chunker import Chunk


@dataclass(frozen=True)
class ChunkHit:
    chunk: Chunk
    score: float
    rank: int
