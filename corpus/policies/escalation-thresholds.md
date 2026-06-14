# Policy — Escalation Thresholds

> Synthetic operational playbook. Thresholds are illustrative and pending Daniel's ratification (AP-4).

## Purpose
Define when a Case must be escalated from a first-tier analyst to a senior analyst, the fraud-operations lead, or an external party (issuer, law enforcement, legal). Escalation is not the same as a high Score; it is a determination that the Case exceeds the first-tier scope.

## When to escalate to a senior analyst
- Any Case with `amount` ≥ USD 5,000.
- Any Case where the analyst's recommended Disposition is `block` but the cited evidence is thin (low cross-reference, no prior chargeback history on the `card_token` or `device_fingerprint`).
- Any Case that involves an account previously flagged for retention by the merchant's customer-success team.

## When to escalate to fraud-operations lead
- Cases that fit an emerging pattern not yet covered by an existing Rule, and that pattern crosses three or more Cases in 24 hours.
- Cases where the senior analyst's Disposition disagrees with the Decision Engine's automatic outcome and the customer-impact implications are material.
- Cases that involve potential law-enforcement reporting under BSA/AML thresholds (see `regulatory-hold-procedure.md`).

## When to involve the issuer
- A confirmed cross-merchant pattern on a specific BIN range, indicating issuer-specific exposure.
- A coordinated campaign apparently targeting a single issuer's cardholders.
- A request from the issuer for context on a chargeback already filed.

## When to involve legal
- Any Case that raises a privacy-rights request (LGPD / GDPR) — `lgpd-data-handling-summary.md` and `gdpr-fraud-decisions-summary.md` cover the timeline obligations.
- Any Case where law-enforcement contact has occurred or is anticipated.

## Out of scope
- Routine analyst-to-senior handoffs for aging Cases are governed by `review-queue-sla.md`, not by this policy.
