# ADR-003 — Inference Strategy for System 2 Generation

**Status:** Accepted (2026-06-14)
**Date:** 2026-06-14
**Deciders:** Daniel Moreira
**Related:** `docs/adr/ADR-001`, `docs/adr/ADR-002`, `CODE-SIMPLICITY.md`, `docs/specs/assignment-competency-map.md` (#4)

---

## Context

c04 and c05 need a **generation** LLM — the model that turns retrieved corpus context + a masked Case into the structured disposition JSON (`recommendation`, `confidence`, `cited_sources`, `rationale`). Where that model runs (local / cloud / private) is **graded** under competency #4, which requires *justifying the choice* and *comparing privacy, cost, latency, control, and quality*. The rubric names **GPT4All** for the local path. The choice must fit the Private-RAG thesis (ADR-001) and **HR-3** (no case data leaves the host), and the grader must be able to **reproduce** it.

## Decision drivers

Privacy (HR-3 — the prompt carries masked case fields + retrieved corpus; on the shipped path it must not leave the box), the graded justify-and-compare requirement (#4), structured-JSON reliability (small local models are weaker at valid JSON than frontier cloud models), reproducibility (grader has no guarantee of a cloud key), and simplicity (CS).

## Decision

- **Ship LOCAL for the disposition path, via GPT4All.** System-2 generation runs on a local quantized instruct model (7–8B Q4 — e.g. Llama-3.1-8B-Instruct, with Mistral-7B-Instruct as a lighter fallback), GPU-offloaded on the RTX 3070 (`device='cuda'`). Consistent with ADR-001 (Private RAG) and ADR-002 (local embeddings) — nothing about a case leaves the host. Generation speed is **not** critical: System 2 is async and advisory (off LAT-1), so partial GPU offload or even CPU fallback is acceptable.
- **Cloud is comparison-only.** A small set of paired runs against one cloud API produces the latency / cost / quality / privacy comparison #4 asks for. It is **not** on the shipped private path and is **not** required to reproduce the system.
- **One swappable `generate()` seam.** Local and cloud sit behind a single function (one signature, two backends), so the comparison is a config swap, not duplicated code (CS). No orchestration framework.
- **Keys via environment only**, never committed; the repo ships with the local path as the default so it runs key-free (HR-3 + rubric).

## Why (the actual reasons)

- **Privacy is the spine.** The whole architecture is "the data stays on-box." Local embeddings (ADR-002) with cloud generation would leak the case + retrieved context to a third party — incoherent. Local generation keeps the thesis intact, and that coherence is itself a graded justification (#4 privacy/control).
- **Weaker local JSON is a manageable cost, and the mitigation is also graded.** Small local models fumble strict JSON more than cloud models. The fix — a tight role/context/format prompt plus schema validation and a repair retry — is exactly competency #2's structured-output work. So the cost of going local *funds* another rubric item instead of being dead weight.
- **Cloud-as-comparison gives #4 its evidence without breaking privacy.** A handful of paired calls (same prompt, local vs cloud) yields the real latency/quality/cost numbers the rubric wants, while the shipped path stays private. Best of both: graded comparison *and* a coherent private system.
- **Local-default = reproducible.** The grader runs the local path with no key and no spend. The cloud comparison is documented and optional to re-run.
- **GPT4All is the lowest-risk local engine** — the rubric names it, it has a Python SDK, runs quantized GGUF models on CPU, and needs no separate server. (Its LocalDocs RAG is ignored — we build RAG manually per ADR-002.) Ollama is the strong alternative; see open question 1.

## How we justify it with results (graded — #4)

Run the **same disposition prompts** through local and cloud and tabulate:

| Axis | What we measure |
|---|---|
| Privacy | Does case data leave the host? (local: no; cloud: yes) |
| Latency | Wall-clock per generation, local vs cloud |
| Cost | Per-call cost (local: $0 after download; cloud: token price) |
| Quality | Valid-JSON parse rate + qualitative grounding/faithfulness on a few cases |
| Control | Versioning, offline availability, dependency on a vendor |

That single paired-run table covers #4's *compare requirements/perf/cost/privacy/quality* and *analyze local-vs-cloud trade-offs* items with evidence, not assertion — same pattern as ADR-002's eval feeding #3.

## Consequences

**Good:** private by construction (HR-3, ADR-001); reproducible key-free; the local-JSON mitigation doubles as competency #2; the comparison gives #4 real numbers; one `generate()` seam keeps it simple.

**Cost:** local model needs prompt + validation/repair work to hit reliable JSON; local inference is slower than cloud (measured, not hidden); one cloud key needed for the comparison runs (handled via env, kept out of git).

## Alternatives rejected

1. **Cloud-primary (ship cloud).** Breaks the Private-RAG thesis and HR-3 — case data leaves the host. Incoherent with local embeddings.
2. **Local-only, no cloud comparison.** Misses #4's explicit *compare* item; weaker grade for no real reason (a few cloud calls are cheap).
3. **GPT4All LocalDocs as the RAG.** Hides the pipeline the rubric wants demonstrated (same reasoning that rejected LangChain in ADR-002). We use GPT4All only as the generation engine.

## Dependencies introduced (System 2 runtime — `system2` extra, off the scorer path)

Local engine: `gpt4all` (Python SDK, GPU via CUDA). Cloud comparison: `openai` (cheapest current small/mini tier; HF Inference free tier as the no-billing fallback). ADR-justified; diff-review on `pyproject`. **No keys in the repo** — env vars only, documented in the README. The comparison sends only **synthetic** corpus cases, so it is HR-3-safe even while calling a cloud API; the privacy argument is about the *production posture* (ship local), which the system demonstrates.

## Resolved parameters (2026-06-14)

1. **Local engine — GPT4All** (rubric-named, SDK-simple, no server).
2. **Hardware — RTX 3070 (8 GB VRAM)** → a 7–8B Q4 instruct model fits with GPU offload; the best-for-JSON GGUF is selected from GPT4All's catalog at build time. CPU fallback acceptable — System 2 is async, off LAT-1.
3. **Cloud comparison — OpenAI cheapest small tier** (real paired calls on synthetic cases, ~cents; cleanest evidence for #4). No-billing fallback: HF Inference free tier. Switch to local-only-documented only if Daniel declines a key — weaker on #4's *compare* item but valid.

## Follow-ups

- **c04** implements the `generate()` seam, runs the paired comparison, produces the table above.
- **c02** builds the disposition prompt + JSON validation/repair on the chosen engine (the local-JSON mitigation).
- **c05** wires retrieval → augmented prompt → local generation into the full RAG.

## Changelog

- **2026-06-14** — Initial draft. Ship-local decision, cloud-as-comparison, swappable seam, three open questions.
- **2026-06-14** — Accepted. Engine GPT4All; local model 7–8B Q4 on RTX 3070; cloud comparison via OpenAI cheap tier (HF free tier fallback).

## Update — 2026-06-20 (post-c02: local engine switched to Ollama)

c04 shipped and measured GPT4All as the local engine (committed notebook: local GPT4All vs
cloud gpt-5.4-nano — competency #4, unchanged and still the recorded comparison). Building c02
surfaced a hardware limit GPT4All cannot clear on this host:

- GPT4All's CUDA backend fails to load (error 0x7e — missing runtime DLLs).
- GPT4All's Vulkan path (device='gpu') works but is too slow for long generations: ~70 s/call on
  short probes, and chain-of-thought / RAG-length prompts push a single 3-call cell past 600 s.
  A full c02 grid would run 1-2 h; c05's retrieved-context prompts would be worse.

**Decision change:** the production local engine for System 2 generation is now Ollama
(`llama3.1:8b`, same Llama-3.1-8B family as the c04 GGUF), using the RTX 3070 via proper CUDA.
Measured: warm ~300 ms/call, cold start ~22 s (one-time VRAM load). It stays fully local and
private — nothing leaves the host (HR-3 intact) — and the rubric permits a "servidor compatível".
Ollama exposes an OpenAI-compatible endpoint, so local.py drives it with the `openai` client
already in deps; the generate() seam, Disposition schema, json_repair, and prompt.py are all
unchanged. A backend swap, not a redesign.

**What stays GPT4All:** the committed c04 notebook is the recorded competency-#4 artifact and is
not re-run. `gpt4all` remains in the system2 extra and selectable via VIGIL_LOCAL_ENGINE=gpt4all,
so c04 reproduces as recorded; the default (ollama) is what c02/c05 use.