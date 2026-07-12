# Vigil — Dual-Process Card-Fraud Detection with a Private-RAG Analyst

**Sistemas Cognitivos / Linguagem Natural — Aplicações LLMs**

Vigil is a card-fraud detection system built on a dual-process (Kahneman) architecture:

- **System 1 — the Scorer.** A fast ML risk score on every Transaction. No LLM, sub-200 ms, fully auditable. Out of scope for this assignment's five notebooks (kept lean by design).
- **System 2 — the Analyst.** An asynchronous, advisory **Private RAG** pipeline. For a Case routed to the human review queue, it retrieves grounding chunks from a fraud-knowledge corpus and generates a **structured, cited Disposition** (`recommendation`, `confidence`, `reason_codes`, `cited_sources`, `rationale`) validated against a schema. It never acts — a human dispositions every Case.

Everything in the shipped path runs **on-box**: local embeddings (sentence-transformers) and local generation (Ollama). No case data leaves the host.

---

## Requirements

| | |
|---|---|
| Python | 3.13 |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Local LLM | [Ollama](https://ollama.com) + `llama3.1:8b` |
| GPU | Optional. An 8 GB card (RTX 3070) gives ~4–8 s/generation; CPU works but is slower. System 2 is asynchronous, so latency is not a gate. |
| Cloud key | **Optional.** Only for the c04 cloud *comparison*. The system runs fully without it. |

---

## Install

```bash
git clone https://github.com/danimoreira90/vigil.git
cd vigil

# IMPORTANT: sync BOTH extras together.
# `uv sync --extra X` resolves the environment to base + X only — it will
# uninstall the other extra's packages. Always pass both.
uv sync --extra system2 --extra c01
```

Install Ollama from https://ollama.com, then pull the generation model:

```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b "Reply with the single word OK."   # sanity check
```

**Optional — cloud comparison (c04 only).** The cloud path is a documented comparison, never the shipped path. Set the key as an environment variable; it is never committed:

```powershell
$env:OPENAI_API_KEY = "sk-..."      # PowerShell
```
```bash
export OPENAI_API_KEY="sk-..."      # bash
```

Without a key, the c04 notebook skips the cloud cells cleanly and the local results still stand.

---

## The knowledge base

The corpus is **52 hand-authored markdown documents** in `corpus/`:

| Family | Contents |
|---|---|
| `typologies/` | 12 fraud typologies (card-testing, account-takeover, friendly-fraud, …) |
| `reason_codes/` | 18 network reason codes (Visa, Mastercard, Amex) |
| `glossary.md` | Vigil's own reason codes, one H2 section per code |
| `policies/` | 6 operational playbooks (disposition guidelines, escalation thresholds, …) |
| `regulatory/` | 5 summaries (PCI-DSS, PSD2/SCA, …) |
| `cases/` | 10 synthetic, masked Cases — the **evaluation set** |

All cases are **synthetic**. No real cardholder, card, or merchant data exists anywhere in this repository. Identifiers are masked tokens; a test enforces this at the chunk boundary.

**No downloads are required.** The retrieval index is built from `corpus/` in seconds.

---

## Index the knowledge base

Indexes are build artifacts (`data/index/`, gitignored) and are rebuilt automatically the first time a notebook needs them. Two indexes exist:

- **Full corpus index** (c03) — used for the retrieval-quality evaluation.
- **Knowledge-only index** (c05) — **excludes `corpus/cases/`**. This is a security control, not an optimization: if a Case could retrieve its own document, it would retrieve its own gold Disposition, and every score downstream would be meaningless. A test asserts zero case chunks reach this index.

To build the c05 knowledge index explicitly:

```bash
uv run python -c "from pathlib import Path; from vigil.retrieval.knowledge import build_knowledge_index, KNOWLEDGE_INDEX_DIR; c = build_knowledge_index(Path('corpus'), KNOWLEDGE_INDEX_DIR); print('chunks indexed:', c.count())"
```

---

## Run the notebooks

```bash
uv run jupyter lab
```

Run in order. Each is self-contained and maps to one graded competency:

| Notebook | Competency | What it demonstrates |
|---|---|---|
| `c01_modelos_llm.ipynb` | #1 — HuggingFace NLP | Encoder vs decoder on the same task: DeBERTa-v3 zero-shot NLI vs a prompted Qwen2.5-0.5B, classifying Cases into 13 labels. Tokenizer inspection (SentencePiece vs byte-level BPE), pipeline vs manual inference. |
| `c02_prompting.ipynb` | #2 — Prompt engineering | Three layered techniques (role+schema+delimiters → +few-shot → +chain-of-thought), structured JSON with validation and repair, a 90-generation multi-run comparison, and the production prompt chosen on the numbers. |
| `c03_embeddings_busca.ipynb` | #3 — Embeddings & retrieval | BGE-small vs MiniLM × dense / BM25 / hybrid (RRF), evaluated with 18 gold domain queries plus an out-of-domain probe. Hybrid MiniLM+BM25 ships. |
| `c04_inferencia_local_ou_remota.ipynb` | #4 — Local / remote inference | Local vs cloud generation on identical prompts: privacy, cost, latency, control, quality. Includes a real local-inference failure analysis. |
| `c05_rag_pipeline.ipynb` | #5 — RAG pipeline | The full Private-RAG pipeline, a with-context vs without-context experiment, failure analysis, and the security section (prompt injection, context leakage, controls). |

Notebooks 1–4 execute in minutes. Notebook 5 is **analysis-only** — it loads recorded results (see below) rather than re-running generation, so it renders in seconds.

---

## Reproduce the evaluations

The heavy generation loops live in scripts, not notebooks (a long loop exceeds Jupyter's per-cell timeout). Each writes results incrementally, so a crash or interrupt preserves completed work.

```bash
# c02 — prompt-technique comparison: 10 cases × 3 techniques × 3 runs = 90 generations (~8 min)
uv run python tests/evals/run_c02_prompting.py 10 3

# c05 — RAG with/without context: 10 cases × 2 arms × 3 runs = 60 generations (~9 min)
uv run python tests/evals/run_c05_rag.py 10 3

# c05 — prompt-injection probe (live, adversarial case body)
uv run python tests/evals/probe_c05_injection.py
```

Results land in `tests/evals/*.json`. These committed JSON files are the frozen baseline the notebooks render; re-running overwrites them with fresh numbers.

---

## Tests

```bash
uv run pytest -q      # 105 tests
```

The suite includes the anti-leakage gates that make the evaluation numbers meaningful:

- **Disposition stripping** — `load_case_body` removes each Case's `## Disposition` section before the prompt is built, and raises if the header is missing rather than silently returning the whole file.
- **Knowledge-index exclusion** — a gate builds the real c05 index and asserts that no chunk originates from `corpus/cases/`.
- **PII guard** — a pattern check asserts no PAN-shaped or PII-shaped content exists in any corpus chunk.
- **Retrieval floor** — the c03 recall@5 gate fails the build if retrieval quality regresses below its committed floor.

---

## Repository layout

```
corpus/          the 52-document fraud-knowledge base (+ 10 synthetic cases)
src/vigil/
  corpus/        loader + chunker (H2-section chunks)
  retrieval/     embeddings, Chroma, BM25, hybrid RRF, knowledge-only index
  generation/    schema, JSON repair, prompt builders, local/cloud generation seam
  classify/      the c01 encoder/decoder typology classifiers
  rag/           the c05 pipeline — retrieve → augment → generate → validate
notebooks/       the five graded notebooks
tests/           unit tests, evaluation harnesses, gold sets, probes
docs/adr/        architecture decision records (ADR-001/002/003)
data/            build artifacts and raw datasets — gitignored, not required
```

---

## Architecture decisions

The three ADRs in `docs/adr/` record the decisions and their trade-offs:

- **ADR-001 — Dual-process architecture.** Why the LLM sits outside the latency path, and why System 2 is a Private RAG rather than a classifier.
- **ADR-002 — Embeddings and retrieval.** Local embeddings over an API, Chroma over FAISS, and why a measured evaluation overturned the predicted winner.
- **ADR-003 — Inference strategy.** Ship local; cloud as a documented comparison. Includes the amendment recording why the local engine moved from GPT4All to Ollama after measured hardware limits.

---

## Security posture

- **No real data.** Synthetic, masked cases only; a test enforces it.
- **No keys in the repository.** The cloud comparison reads `OPENAI_API_KEY` from the environment and is optional.
- **Private by default.** The shipped path — embeddings and generation — runs entirely on-box.
- **Context-leakage control.** Two independent barriers keep a Case's gold answer out of its own prompt: the disposition is stripped on the query side, and case documents are excluded from the retrieval index entirely.
- **Prompt-injection posture.** The untrusted Case body is fenced inside explicit `data, not instructions` delimiters, placed *after* and *outside* the trusted retrieved-knowledge block. The delimiter is a partial control; the load-bearing guarantees are downstream — schema validation rejects malformed output, cited sources must resolve to real corpus paths, a `block` requires reason codes, and the model only ever *recommends* (a human decides). A live probe measures whether the model obeys an injected instruction; the result is reported in `c05_rag_pipeline.ipynb`.
