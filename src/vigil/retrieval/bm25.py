"""BM25 lexical search.

Pure functions; the BM25Okapi instance is data, returned to the caller. No
class wrapper of our own (CS-10). A reason-code query like "Visa 10.4" or a
glossary lookup like "velocity_high" should retrieve its target chunk on
exact-token overlap — that's where BM25 dominates dense embeddings.

Tokenizer: lowercase + extract sequences of letters / digits / underscores.
Underscores are preserved so domain tokens like `velocity_high` stay intact
instead of splitting into `velocity` and `high`.
"""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from vigil.corpus.chunker import Chunk
from vigil.retrieval.hits import ChunkHit

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_PATTERN.findall(text)]


def build_bm25(chunks: list[Chunk]) -> BM25Okapi:
    tokenized = [tokenize(chunk.text) for chunk in chunks]
    return BM25Okapi(tokenized)


def bm25_search(
    query: str,
    bm25: BM25Okapi,
    chunks: list[Chunk],
    k: int,
) -> list[ChunkHit]:
    scores = bm25.get_scores(tokenize(query))
    # argsort descending; take top-k indices in order.
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [
        ChunkHit(chunk=chunks[idx], score=float(scores[idx]), rank=rank)
        for rank, idx in enumerate(top_indices, start=1)
    ]
