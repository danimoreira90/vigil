"""Pure-string tests for the c05 RAG prompt assembly (no live model).

The trust boundary is the whole point of c05: retrieved corpus knowledge is
TRUSTED reference and must sit BEFORE and OUTSIDE the BEGIN CASE fence; the case
body is UNTRUSTED data inside the fence. These tests pin that geometry, prove the
t3 scaffold is preserved, and prove no case path / gold-disposition header can be
injected by the reference renderer. Retrieval-side leak proof lives in
test_context_leakage.py (it loads the index); this file needs no model.
"""
from __future__ import annotations

from vigil.corpus.chunker import Chunk
from vigil.generation.prompt import CASE_CLOSE, CASE_OPEN, technique_t3
from vigil.rag.pipeline import (
    REFERENCE_HEADER,
    build_rag_prompt,
    render_reference_block,
)
from vigil.retrieval.hits import ChunkHit


def _hit(rank: int, path: str, section: str, body: str) -> ChunkHit:
    return ChunkHit(
        chunk=Chunk(
            text=f"## {section}\n{body}",
            source_path=path,
            family=path.split("/")[0],
            doc_title="Doc",
            section_title=section,
        ),
        score=1.0 / rank,
        rank=rank,
    )


KNOWLEDGE_HITS = [
    _hit(1, "typologies/card-testing.md", "Card testing", "Many small auths across many cards."),
    _hit(2, "reason_codes/velocity.md", "velocity_high", "A burst of attempts in a short window."),
]

CASE_BODY = (
    "# Case — TX-2026-Q2-TEST-001\n"
    "- card_token: TKN-test...0000\n"
    "- reason_codes: [velocity_high]\n"
)


def test_reference_block_precedes_and_sits_outside_the_case_fence():
    prompt = build_rag_prompt(CASE_BODY, KNOWLEDGE_HITS)
    # rindex, not index: the few-shot exemplars carry their own BEGIN CASE
    # fences — the untrusted case fence is the LAST one in the prompt.
    case_open = prompt.rindex(CASE_OPEN)
    assert prompt.index(REFERENCE_HEADER) < case_open
    for hit in KNOWLEDGE_HITS:
        assert prompt.index(hit.chunk.text) < case_open


def test_no_chunk_text_lands_inside_the_begin_case_fence():
    prompt = build_rag_prompt(CASE_BODY, KNOWLEDGE_HITS)
    fenced = prompt[prompt.rindex(CASE_OPEN):prompt.rindex(CASE_CLOSE)]
    for hit in KNOWLEDGE_HITS:
        assert hit.chunk.text not in fenced


def test_reference_block_renders_citable_path_handles():
    block = render_reference_block(KNOWLEDGE_HITS)
    assert "[S1] typologies/card-testing.md ## Card testing" in block
    assert "[S2] reason_codes/velocity.md ## velocity_high" in block


def test_reference_block_instructs_cited_sources_from_shown_paths():
    block = render_reference_block(KNOWLEDGE_HITS)
    assert "cited_sources" in block


def test_rag_prompt_preserves_full_t3_scaffold_in_order():
    prompt = build_rag_prompt(CASE_BODY, KNOWLEDGE_HITS)
    assert "senior fraud-case analyst" in prompt          # role
    assert "Return ONLY one JSON object" in prompt         # schema
    assert "TX-2026-Q2-FS-A" in prompt                     # few-shot
    assert "Before emitting the JSON" in prompt            # reasoning
    # order: reasoning → reference → untrusted case fence (rindex; see above)
    assert (
        prompt.index("Before emitting the JSON")
        < prompt.index(REFERENCE_HEADER)
        < prompt.rindex(CASE_OPEN)
    )


def test_case_body_still_inserted_verbatim():
    prompt = build_rag_prompt(CASE_BODY, KNOWLEDGE_HITS)
    assert CASE_BODY in prompt


def test_baseline_t3_has_no_reference_block():
    # The baseline arm must be byte-identical to c02 T3: one variable only.
    assert REFERENCE_HEADER not in technique_t3(CASE_BODY)


def test_renderer_cannot_inject_case_path_or_disposition_header():
    prompt = build_rag_prompt(CASE_BODY, KNOWLEDGE_HITS)
    assert "cases/" not in prompt
    assert "## Disposition" not in prompt
