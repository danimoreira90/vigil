"""Embed text with a local sentence-transformers model (HR-3).

Pure function. Model instances cache at module level (CS-10) so repeated calls
in a notebook re-use the loaded weights without rebuilding a class wrapper.
Embeddings are L2-normalized so cosine similarity equals the dot product —
this is what Chroma compares against when the collection is created with
metadata={"hnsw:space": "cosine"}.
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

_MODELS: dict[str, SentenceTransformer] = {}


def _get_model(model_name: str) -> SentenceTransformer:
    if model_name not in _MODELS:
        _MODELS[model_name] = SentenceTransformer(model_name)
    return _MODELS[model_name]


def encode_texts(model_name: str, texts: list[str]) -> np.ndarray:
    model = _get_model(model_name)
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return np.asarray(embeddings, dtype=np.float32)
