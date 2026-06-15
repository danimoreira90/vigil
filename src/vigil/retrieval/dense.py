"""Dense (cosine) search against a Chroma collection.

Embed the query with the same model that built the collection (asymmetric
encoder would break cosine comparability), then ask Chroma for top-k. The
returned ChunkHit list preserves Chroma's ranking 1..k.
"""

from __future__ import annotations

from chromadb.api.models.Collection import Collection

from vigil.corpus.chunker import Chunk
from vigil.retrieval.embed import encode_texts
from vigil.retrieval.hits import ChunkHit


def dense_search(
    query: str,
    collection: Collection,
    model_name: str,
    k: int,
) -> list[ChunkHit]:
    query_embedding = encode_texts(model_name, [query])[0]
    result = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
    )

    metadatas = result["metadatas"][0]
    documents = result["documents"][0]
    distances = result["distances"][0]

    hits: list[ChunkHit] = []
    for rank, (meta, text, distance) in enumerate(
        zip(metadatas, documents, distances), start=1
    ):
        chunk = Chunk(
            text=text,
            source_path=meta["source_path"],
            family=meta["family"],
            doc_title=meta["doc_title"],
            section_title=meta["section_title"],
        )
        # Chroma returns cosine DISTANCE (1 - cosine_similarity) when the
        # collection is created with hnsw:space="cosine". Convert to
        # similarity so the score is comparable across strategies in the
        # hit/miss analysis.
        hits.append(ChunkHit(chunk=chunk, score=1.0 - distance, rank=rank))
    return hits
