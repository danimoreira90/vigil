# Sentinela — Project CLAUDE.md

**Version:** 0.1 (DRAFT — pending role-taxonomy confirmation)
**Date:** 2026-06-06
**Project:** Sentinela (real-time card / payment fraud detection)
**Owner:** Daniel Moreira
**Repo:** TODO — github.com/danimoreira90/sentinela

> Replace the codename `Sentinela` if you prefer another.

---

## Inheritance

This project **extends** the global agentic engineering framework in `~/.claude/CLAUDE.md` (Claude Swarm v2.0), exactly as Nexus does. Same decision (B — Estende puro).

**You inherit, fully:** the 13 Core Rules, the 4 frameworks (12-Factor, CAP, C4, ADR), the 3 methodologies (TDD, EDD, SDD), the 17 Tier 2/3 agents, the 8 rules, the personal skills.

**This file adds:** project identity, stack, fraud-specific hard rules, the ML branch-role system, protected paths for model/data artifacts, agent routing, and known gaps.

**Read this file FIRST, then `~/.claude/CLAUDE.md`. Project rules below override global rules on conflict.**

### Key difference from Nexus

EDD is **not** a later sprint here — the whole product is a model. EDD is active day one. The generative-AI gates (`pass@3 >= 0.90`, `pass^3 = 1.00`) do not apply to a classifier; the scorer is gated on an agreed metric target + no-regression + no-leakage (see HR-4, EVAL-RUBRIC).

---

## Project Identity

```yaml
name: Sentinela
type: Real-time fraud detection system
domain: Card / payment fraud (card-not-present focus)
decision_latency_budget: < 200 ms per transaction
pilot_scale: ~1,000 transactions/day
decision_maker: robot first; human review queue added later
label_status: NO labels at start — cold start on rules + anomaly detection
core_pillars:
  - Scoring (model returns fraud probability + reason codes)
  - Decision policy (allow / block / review — owned by the decision engine)
  - Label factory (chargebacks + human review accrue labels over time)
status: bootstrap — manifest + first spec
```

## Stack

```yaml
runtime: python 3.13
package_manager: uv
modeling: scikit-learn + xgboost / lightgbm
serving: TODO — FastAPI scorer (stateless) behind the decision engine
storage: TODO — transaction store + case store + label store
feature_store: TODO
observability: TODO — metrics + drift monitor (Langfuse n/a to a classifier)
tests: pytest
eval: held-out test set + metric harness (see HR-4)
dev_environment:
  os_target: windows 11 (primary), linux/mac (secondary)
  agent_runtime: claude code (run `claude --version` to confirm)
build_data:
  - IEEE-CIS (Vesta): main proving ground (~590k CNP tx, 3.5% fraud, 431 features)
  - Sparkov: readable feature names for feature-engineering practice
  - NOTE: build data is labeled; live system is not — see label_status
```

## Hard Rules (Project-Specific)

Listed by priority. Override global rules where they conflict.

### HR-1 — Manual Commits Only (carries from Daniel's standing preference; overrides Swarm Rule 7 automation)

ALL git commits are executed MANUALLY by Daniel. Agents may show `git status` / `git diff --cached` and suggest a commit message as plain text. Forbidden: `git add` / `commit` / `push`, `gh pr create` / `merge`, any hook/script that triggers them. Read-only git (`log`, `diff`, `checkout`, `branch`, `fetch`, `pull`) is fine.

### HR-2 — Test & Eval Integrity (refines inherited anti-cheat; extends Nexus HR-4 to ML)

- CREATE new tests / new eval cases: permitted.
- EDIT existing tests or existing eval cases: forbidden without explicit Daniel approval + `docs/tech-debt.md` entry.
- Forbidden: delete a test, `skip`/`xfail`/`it.only`-equivalents on existing tests, soften an assertion, mock-the-world tautologies.
- Show FULL test and eval output, never paraphrase (Honest Reporting Mandate).

### HR-3 — No Raw Card Data; PII Masked Everywhere (PCI / privacy)

- NEVER log, print, store, or commit a raw card number (PAN) or CVV. Tokens only.
- Mask all PII in logs and in any sample data committed to the repo.
- No real customer data in the repo, ever. Build only on the public datasets above.

