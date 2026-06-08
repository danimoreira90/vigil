# Sentinela — Domain Glossary (CONTEXT.md)

**Status:** Draft v0.1 | **Date:** 2026-06-06 | **Owner:** Daniel

> Canonical domain language for the fraud detection codebase. Variables, functions, file names, conversations, and agent-generated text MUST use these terms.
>
> When you catch yourself using vague or overloaded wording, stop and add the term here. The next session is sharper.

---

## Core entities

### Transaction
The unit we score. A single payment attempt. Fields of note: `transaction_id`, `amount`, `timestamp`, `card_token` (NEVER raw PAN — HR-3), `merchant_id`, `channel` (CNP / CP), `device`, `geo`. Immutable once recorded.

### Score
The model's output for one Transaction: a fraud probability in `[0, 1]` plus **reason codes**. A Score is not a decision. The scorer produces it; the decision engine acts on it (AP-1).

### Reason Code
An explainable factor behind a Score / Decision (e.g. `velocity_high`, `geo_mismatch`, `new_device`). Required on every live decision (HR-5). Drives regulatory explainability and the review queue.

### Decision
The action taken on a Transaction: `allow`, `block`, or `review`. Made by the **Decision Engine**, never by the model (AP-1, AP-2). Logged with masked input, score, reason codes, and model/rule version.

### Decision Engine
The component that owns fraud policy: thresholds, the score-to-decision mapping, which reason codes route to human review. Policy-bearing, domain-aware. Acts and persists.

### Scorer
The stateless model service. Receives a Transaction, returns a Score + reason codes. Knows nothing about thresholds or policy (AP-2). "The scorer thinks."

### Rule
An explicit, readable if-then policy (e.g. "new card + amount > X + odd hour + shipping != billing country -> flag"). Lives in `rules/`. Auditable. The day-one cold-start mechanism alongside anomaly detection.

### Feature (a.k.a. Signal)
A model input variable derived from a Transaction and its context (e.g. `amount_zscore`, `txns_last_hour`, `distance_from_home`). **Reserved term** — "feature" always means this, never a product capability or a git branch.

### Case (Review Case)
A Transaction routed to the human review queue. Has `status`, `assigned_to`, `resolution`. A resolved Case produces a Label.

### Label
A confirmed verdict on a Transaction: `fraud` or `clean`. Sources: chargebacks and resolved review Cases. The training signal we do not have at start (cold start) and accrue over time via the Label Factory.

### Chargeback
A late-arriving confirmed-fraud signal from the payment network / issuer. Primary label source. Note the lag — a Transaction's true Label may land weeks later.

---

## System concepts

### Label Factory
The pipeline that turns chargebacks and resolved Cases into Labels and writes them to the label store. Runs from day one (HR philosophy: without it, the system stays blind forever).

### Cold Start
The label-less initial state. Detection runs on Rules + anomaly detection until enough Labels accrue to train a supervised Scorer.

### Held-Out Test Set
The fixed, time-based, untouched slice of data used only for final metric reporting. Sacred (HR-4). Never trained on, tuned on, or inspected for feature/threshold choices.

### Time-Based Split
Train / validation / test split ordered by time, never randomly shuffled. Random shuffling leaks the future into the past for fraud and inflates metrics.

### Data Leakage
Any path by which target-derived or future information reaches a Feature or the model during training. The ML equivalent of editing the test to pass (HR-4 / anti-cheat).

### Drift
Degradation of model quality over time as fraud tactics change. Watched by the drift monitor; triggers retraining.

### Capability Eval
A defined check that a model meets its agreed metric target before shipping. For a classifier the gate is a **metric target** (e.g. recall at a fixed false-positive rate, or PR-AUC >= baseline) — NOT the generative `pass@3`.

### Regression Eval
A check that a model change does not drop previously-passing metrics on the held-out set. No-regression is a ship gate.

### Decision Latency
Time from Transaction arrival to Decision. Budget: < 200 ms. Enforced as a fitness function (HR-7).

---

## Build data (not live data)

| Dataset | Use | Note |
|---|---|---|
| IEEE-CIS (Vesta) | Main proving ground | ~590k CNP tx, 3.5% fraud, 431 features; feature names masked |
| Sparkov | Feature-engineering practice | Readable feature names; ~0.5% fraud; time-ranged 2019-2020 |

Build data is **labeled**; the live system is **not** (Cold Start). Models built on these prove the pipeline; they are not the live model.

---

## Forbidden / fuzzy / overloaded terms

Avoid the left column; use the right.

| Avoid | Use instead |
|---|---|
| "feature" for a product capability | "capability" — "feature" is a model input only |
| "charge" / "payment" loosely | "Transaction" |
| "risk" as a noun for the number | "Score" (0-1) or "Reason Code" |
| "decline" | "block" (one of allow/block/review) |
| "fraud" unqualified | "Label = fraud" (confirmed) vs "flagged" (suspected, not confirmed) |
| "the model decides" | "the Scorer scores; the Decision Engine decides" (AP-1) |
| "alert" | "Case" (in the review queue) or "flag" (a rule firing) |
| "test data" ambiguously | "held-out test set" (sacred) vs "validation set" (tuning) |
| "accuracy" | name the real metric (recall@FPR, PR-AUC) — accuracy is meaningless at 0.5% fraud |

---

## To resolve (open questions)

- [ ] The FP/FN trade-off target — Daniel's call (AP-4). Default "balanced" until set.
- [ ] Auto-block vs review-only at launch — product/risk decision (AP-4).
- [ ] Storage choices for transaction / case / label stores.
- [ ] Retrain cadence and drift thresholds.
- [ ] Build vs buy baseline (e.g. a vendor scorer underneath the custom layer).

---

## Changelog

- **2026-06-06** — Initial draft. Core entities, system concepts, build data, forbidden terms.
