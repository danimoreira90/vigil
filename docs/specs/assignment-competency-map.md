# Assignment ↔ Vigil — Competency Coverage Map

**Purpose:** map every graded competency (and its rubric items) to a concrete Vigil deliverable, so nothing slips.
**Due:** 2026-06-29 · **Deliverables:** 5 notebooks + `README.md` + report PDF · **Architecture:** see `docs/adr/ADR-001`.

---

## The substrate (not graded directly — it feeds everything)

**System 1 produces real Cases.** A baseline Scorer on IEEE-CIS + SHAP reason codes. Keep it **lean** (CS / YAGNI — the rubric grades none of the model's recall or latency). It exists so the LLM layer reasons over *real* scores and *real* reason codes — making this an **applied system, not isolated tests** (which the brief explicitly demands).

The five notebooks then progressively build **System 2** — the Private RAG fraud analyst — fed by that substrate.

---

## c01_modelos_llm.ipynb — Competency 1 (NLP with LLMs / Hugging Face)

**Build:** classify a Case into a fraud typology. Show an **encoder-only** model (HF zero-shot, NLI-based) vs a **decoder** LLM on the same task. Tokenization; pipeline vs manual inference; generation params.

**Rubric covered:** pretrained model on the domain ✓ · configure tokenizer/pipeline/params ✓ · compare models ✓ · explain encoder-vs-decoder ✓ · relate results to the use case ✓.

**Constraints:** masked inputs (HR-3); a small typology eval set with full, honest metrics (EDD + anti-cheat); functions, not classes (CS-1/CS-10).

## c02_prompting.ipynb — Competency 2 (prompt engineering + controlled output)

**Build:** the disposition prompt (role / context / task / format). Three techniques — **zero-shot**, **few-shot** (past resolved cases), **chain-of-thought** (investigation steps); plus a meta-prompt pass. Output strict JSON `{recommendation, confidence, reason_codes, cited_sources, rationale}` with **pydantic validation + error handling**. Iterate versions against an explicit metric (% valid JSON; agreement with a labeled mini-set).

**Rubric covered:** model/API call ✓ · compare ≥3 techniques ✓ · structured prompts ✓ · JSON + parsing/validation ✓ · iterate with a quality criterion ✓.

**Constraints:** fail loud on invalid JSON, no silent default (CS-6); honest prompt-eval output (anti-cheat); reason codes present (HR-5).

## c03_embeddings_busca.ipynb — Competency 3 (embeddings + vector search)

**Build:** embed the fraud-knowledge corpus. Compare two embedding models; cosine vs **hybrid BM25 + dense**. Test queries drawn from real reason-code narratives. Analyze hits/misses; justify the choice.

**Rubric covered:** embeddings for docs/queries ✓ · semantic + hybrid search ✓ · evaluate models/metrics/rankings ✓ · hit/miss analysis ✓ · justify strategy ✓.

**Constraints:** a retrieval eval with recall@k, reported honestly (EDD); use Chroma/FAISS **directly**, no wrapper (CS-1).

## c04_inferencia_local_ou_remota.ipynb — Competency 4 (private inference)

**Build:** run the analyst **locally** (GPT4All / Ollama); compare against a cloud API on cost / latency / quality / privacy; justify **local for fraud** (HR-3). Programmatic SDK/API integration.

**Rubric covered:** local/remote execution justified ✓ · compare requirements/perf/cost/privacy ✓ · programmatic integration ✓ · local-vs-cloud analysis ✓ · privacy/cost/latency/control ✓.

**Constraints:** no secrets in code, `.env` only; measure latency honestly; the privacy argument **is** the HR-3 story (this is the natural fit, not a stretch).

## c05_rag_pipeline.ipynb — Competency 5 (RAG + security) — the capstone

**Build:** full pipeline — load → chunk → embed → Chroma → top-k → augmented prompt → grounded disposition; reproducible Q&A; **with vs without context** (hallucination reduction); chunking analysis; failure points. Security: **prompt injection** via an adversarial case-note / merchant field; **context leakage** (PII in a retrieved past case → masking control); proposed controls.

**Rubric covered:** full RAG ✓ · vector store functional + documented ✓ · chunking/retrieval/with-vs-without analysis ✓ · failure points + improvements ✓ · prompt injection + leakage + controls ✓ · coherent professional problem ✓ · reproducible ✓ · integrates LLM+prompts+embeddings+grounding ✓ · justify with results ✓ · no secrets ✓ · critical analysis of limits/risks ✓.

**Constraints:** HR-3 / HR-4; anti-cheat (real before/after, no cherry-picking); this notebook ties c01–c04 into one System 2.

---

## Remaining deliverables

- **`README.md`** — install deps, prepare the corpus, index the base, run queries.
- **Report PDF** — every section the brief lists, structured around ADR-001 + these notebooks. Filename: `daniel_moreira_sistemas-cognitivos-linguagem-natural_aplicacoes-llms.pdf`.

## Time risk (18 days)

The **corpus + c03 + c05** (embeddings + RAG) are the heaviest and highest-graded — **start them first.** c01/c02 are quicker. System 1 stays lean. The corpus is the long pole: it gates c03 and c05, so it's the next thing to spec.
