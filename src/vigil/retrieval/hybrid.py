"""Hybrid search via Reciprocal Rank Fusion (RRF).

RRF combines independently-ranked lists without needing score normalization:
each chunk's fused score is the sum of 1 / (k_rrf + rank) across the input
strategies, with k_rrf=60 by convention (Cormack, Clarke, Buettcher 2009).

This fits ADR-002's lexical + semantic corpus mix: BM25 nails reason-code IDs
("Visa 10.4", "4837"), dense nails typology paraphrases ("many small charges
across many cards"), and RRF rewards a chunk that ranks well in either.
"""

from __future__ import annotations

from collections import defaultdict

from vigil.corpus.chunker import Chunk
from vigil.retrieval.hits import ChunkHit


def _chunk_key(chunk: Chunk) -> tuple[str, str]:
    return (chunk.source_path, chunk.section_title)


def hybrid_rrf(
    rankings: list[list[ChunkHit]],
    k: int,
    k_rrf: int = 60,
) -> list[ChunkHit]:
    fused_scores: dict[tuple[str, str], float] = defaultdict(float)
    seen_chunks: dict[tuple[str, str], Chunk] = {}

    for hits in rankings:
        for hit in hits:
            key = _chunk_key(hit.chunk)
            fused_scores[key] += 1.0 / (k_rrf + hit.rank)
            seen_chunks.setdefault(key, hit.chunk)

    ranked_keys = sorted(fused_scores, key=lambda k_: fused_scores[k_], reverse=True)[:k]
    return [
        ChunkHit(chunk=seen_chunks[key], score=fused_scores[key], rank=rank)
        for rank, key in enumerate(ranked_keys, start=1)
    ]
