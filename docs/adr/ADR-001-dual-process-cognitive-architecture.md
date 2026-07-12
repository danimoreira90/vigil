# ADR-001 â€” Dual-Process Cognitive Architecture

**Status:** Accepted
**Date:** 2026-06-11
**Deciders:** Daniel Moreira

---

## Context

Vigil must satisfy four hard forces at once:

1. Decisions in **< 200 ms** (HR-7) â€” a fitness function, not an aspiration.
2. Every live decision **explainable**, with reason codes (HR-5).
3. **Cold start**: no labels on day one; detection runs on rules + anomaly.
4. The system must demonstrate an applied LLM cognitive layer with **embeddings and retrieval-grounded answers**.

An LLM call costs 0.5â€“several seconds and can hallucinate. Put it in the decision path and it breaks HR-7 and turns an auditable decision into a black box (violating HR-5 and AP-1). Yet the LLM is exactly where explanation, investigation, and cold-start knowledge live. We need an architecture that uses LLM reasoning **without it ever touching the latency path**, and that **grounds** that reasoning so a high-stakes domain can trust it.

## Decision

Adopt a **dual-process** architecture, after Kahneman's System 1 / System 2.

**System 1 â€” fast, statistical, in the latency path.**
- A stateless **Scorer**: Transaction in â†’ Score + Reason Codes out. Rules + anomaly detection at cold start; a gradient-boosted Scorer once labels accrue (SHAP â†’ reason codes).
- The **Decision Engine** owns policy: it maps Score + Reason Codes â†’ `allow` / `block` / `review`, then persists. (AP-1, AP-2.)
- No LLM. No call to a model server. Budget: **< 200 ms** (HR-7).

**System 2 â€” slow, deliberate, async, OUTSIDE the latency budget.**
A **Private RAG fraud analyst** that works the `review` queue only. For each Case it:
1. **retrieves** from a read-only fraud-knowledge corpus (chargeback reason-code definitions, fraud typologies, handling policies, anonymized past cases) via embeddings + vector search;
2. generates a **grounded, structured disposition** â€” JSON `{recommendation, confidence, reason_codes, cited_sources, rationale}` â€” that cites the retrieved knowledge rather than inventing it;
3. drafts the analyst **Case note**;
4. at cold start, **proposes candidate Rules** from recurring case patterns for Daniel to review and version.

System 2 is **advisory-only** (AP-4, already decided): it never auto-acts; a human dispositions every Case. It runs on **masked input only** (HR-3) and, by default, on **local/private inference** so case data never leaves the host.

## Decision drivers

Latency (HR-7), explainability / regulatory (HR-5), privacy (HR-3), cold start, hallucination risk in a high-stakes domain, reversibility (Ford), clear data ownership (Newman), bounded contexts (Evans).

## Why this shape (the actual reasons, not name-dropping)

- **Clean Architecture (Martin).** The latency-critical core (Scorer) is the stable center and depends on nothing volatile. The LLM/RAG is a plugin at the boundary. The dependency rule runs one way: System 2 may read System 1's outputs; **System 1 must never import System 2.**
- **Evolutionary architecture (Ford).** Swapping the LLM, editing a prompt, or updating the corpus are artifact/config changes â€” not hot-path redeploys. Cheap to reverse. Enforced by fitness functions below.
- **Data ownership (Newman).** Scorer owns scoring; Decision Engine owns policy + persistence; System 2 owns case reasoning and only *reads* a versioned knowledge store. No shared writes.
- **Bounded contexts (Evans).** Scoring, decision policy, and case investigation are distinct domains with distinct language (`CONTEXT.md`).
- **Simplicity (CODE-SIMPLICITY).** No Scorer/LLM abstraction layer until a second implementation exists (CS-2); System 2 is functions + a vector store, not a framework (CS-1, CS-10).

## Fitness functions (how the decision is enforced, not merely stated)

- **LAT-1:** scoring-path p99 < 200 ms or the build fails (HR-7). System 2 is explicitly outside this budget.
- **ARCH-1:** an import contract fails the build if any System 1 module imports an LLM / vector-store / System 2 module (the one-way dependency rule, machine-checked).
- **PII-1:** a test asserts no raw PAN/PII field can reach a System 2 prompt; inputs are masked (HR-3).
- **LEAK-1:** neither system reads `data/test/` outside the eval harness (HR-4).

## Consequences

**Good:** latency stays safe; decisions are explainable and now **grounded** (citations, not opinions); private by default; cold start is bootstrapped instead of blocked; the LLM layer is **fully removable without touching scoring**; the design exercises the full LLM / embeddings / RAG competency set end to end.

**Cost:** two runtimes to operate; a Case and its System 2 analysis are **eventually consistent** (async); the corpus must be curated and versioned; **retrieval quality** becomes something to evaluate and monitor (EDD).

## Alternatives considered

1. **LLM in the scoring path** â€” rejected: breaks HR-7; makes the decision a black box (HR-5, AP-1).
2. **LLM-only detection, no ML Scorer** â€” rejected: latency, cost, no calibrated probability, weak on tabular fraud.
3. **Free-form LLM analyst without retrieval** â€” rejected: hallucination is unacceptable in a high-stakes decision and fails the grounding requirement. RAG is what makes the analyst auditable.

## Follow-ups

- C4 L1/L2 diagrams for the two processes 
- **ADR-002:** embedding model + vector store choice (real trade-off â†’ its own ADR).
- **ADR-003:** local vs cloud inference for System 2 (privacy / cost / latency trade-off).