### HR-4 — The Held-Out Test Set Is Sacred (data leakage = the ML cheat)

This is anti-cheat for modeling. Violating it fakes a passing state.

- NEVER train or tune on the held-out test set. NEVER inspect it to choose features/thresholds.
- NEVER let target-derived information leak into features (label leakage, look-ahead on time series).
- Train / validation / test split is fixed and **time-based** for fraud (no random shuffling across time).
- Any reported metric MUST come from the untouched test set, with FULL harness output shown.
- Suspected leakage -> STOP and report. Do not "adjust" the split to make a number look good.

### HR-5 — Every Live Decision Must Be Explainable

- Production scoring uses models that can produce reason codes (gradient-boosted trees), not black-box-only.
- Every decision is logged: masked input snapshot, score, decision, reason codes, model/rule version.
- A "block" with no reason code is a defect.

### HR-6 — Deployed Models Are Immutable + Versioned (parallel to Nexus HR-3 migrations)

- A model artifact, once deployed, is never edited in place. New behavior = new versioned artifact.
- Every deployed model has a model card (`docs/model-cards/`) with metrics, training window, known weak spots.

### HR-7 — Latency Budget Is a Fitness Function (Ford)

- An automated test fails the build if scoring exceeds the latency budget (200 ms default).
- Same for any architecture characteristic we commit to (see Architectural Principles).

---

## Architectural Principles (apply, then cite which one in your report)

Decisions of HOW to build follow these. Decisions of WHAT to build and at WHAT RISK are product/risk — not architectural — and go to Daniel (see "When uncertain").

- **AP-1 — The scorer thinks, the decision engine acts.** The model/scoring service is stateless: receives a transaction, returns a score + reason codes. It does NOT decide allow/block, does NOT write to the case or label store. The decision engine (owns policy + thresholds) acts and persists. (Newman: data ownership; Evans: the decision is domain logic.)
- **AP-2 — Fraud policy lives in the decision domain, not the model.** Thresholds, allow/block/review mapping, which reason codes trigger human review = business/risk policy. The model is policy-agnostic by contract — it only scores. (Evans.)
- **AP-3 — Minimize coupling; prefer the reversible.** A threshold change or model swap should be cheap to revert (config / versioned artifact), not a synchronized redeploy. (Ford: evolutionary architecture.)
- **AP-4 — Canonical principle -> agent decides and cites. No canonical answer -> report to Daniel.** If Evans/Ford/Newman/12-Factor agree, apply and proceed. If the choice depends on product vision or risk appetite — it is Daniel's. **The false-positive/false-negative trade-off is an AP-4 decision: report options, do not pick.**

Rationale, examples, study cases: `docs/agentic-engineering/ARCHITECTURE-PRINCIPLES.md` (to be written).

---

## Branch Roles (PROPOSED — confirm before dependent docs are generated)

Roles answer "what type of change is this?" — orthogonal to the inherited Tier system ("who knows how to do this?").

| Role | Branch prefix | When | Invoke (Tier 2 / 3) |
|---|---|---|---|
| `data/*` | `data/<short-name>` | Ingest, clean, label factory | orchestrator -> builder -> db-architect -> lang-python + security-guardian (PII) |
| `model/*` | `model/<short-name>` | Train, tune, evaluate models (EDD) | orchestrator -> planner -> builder -> ai-ml-engineer + lang-python |
| `rules/*` | `rules/<short-name>` | Fraud rules + thresholds (policy) | orchestrator -> planner -> builder + security-guardian |
| `serving/*` | `serving/<short-name>` | Real-time scorer + latency | orchestrator -> backend-expert -> cloud-engineer + security-guardian |
| `quality/*` | `quality/<short-name>` | Tests, docs, ADRs, eval-set curation | orchestrator -> qa-champion -> doc-engineer |
| `infra/*` | `infra/<short-name>` | CI/CD, deploy, drift monitoring | orchestrator -> devops-engineer -> cloud-engineer + security-guardian |
| `bugfix/*` | `bugfix/issue-<n>-<short>` | Pointed fix referencing an issue | orchestrator -> planner -> builder + qa-champion |
| `chore/*` | `chore/<short-name>` | Maintenance (deps, configs) | orchestrator -> builder (lightweight) |

