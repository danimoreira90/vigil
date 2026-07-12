"""c05 context-leakage gate (HR-4): the RAG retrieval path can never surface a
case chunk, and no gold `## Disposition` header can reach an assembled prompt.

This is the RETRIEVAL-side proof to complement test_pipeline.py's assembly-side
proof and test_knowledge_index_leakage.py's index-side proof. It drives the real
retrieve_context over all 10 held-out cases: the query is the (disposition-
stripped) case body, and the assertion is on source_path metadata, which
build_knowledge_index writes verbatim — deterministic despite float embeddings.

The cases/-exclusion (knowledge_chunks) is the PRIMARY control; load_case_body
stripping `## Disposition` on the query side is the belt-and-suspenders second.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from vigil.generation.case_loader import load_case_body
from vigil.rag.pipeline import build_rag_prompt, retrieve_context
from vigil.retrieval.knowledge import CASES_PREFIX

CASES_DIR = Path(__file__).resolve().parents[2] / "corpus" / "cases"
CASE_PATHS = sorted(CASES_DIR.glob("case-*.md"))


def test_ten_cases_present() -> None:
    assert len(CASE_PATHS) == 10, f"expected 10 cases, found {len(CASE_PATHS)}"


@pytest.mark.parametrize("case_path", CASE_PATHS, ids=lambda p: p.name)
def test_retrieval_never_returns_a_case_chunk(case_path: Path) -> None:
    case_body = load_case_body(case_path)
    hits = retrieve_context(case_body)
    leaked = [h.chunk.source_path for h in hits if h.chunk.source_path.startswith(CASES_PREFIX)]
    assert not leaked, f"case chunk retrieved for {case_path.name}: {leaked}"


@pytest.mark.parametrize("case_path", CASE_PATHS, ids=lambda p: p.name)
def test_assembled_prompt_carries_no_gold_disposition_header(case_path: Path) -> None:
    case_body = load_case_body(case_path)
    prompt = build_rag_prompt(case_body, retrieve_context(case_body))
    assert "## Disposition" not in prompt
