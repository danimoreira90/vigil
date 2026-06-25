"""c05 knowledge-only retrieval boundary — keeps gold dispositions out of the index.

The c03 loader walks ALL of corpus/, INCLUDING corpus/cases/. Case files carry a
`## Disposition` section, which the chunker emits as its own retrievable chunk.
Embedded into the c03 index, a query case could retrieve its OWN gold answer.

The fix is additive and leaves c03 untouched: c05 filters case chunks out at this
boundary and builds a SEPARATE Chroma collection under KNOWLEDGE_INDEX_DIR. The
c03 loader, the c03 retrieval-quality eval, and the c03 minilm/bge-small index
dirs are never mutated.

The guarantee is belt-and-suspenders:
  1. generation.case_loader.load_case_body strips `## Disposition` on the QUERY side; and
  2. this knowledge index contains no case documents at all on the RETRIEVAL side.
"""

from __future__ import annotations

from pathlib import Path

from chromadb.api.models.Collection import Collection

from vigil.corpus.chunker import Chunk
from vigil.corpus.loader import load_chunks
from vigil.retrieval.index import INDEX_ROOT, build_chroma

# The shipped retriever is MiniLM hybrid (chosen on the c03 run; ADR-002 addendum).
KNOWLEDGE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Separate from the c03 dirs (data/index/minilm, data/index/bge-small) by design.
KNOWLEDGE_INDEX_DIR = INDEX_ROOT / "minilm_knowledge"
# corpus/cases/ holds synthetic eval cases (with gold dispositions), not knowledge.
CASES_PREFIX = "cases/"


def knowledge_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Drop case chunks so no gold disposition can ever be retrieved (HR-4)."""
    return [c for c in chunks if not c.source_path.startswith(CASES_PREFIX)]


def build_knowledge_index(corpus_root: Path, persist_dir: Path) -> Collection:
    """The c05 seam: load the corpus, exclude cases, embed the rest.

    Points at the knowledge-only index, never the c03 full index.
    """
    chunks = knowledge_chunks(load_chunks(corpus_root))
    return build_chroma(chunks, KNOWLEDGE_MODEL, persist_dir)
