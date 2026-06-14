# Policy — Review Queue SLA

> Synthetic operational playbook. The thresholds below are illustrative and pending Daniel's risk-policy ratification (AP-4).

## Purpose
Define how quickly the analyst (System 2) must reach a Disposition on a Case routed to the `review` queue by the Decision Engine. Latency in this queue is not the System 1 latency budget — those budgets are different problems — but it is a real customer-experience and loss-exposure budget.

## Target service levels
- A Case below USD 250 in `amount` must reach Disposition within 4 business hours.
- A Case at or above USD 250 must reach Disposition within 1 business hour.
- A Case at or above USD 5,000 must reach Disposition within 15 minutes and may be auto-routed to a senior analyst.
- A Case carrying `chargeback_history` on the `card_token` or customer account must reach Disposition within 30 minutes regardless of amount.

## Aging Cases
- A Case in `review` for more than 2× the target SLA is escalated automatically to a senior analyst.
- A Case in `review` for more than 4× the target SLA without Disposition triggers a customer-experience review — at some point not deciding is the worst Decision.

## Reporting
- Daily report: count of Cases by tier, percent within SLA, median time to Disposition, worst case.
- Weekly report: SLA misses by typology and by merchant; feeds into Rule and threshold review.

## Out of scope
- The latency budget for the Scorer (System 1) is a separate fitness function (HR-7).
- This policy is about the review queue, not about regulatory holds (see `regulatory-hold-procedure.md`).
