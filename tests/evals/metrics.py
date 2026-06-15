"""Retrieval metrics — recall@k and MRR over the gold query set.

Pure functions over a per-query list of retrieved chunks. The metric is
known-item style: for each gold query, the relevant set is the subset of
corpus chunks that match the query's targets (see ``is_hit``). A query is a
"hit at k" if any of its top-k retrieved chunks is in the relevant set.

These are the only metrics gated in the EDD test. The notebook also reports
per-strategy MRR for ranking quality, but the ship gate is recall@5.
"""

from __future__ import annotations

from collections.abc import Sequence

from vigil.retrieval.hits import ChunkHit

from .gold_queries import GoldQuery, is_hit


def first_hit_rank(hits: Sequence[ChunkHit], gold: GoldQuery) -> int | None:
    for hit in hits:
        if is_hit(hit.chunk.source_path, hit.chunk.section_title, gold):
            return hit.rank
    return None


def recall_at_k(
    retrieved_per_query: Sequence[Sequence[ChunkHit]],
    gold_queries: Sequence[GoldQuery],
    k: int,
) -> float:
    if len(retrieved_per_query) != len(gold_queries):
        raise ValueError(
            f"retrieved/gold length mismatch: {len(retrieved_per_query)} vs {len(gold_queries)}"
        )
    hits = 0
    for hits_for_query, gold in zip(retrieved_per_query, gold_queries):
        top_k = list(hits_for_query)[:k]
        if first_hit_rank(top_k, gold) is not None:
            hits += 1
    return hits / len(gold_queries)


def mean_reciprocal_rank(
    retrieved_per_query: Sequence[Sequence[ChunkHit]],
    gold_queries: Sequence[GoldQuery],
    k_max: int,
) -> float:
    if len(retrieved_per_query) != len(gold_queries):
        raise ValueError(
            f"retrieved/gold length mismatch: {len(retrieved_per_query)} vs {len(gold_queries)}"
        )
    total = 0.0
    for hits_for_query, gold in zip(retrieved_per_query, gold_queries):
        top = list(hits_for_query)[:k_max]
        rank = first_hit_rank(top, gold)
        if rank is not None:
            total += 1.0 / rank
    return total / len(gold_queries)
