"""c05 knowledge-only boundary: the filter that keeps gold dispositions out (HR-4).

The c03 loader walks ALL of corpus/, including corpus/cases/. Those case files
carry a `## Disposition` section, which the chunker emits as its own retrievable
chunk. Embedded into the c03 index, a query case could retrieve its OWN gold
answer — a textbook leakage cheat.

These tests are deterministic and model-free: they prove the filter at the
boundary that feeds build_chroma, so a knowledge index built from
`knowledge_chunks(...)` provably carries no case metadata (build_chroma writes
source_path verbatim). The built-index assertion lives in
tests/evals/test_knowledge_index_leakage.py.
"""

from __future__ import annotations

from pathlib import Path

from vigil.corpus.loader import load_chunks
from vigil.retrieval.knowledge import CASES_PREFIX, knowledge_chunks

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "corpus"


def _case_chunks(chunks):
    return [c for c in chunks if c.source_path.startswith(CASES_PREFIX)]


def test_corpus_actually_contains_case_chunks() -> None:
    # Guards against a vacuous filter test: if cases/ moves or empties, the
    # exclusion tests below would pass for the wrong reason.
    all_chunks = load_chunks(CORPUS_ROOT)
    assert _case_chunks(all_chunks), (
        "expected corpus/cases/*.md to produce chunks — the leak this filter "
        "exists to prevent; if this fails, the exclusion tests are vacuous"
    )


def test_knowledge_chunks_excludes_all_cases() -> None:
    knowledge = knowledge_chunks(load_chunks(CORPUS_ROOT))
    leaked = _case_chunks(knowledge)
    assert not leaked, "case chunks leaked into the knowledge set:\n  " + "\n  ".join(
        f"{c.source_path} :: {c.section_title}" for c in leaked
    )
    assert knowledge, "knowledge set is empty — filter dropped the whole corpus"


def test_knowledge_chunks_drops_only_cases() -> None:
    # Nothing but cases/ is removed — the knowledge corpus stays intact.
    all_chunks = load_chunks(CORPUS_ROOT)
    knowledge = knowledge_chunks(all_chunks)
    assert len(knowledge) == len(all_chunks) - len(_case_chunks(all_chunks))
