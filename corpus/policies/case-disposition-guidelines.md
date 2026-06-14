# Policy — Case Disposition Guidelines

> Synthetic operational playbook. Defines the shape of a Disposition and the rules every analyst applies before writing one. The shape here is the schema c02 enforces and c05 grounds.

## The Disposition object
Every Disposition records four fields:
- `recommendation`: one of `allow`, `block`, `review-continue`. Never `decline` — `block` is the Vigil term (see `CONTEXT.md`).
- `confidence`: one of `low`, `medium`, `high`. Reflects the analyst's certainty given the evidence, not the Score.
- `cited_sources`: a list of corpus paths the Disposition rests on (typology, reason code, policy, prior synthetic Case). Every claim of fact in `rationale` must trace back to one of these paths.
- `rationale`: short prose explaining what the analyst saw, which signals corroborated which, and why the recommendation follows. The rationale should be readable by a non-analyst (auditor, regulator).

## Hard rules for every Disposition
- Cite at least one source for every Disposition. Free-form opinion without citation is not a permitted Disposition under the grounding requirement.
- Use the domain language exactly as `CONTEXT.md` defines it: `Transaction`, `Score`, `Reason Code`, `Case`, `Label`, `card_token`, `device_fingerprint`. Do not invent synonyms.
- Reference masked tokens only; raw PAN, CVV, or PII may not appear in the rationale (HR-3).
- A `block` recommendation must list at least one Reason Code that, together with the cited typology or reason-code reference, supports the recommendation. A bare `block` is a defect (HR-5 parallel).

## Confidence calibration
- `high`: at least two independent strong reason codes, plus a corroborating prior Case or chargeback history, plus a clear typology fit.
- `medium`: one strong reason code plus corroborating context, or multiple weak reason codes that combine cleanly with a typology.
- `low`: signal is suggestive but the evidence does not rule out a legitimate alternative explanation. A `low`-confidence `block` is rare and should be escalated.

## Out of scope
- Threshold tuning that maps `confidence` to Decision Engine policy is owned by the Decision Engine team (AP-2 / AP-4), not the analyst.
- The exact prompt template the analyst LLM uses lives in c02's notebook; this policy defines the schema, not the prompt.
