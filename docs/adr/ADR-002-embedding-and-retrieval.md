# ADR-002 — Embedding Model & Retrieval Strategy for System 2

**Status:** Proposed (awaiting Daniel approval)
**Date:** 2026-06-14
**Deciders:** Daniel Moreira
**Related:** `docs/adr/ADR-001`, `docs/specs/corpus-foundation.md`, `CODE-SIMPLICITY.md`, `docs/specs/assignment-competency-map.md` (#3)

---

## Context

c03 must embed the fraud-knowledge corpus (282 chunks) and retrieve the relevant chunks for a Case. The choice of embedding model, vector store, and retrieval strategy is **graded** — the rubric requires *justifying the search strategy* and *comparing models/strategies with domain queries*. It must respect **HR-3** (privacy) and the Private-RAG thesis (ADR-001), stay simple (CS), and feed c05's RAG. The corpus is **mixed**: lexical tokens (reason-code IDs like "Visa 10.4", "MC 4837") and semantic prose (typology and case narratives).

## Decision drivers

Privacy (HR-3 — masked case text must not leave the host), the graded justify-and-compare requirement (#3), the lexical+semantic mix, simplicity (CS), reproducibility, and it must hand off cleanly to c05.

## Decision

- **Embeddings — local, via sentence-transformers.** Primary `BAAI/bge-small-en-v1.5`; baseline `all-MiniLM-L6-v2`. Compare both. Both are small, CPU-friendly, and run on-box — no case text leaves the machine (HR-3).
- **Vector store — Chroma** (local, persistent, metadata-native). Index lives at `data/index/` (gitignored, regenerable from `corpus/`).
- **Retrieval — compare three strategies:** dense (cosine over embeddings), lexical (BM25), and hybrid (combine). Report recall@k and hit/miss on a gold query set.
- **Similarity — cosine** on normalized embeddings.
- **No orchestration framework** (no LangChain / LlamaIndex). Build the pipeline explicitly.

## Why (the actual reasons)

- **Local embeddings, not OpenAI.** Fraud case text — even masked — should not go to a third-party API. Local sentence-transformers keep it on-box (HR-3, ADR-001 Private-RAG). That privacy choice is itself a graded justification (#3 + #4). OpenAI embeddings can appear as a *comparison point* in the report, never the primary path.
- **BGE-small primary, MiniLM baseline.** Both tiny and local; comparing them satisfies "compare models" and gives EDD a baseline to beat. BGE-small generally tops MiniLM on retrieval at the same size/speed.
- **Chroma over FAISS.** We have rich chunk metadata (`family`, `source_path`, `section_title`) for citations and filtered retrieval. Chroma stores it natively; FAISS would need a hand-built parallel metadata store (CS-1 — don't build the layer Chroma already gives you). At 282 chunks FAISS's speed edge is irrelevant. FAISS stays the noted alternative for scale we don't have.
- **Hybrid (BM25 + dense) fits the corpus — not ceremony.** Reason-code queries ("Visa 10.4", "4837") are lexical; dense embeddings can miss exact codes, BM25 nails them. Typology/case queries are semantic; dense wins. Combining both is the right design for a corpus mixing codes and prose — and it's a graded comparison item.
- **No framework.** The rubric explicitly rewards showing you understand the pipeline ("construção manual do prompt aumentado", "não apenas consumo de uma ferramenta pronta"). A manual pipeline is both simpler (CS) and higher-scoring. LangChain would hide the mechanics the grader wants to see.

## How we justify it with results (graded — EDD)

Author a small **gold query set** (~15–20 queries, each mapped to the chunk(s) that should retrieve, e.g. "cardholder denies online purchase" → `visa-10-4`; "many small charges across many cards" → `card-testing`). Measure **recall@k** and **MRR** for each model × strategy. Report where retrieval hit, where it failed, and why. That single eval covers the rubric's *evaluated models* + *hit/miss analysis* + *justified strategy* trio — with numbers, not assertions.

## Consequences

**Good:** private by construction; comparison + justification fall straight out of the eval (graded items *and* report content); metadata-native citations for c05; simple, framework-free, reproducible.

**Cost:** three retrieval paths to implement (modest); a ~20-pair gold set to author; three new System-2 deps.

## Alternatives rejected

1. **Cloud embeddings (OpenAI) as primary** — sends case text off-box; undercuts the privacy thesis that's a graded differentiator. Kept only as a comparison data point.
2. **FAISS as primary** — needs a hand-built metadata layer for citations; no benefit at this corpus size (CS).
3. **LangChain / LlamaIndex** — over-engineering for 282 chunks, and it hides the pipeline the rubric wants demonstrated.

## Dependencies introduced (System 2 runtime — off the <200 ms path, not latency-critical)

`sentence-transformers`, `chromadb`, `rank-bm25`. These are the deps ADR-001 earmarked for this ADR; diff-review on `pyproject.toml`, and this ADR is their justification. (Note: corpus and queries are English, so English-specialized models are correct; a multilingual model would only be needed if queries arrive in Portuguese.)

## Follow-ups

- **ADR-003** — local vs cloud inference for *generation* (c04).
- The gold query set lands under `tests/` or `corpus/eval/` (CREATE-only, EDD).

## Changelog

- **2026-06-14** — Initial draft. Embedding model, vector store, retrieval strategy, eval plan.
