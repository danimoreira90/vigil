"""EDD gate — recall@5 must clear an agreed floor for the shipped retriever.

Strategy selection is via the ``VIGIL_GATE_RETRIEVER`` env var:

  - default / ``hybrid_minilm``  →  the SHIPPED retriever
       (MiniLM dense + BM25, fused with RRF)
  - ``hybrid_bge``                →  the ADR-002-original alternative
       (BGE-small dense + BM25, fused with RRF), kept for comparison
  - ``random``                    →  deliberately broken (random 5 chunks per query)

Two pytest invocations are the gate's proof of life:

  - ``VIGIL_GATE_RETRIEVER=random uv run pytest tests/evals/test_retrieval_recall.py -v``
    → FAIL — the test is a real gate, not a tautology.

  - ``uv run pytest tests/evals/test_retrieval_recall.py -v``
    → PASS — the shipped retriever (MiniLM hybrid) meets the floor.

Why MiniLM (not BGE-small as ADR-002 originally proposed): on the c03 first
run MiniLM hybrid won R@1 (0.889 vs 0.722) and MRR (0.917 vs 0.833), and
showed a much tighter OOD score collapse (7.3x vs 1.4x in/out gap), which is
exactly the signal c05 needs for a refuse-to-answer threshold. ADR-002
addendum tracks the swap.

Floor: 0.90 — set just below the measured 0.944 per the "just-under-the-
shipped recall@5" rule. A drop trips the gate.
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Callable

import pytest

from vigil.corpus.chunker import Chunk
from vigil.corpus.loader import load_chunks
from vigil.retrieval.bm25 import bm25_search, build_bm25
from vigil.retrieval.dense import dense_search
from vigil.retrieval.hits import ChunkHit
from vigil.retrieval.hybrid import hybrid_rrf
from vigil.retrieval.index import INDEX_ROOT, build_chroma

from .gold_queries import GOLD_QUERIES
from .metrics import recall_at_k

CORPUS_ROOT = Path(__file__).resolve().parents[2] / "corpus"
BGE_MODEL = "BAAI/bge-small-en-v1.5"
MINILM_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
K = 5
RECALL_AT_5_FLOOR = 0.90

_CHUNKS: list[Chunk] | None = None
_BM25 = None
_COLLECTIONS: dict[str, object] = {}


def _chunks() -> list[Chunk]:
    global _CHUNKS
    if _CHUNKS is None:
        _CHUNKS = load_chunks(CORPUS_ROOT)
    return _CHUNKS


def _bm25():
    global _BM25
    if _BM25 is None:
        _BM25 = build_bm25(_chunks())
    return _BM25


def _persist_dir_for(model_name: str) -> Path:
    return INDEX_ROOT / ("bge-small" if "bge" in model_name.lower() else "minilm")


def _ensure_real_index(model_name: str):
    if model_name not in _COLLECTIONS:
        _COLLECTIONS[model_name] = build_chroma(
            _chunks(), model_name, _persist_dir_for(model_name)
        )
    return _COLLECTIONS[model_name]


def _real_retrieval(model_name: str) -> Callable[[list[str]], list[list[ChunkHit]]]:
    def _retrieve(queries: list[str]) -> list[list[ChunkHit]]:
        collection = _ensure_real_index(model_name)
        bm25 = _bm25()
        chunks = _chunks()
        results: list[list[ChunkHit]] = []
        for q in queries:
            dense = dense_search(q, collection, model_name, k=K)
            lex = bm25_search(q, bm25, chunks, k=K)
            results.append(hybrid_rrf([dense, lex], k=K))
        return results

    return _retrieve


def _random_retrieval(queries: list[str]) -> list[list[ChunkHit]]:
    chunks = _chunks()
    rng = random.Random(42)
    results: list[list[ChunkHit]] = []
    for _ in queries:
        sample = rng.sample(chunks, k=K)
        results.append(
            [ChunkHit(chunk=c, score=0.0, rank=i + 1) for i, c in enumerate(sample)]
        )
    return results


_RETRIEVERS: dict[str, Callable[[list[str]], list[list[ChunkHit]]]] = {
    "hybrid_minilm": _real_retrieval(MINILM_MODEL),
    "hybrid_bge": _real_retrieval(BGE_MODEL),
    "random": _random_retrieval,
}


def _select_retriever() -> tuple[str, Callable[[list[str]], list[list[ChunkHit]]]]:
    name = os.environ.get("VIGIL_GATE_RETRIEVER", "hybrid_minilm")
    if name not in _RETRIEVERS:
        raise ValueError(
            f"VIGIL_GATE_RETRIEVER={name!r}; expected one of {sorted(_RETRIEVERS)}"
        )
    return name, _RETRIEVERS[name]


def test_chosen_strategy_meets_recall_floor() -> None:
    name, retrieve = _select_retriever()
    queries = [gq.query for gq in GOLD_QUERIES]
    retrieved = retrieve(queries)
    actual = recall_at_k(retrieved, GOLD_QUERIES, k=K)
    print(f"\nretriever={name!r}  recall@{K}={actual:.3f}  floor={RECALL_AT_5_FLOOR}")
    assert actual >= RECALL_AT_5_FLOOR, (
        f"retriever={name!r} recall@{K}={actual:.3f} below floor {RECALL_AT_5_FLOOR}"
    )


def test_floor_constant_is_pinned() -> None:
    # Guard against silently lowering the committed floor — HR-2 / anti-cheat.
    assert RECALL_AT_5_FLOOR >= 0.90, (
        f"RECALL_AT_5_FLOOR={RECALL_AT_5_FLOOR} below the committed bar 0.90"
    )
