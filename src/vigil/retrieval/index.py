"""Persist and load Chroma collections for the fraud-knowledge corpus.

One collection per embedding model so we can compare them side by side without
re-embedding for every query. The persist directory is regenerable from
corpus/ at any time and is gitignored.

Pure functions; Chroma's PersistentClient is the only stateful object and it's
owned by the caller (notebook / test). No singleton, no DI container (CS-10).
"""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection

from vigil.corpus.chunker import Chunk
from vigil.retrieval.embed import encode_texts

INDEX_ROOT = Path("data/index")


def collection_name(model_name: str) -> str:
    return "corpus_" + model_name.replace("/", "_").replace("-", "_").replace(".", "_")


def build_chroma(
    chunks: list[Chunk],
    model_name: str,
    persist_dir: Path,
) -> Collection:
    """Embed every chunk and persist a fresh Chroma collection.

    Idempotent: if the collection already exists it is deleted and rebuilt.
    The notebook re-runs this cell often, so silent stale state would mask
    bugs (CS-6).
    """
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))
    name = collection_name(model_name)

    existing = {c.name for c in client.list_collections()}
    if name in existing:
        client.delete_collection(name)

    collection = client.create_collection(
        name=name,
        metadata={"hnsw:space": "cosine", "embedding_model": model_name},
    )

    texts = [chunk.text for chunk in chunks]
    embeddings = encode_texts(model_name, texts)

    collection.add(
        ids=[f"{i}" for i in range(len(chunks))],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "source_path": c.source_path,
                "family": c.family,
                "doc_title": c.doc_title,
                "section_title": c.section_title,
            }
            for c in chunks
        ],
    )
    return collection


def load_collection(persist_dir: Path, model_name: str) -> Collection:
    client = chromadb.PersistentClient(path=str(persist_dir))
    return client.get_collection(name=collection_name(model_name))