> NOTE: there is no `feature/*` role. In ML, "feature" = model input variable (see CONTEXT.md). New model capability lives under `model/*`; reserving the word avoids the clash.

Detail: `docs/agentic-engineering/ROLES.md` (to be written after this taxonomy is confirmed).

---

## Protected Paths (Project-Specific summary)

READ-ONLY (never edit):
```
data/test/**                 # held-out test set — HR-4, sacred
data/raw/**                  # immutable source dumps
models/deployed/**           # deployed artifacts — HR-6, immutable
docs/adr/0*.md               # approved ADRs immutable
.env, .env.*                 # never read content, never commit
**/test_*.py                 # CREATE permitted; EDIT existing forbidden (HR-2)
tests/evals/**               # eval cases — CREATE permitted; EDIT existing forbidden (HR-2/HR-4)
```

REVIEW-REQUIRED (Daniel reads diff before commit):
```
pyproject.toml, uv.lock      # new RUNTIME / latency-path deps require ADR; dev/tooling deps (pandas, pytest, kaggle) need only Daniel diff review
rules/thresholds.*           # threshold changes are risk decisions (AP-4)
config/serving.*             # latency / serving config
```

FREE (within role scope):
```
src/**/*.py (NOT test_*)     # scorer, features, decision engine
data/processed/**            # derived, reproducible data
docs/specs/**, docs/decisions/**, docs/agentic-engineering/**
scripts/**                   # one-off tools (inspectors, ETL probes); writable only on data/* and quality/* branches
```

Full table: `docs/agentic-engineering/PROTECTED-PATHS.md` (to be written).

---

## Skills / Agents Available (inherited from Claude Swarm v2.0)

```
Skills:  anti-cheat  blueprint  eval-driven-development (CENTRAL here)  memory-management
         spec-driven-dev  system-design  twelve-factor
Tier 2:  orchestrator architect planner builder qa-champion security-guardian
         db-architect backend-expert cloud-engineer devops-engineer
         ai-ml-engineer (TRIGGER ALWAYS — this is an ML project) doc-engineer git-master
Tier 3:  lang-python (primary)  tool-docker
Rules:   anti-cheat-discipline  coding-standards  edd-discipline  git-conventions
         security  tdd-discipline  testing-requirements  verification-discipline
```

`frontend-expert` and `lang-typescript` are unlikely to fire (no web UI in MVP).

---

## Known Gaps in Inherited Claude Swarm v2.0

Same gaps as documented in Nexus (slash commands, several referenced skills, MCP config, hooks — all NOT IMPLEMENTED as of the Nexus snapshot). Behavior on encountering a gap: acknowledge it, apply the intent manually, do not improvise silently. Verify current machine state with `claude --version`, `claude mcp list`, and inspect `~/.claude/`. Track in `docs/tech-debt.md`.

---

## Quick Reference for Agents

```
Before any task:
  1. Read this file
  2. Read ~/.claude/CLAUDE.md (Claude Swarm v2.0)
  3. Read CONTEXT.md (fraud domain glossary)
  4. Read docs/agentic-engineering/ROLES.md (find your Role)
  5. Map the codebase before acting

Before any commit (DANIEL ONLY):
  1. Show git diff --cached (full)
  2. Run tests + eval harness; show FULL output (Honest Reporting Mandate)
  3. Confirm no test-set contact (HR-4) and no raw PAN/PII (HR-3)
  4. Daniel runs git add / commit / push manually (HR-1)

When uncertain:
  Stop. Report. List 2-3 options with trade-offs. Wait for Daniel.
  (The FP/FN dial is one of these — AP-4.)
```

---

## Pointers

- Domain glossary: `CONTEXT.md`
- Multi-model agent rules: `AGENTS.md` (to be written)
- Agentic engineering details: `docs/agentic-engineering/` (to be written)
- ADRs: `docs/adr/`
- Tech debt: `docs/tech-debt.md`
- Model cards: `docs/model-cards/`
- Code simplicity (binding): `CODE-SIMPLICITY.md`