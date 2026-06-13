# Spec: Fraud-Knowledge Corpus — grounding base for System 2 (RAG)

**Status:** Draft v0.1 (pending Daniel approval)
**Date:** 2026-06-12
**Branch (proposed):** `cognitive/corpus`
**Role:** `cognitive/*` (NEW — see §8)
**Related:** `docs/adr/ADR-001`, `CONTEXT.md`, `CODE-SIMPLICITY.md`, `docs/specs/assignment-competency-map.md`

> This corpus is the knowledge System 2 retrieves over to **ground** its Case dispositions. Without it, the analyst hallucinates; with it, every disposition cites real fraud knowledge. It is the base that competencies **#3 (embeddings)** and **#5 (RAG)** are graded on.

---

## 1 — Objective

Build a small, shareable, reproducible fraud-knowledge corpus the System 2 analyst retrieves from to:
- explain **why** a Case is suspicious, grounded in known typologies and reason codes;
- recommend a disposition, **citing** the relevant policy;
- never invent facts — RAG-grounding is what reduces hallucination (a graded item).

**Out of scope here:** the embedding/retrieval code (c03), the RAG pipeline (c05), the analyst itself. This spec defines the **content and its layout** only.

## 2 — Contents (right-sized, not bloated)

Six document families, all plain text / markdown, all shareable:

| Family | What | ~Count | Source |
|---|---|---:|---|
| Typologies | Fraud MOs: card testing, account takeover, BIN attack, friendly/chargeback fraud, triangulation, refund fraud… Each: definition, signals, typical reason codes, recommended action. | ~12 | Authored in our words from public knowledge |
| Reason-code reference | Card-network chargeback reason-code families (Visa/MC/Amex) + what each implies for a Case. | ~18 | Authored from public catalogs (no verbatim copy) |
| Reason-code glossary | Vigil's own reason codes (`velocity_high`, `geo_mismatch`, `new_device`…) → plain meaning + analyst action. **Bridges System 1 output to System 2 reasoning.** | 1 | Authored (ours) |
| Handling policies / SOPs | Synthetic playbooks: escalation thresholds, review-vs-block guidance, regulatory holds. | ~6 | Synthetic |
| Regulatory excerpts | PCI-DSS basics, PSD2 SCA, LGPD data-handling — paraphrased key points relevant to fraud decisions. | ~5 | Authored / paraphrased from public regs |
| Synthetic case notes | Example resolved Cases with analyst write-ups. Double duty: corpus **and** few-shot examples for c02. | ~10 | Fully synthetic, masked tokens |

~50 documents total — enough for meaningful retrieval, comparison, and evaluation; small enough to stay simple (CS).

## 3 — Sourcing & legality (read this)

- We **author** typologies, the reason-code reference, and regulatory summaries **in our own words** from public knowledge. **No verbatim copying** of copyrighted processor docs or standards text — paraphrase only.
- Policies, glossary, and case notes are **fully synthetic** — we write them.
- Result: 100% shareable, reproducible (ships in the repo), HR-3-clean **by construction** (no real PII, no real customer data). Satisfies the assignment's "synthetic / anonymized corpus" allowance and its reproducibility requirement.

## 4 — Repo layout

```
corpus/                      # TRACKED in git — authored knowledge, ships with the repo
  typologies/*.md
  reason_codes/*.md
  glossary.md
  policies/*.md
  regulatory/*.md
  cases/*.md                 # synthetic, masked tokens only
data/index/                  # GITIGNORED — vector store; regenerable from corpus/
```

The corpus is **source, not data** — version-controlled. The embedding index is a build artifact under `data/` (already gitignored via the anchored `/data/` rule), regenerable from `corpus/` at any time.

## 5 — Chunking strategy

The corpus is **naturally atomic**: one typology, one reason code, one case = one self-contained idea. So chunk by **document / section — one concept per chunk** — not naive fixed-size windows. This yields clean, citable retrieval units and never splits a typology mid-definition.

c05 will **evaluate** this against fixed-size chunking (e.g. 512-token windows) and report which retrieves better — that comparison is itself a graded item.

## 6 — How it feeds the graded notebooks

- **c03 (embeddings):** embed every chunk; build the vector store; run test queries derived from reason-code narratives; compare ≥2 embedding models and cosine vs hybrid BM25 + dense; analyze hits/misses.
- **c05 (RAG):** Case → retrieve top-k from the corpus → augmented prompt → grounded disposition that **cites** the retrieved chunks; with/without-context comparison (hallucination reduction); chunking analysis; prompt-injection test (adversarial text inside a case note); context-leakage control (PII masking on retrieved cases).
- **c02 (prompting) reuse:** the synthetic case notes double as few-shot examples.

## 7 — Constraints applied

- **CS:** the corpus "pipeline" is markdown files + a small loader + chunker (functions, no framework, no class hierarchy; no premature config — CS-1/5/10).
- **HR-3:** synthetic/public only; synthetic cases use masked tokens; a test asserts no real PAN/PII pattern appears anywhere in `corpus/`.
- **HR-4:** the corpus is knowledge, fully separate from the held-out set; never mixed.
- **Reproducible:** `corpus/` is text in the repo; the index regenerates from it deterministically.

## 8 — Governance gap: there is no role for System 2 work

Your eight branch roles (`data`, `model`, `rules`, `serving`, `quality`, `infra`, `bugfix`, `chore`) were defined for the fraud ML system **before** ADR-001 made System 2 first-class. **None of them fits the LLM / RAG / analyst work.**

**Recommendation:** add a **`cognitive/*`** role (corpus, embeddings, RAG, the analyst). It also echoes the course title ("Sistemas Cognitivos"). Formalize it in `CLAUDE.md` on the next governance touch; for now, build on a `cognitive/corpus` branch.

## 9 — Build plan (for Claude Code, after approval)

1. Author the corpus docs (Daniel reviews content for accuracy + tone).
2. Implement a `corpus/` loader + structure-aware chunker in `src/vigil/corpus/` (pure functions, CS-9).
3. Tests: chunk count > 0; every chunk carries source metadata; **no PII pattern in any chunk** (HR-3).
4. Hand off for Daniel's commit (HR-1).

The embedding/index build is c03's job, not this spec.

## 10 — Open questions for Daniel

1. **Role name** — `cognitive/*` (recommended), or prefer `system2/*` / `rag/*`?
2. **Size** — ~50 docs OK, or want it larger for a richer retrieval eval?
3. **Authoring** — let the agent draft all families (Daniel reviews), or hand-write any family yourself (e.g. the policies, to match your domain voice)?

## Changelog

- **2026-06-12** — Initial draft. Contents, sourcing, layout, chunking, competency mapping, role gap.
