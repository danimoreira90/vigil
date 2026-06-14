# Policy — Regulatory Hold Procedure

> Synthetic operational playbook. Pending legal review.

## Purpose
Define the process for placing a regulatory hold on a Transaction, account, or related Cases when a Case triggers anti-money-laundering, sanctions, or law-enforcement obligations. Distinct from a fraud `block`: a regulatory hold restricts action because the law requires preservation of evidence and process, not because the Decision Engine has determined fraud.

## When a regulatory hold applies
- A Case meets a structuring pattern that may require a Suspicious Activity Report under BSA/AML (see `bsa-aml-sar-summary.md`).
- A Case involves a sanctioned party or a known suspect listed by relevant authorities.
- A law-enforcement preservation request has been received.
- Internal counsel directs preservation in anticipation of a regulatory inquiry.

## Hold actions
- The `card_token` and account are flagged in the case store; further Transactions on the same `card_token` are routed to `review` regardless of Score, pending hold review.
- All evidence (masked Transaction snapshots, Scorer outputs, analyst notes) is preserved in immutable form. Deletion routines (LGPD / GDPR) are paused for the held records pending counsel guidance.
- The customer-facing communication does not state that a regulatory hold is in place; standard "additional verification required" messaging applies. Tipping off the subject is itself a regulatory violation in many jurisdictions.

## Hold release
- Holds release only on counsel's instruction. The release timestamp and authorizing party are recorded.
- A released hold does not by itself rehabilitate the underlying Case; the Disposition still owes a recommendation on fraud.

## Out of scope
- The substantive decision to file a Suspicious Activity Report or comply with a subpoena is counsel's, not the analyst's.
- Routine Case escalations to legal that do not require a hold follow `escalation-thresholds.md`.
