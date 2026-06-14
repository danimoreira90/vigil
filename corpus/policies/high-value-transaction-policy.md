# Policy — High-Value Transaction Handling

> Synthetic operational playbook. Thresholds are illustrative and pending Daniel's ratification (AP-4).

## Purpose
Define how the Decision Engine routes Transactions whose `amount` materially exceeds the customer's or merchant's typical ticket. High value alone is not fraud, but it changes the expected loss per false negative; the policy reflects that.

## Tiered handling
- Transactions ≤ USD 250: standard Scoring path; the Decision Engine's normal allow/review/block thresholds apply.
- Transactions USD 250 to USD 2,500: standard Scoring path, but Cases routed to `review` must reach Disposition within 1 business hour (`review-queue-sla.md`).
- Transactions USD 2,500 to USD 10,000: even a low Score routes to `review` if any of `new_device`, `geo_mismatch`, `new_card_on_account`, or `chargeback_history` is set.
- Transactions ≥ USD 10,000: routed to `review` regardless of Score; require senior-analyst Disposition.

## Authentication considerations
- For Transactions above USD 2,500 the Decision Engine should prefer a step-up authentication step at checkout where the merchant integration supports it. The step-up does not change the Score; it changes the liability and the analyst's evidence basis.

## Velocity exception
- Transactions in the high-value tier that follow other high-value Transactions from the same `card_token` within a 24-hour window are treated as a velocity-attack candidate even when the individual Score is benign.

## Out of scope
- Auto-block at the high-value tier is an AP-4 decision pending Daniel's risk-appetite call; until then, the policy errs toward `review` rather than `block`.
- Refund and chargeback handling for high-value Transactions is covered in `chargeback-response-workflow.md`.
