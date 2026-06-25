"""EDD leakage gate — the shipped c05 knowledge index contains NO case chunk.

This is anti-cheat for retrieval (HR-4). A single case disposition reachable
from the index makes recommendation_match theater. The recall eval proves the
knowledge index still retrieves; this proves it can never retrieve a gold answer.

Deterministic despite loading the embedding model: source_path metadata is
written verbatim by build_chroma, independent of the float embeddings. The index
is built into a tmp dir so the test never depends on or pollutes the shipped
data/index/minilm_knowledge/ artifact.
"""

from __future__ import annotations

from pathlib import Path

from vigil.retrieval.knowledge import CASES_PREFIX, build_knowledge_index

CORPUS_ROOT = Path(__file__).resolve().parents[2] / "corpus"


def test_knowledge_index_has_no_case_chunks(tmp_path: Path) -> None:
    collection = build_knowledge_index(CORPUS_ROOT, tmp_path / "minilm_knowledge")

    stored = collection.get(include=["metadatas"])
    leaked = [
        m["source_path"]
        for m in stored["metadatas"]
        if m["source_path"].startswith(CASES_PREFIX)
    ]

    assert collection.count() > 0, "knowledge index is empty — nothing was embedded"
    assert not leaked, (
        "case chunks reached the shipped knowledge index (gold-answer leak):\n  "
        + "\n  ".join(sorted(set(leaked)))
    )
