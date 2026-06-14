# Case — CNP Velocity Burst on Digital-Goods Merchant

> Synthetic. All identifiers are masked tokens; no real cardholder, account, or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q2-018734
- `card_token`: TKN-d4a1...e9c2
- `merchant_id`: MRC-digital-7821
- `channel`: CNP (web checkout)
- `amount`: 4.99 USD
- `timestamp`: 2026-04-17T02:14:08Z
- `device_fingerprint`: DEV-9f2b...11a8
- `ip_country`: NL
- `billing_country`: US
- `shipping_country`: n/a (digital good)

## Scorer output
- `score`: 0.81
- `reason_codes`: [`velocity_high`, `bin_diversity_high`, `low_amount_anomaly`, `geo_mismatch`]
- `model_version`: scorer-2026.04.0
- `decision`: `review` — Decision Engine routed to the queue (score above review threshold, below auto-block threshold). Policy lives in the Decision Engine, not the Scorer (AP-2).

## Analyst investigation
Reviewed the surrounding 30-minute window on `MRC-digital-7821`. Forty-one authorization attempts came from a small set of three `device_fingerprint` values and two IP addresses in the same ASN. Twenty-eight attempts were declined; the present Transaction was the seventh of thirteen approvals. All approvals fell between 3.99 and 5.49 USD, well below the merchant's median ticket of 19.95 USD. The card tokens spanned twenty-two distinct BINs across four issuers, consistent with a purchased card batch being validated rather than legitimate concentrated demand.

Cross-checked the past 14 days: the same `device_fingerprint` appeared in two prior Cases resolved as confirmed-fraud after Visa 10.4 chargebacks. No legitimate purchases by this `card_token` exist in the merchant's history.

The 3-D Secure outcome on this Transaction was a frictionless flow with no step-up challenge; under Visa 10.4 treatment the merchant remains exposed if the Transaction is released.

## Disposition
- `recommendation`: block this Transaction; refund if already settled.
- `confidence`: high.
- `cited_sources`: [`typologies/card-testing.md`, `reason_codes/visa-10-4-card-absent.md`, `glossary.md#velocity_high`].
- `rationale`: signals match the card-testing typology cleanly — low-amount burst, high BIN diversity from a tight IP and device cluster, decline-then-success pattern, and prior confirmed-fraud on the same `device_fingerprint`. Authentication did not shift liability. The expected loss from releasing exceeds the expected friction of blocking on this merchant class.

## Candidate Rule proposed
On digital-goods merchants similar to `MRC-digital-7821`: deny when (`velocity_high` AND `bin_diversity_high` from the same `device_fingerprint` within a 30-minute window >= 10 attempts) AND (amount below merchant median × 0.5). Forwarded to Daniel for review and threshold tuning. The Scorer remains policy-agnostic; the Rule lives in `rules/` (AP-2).

## Outcome (recorded after disposition)
Blocked at decision time. Two days later a Visa 10.4 chargeback was filed on a sibling Transaction approved from the same `device_fingerprint` prior to the Rule landing — confirming the typology fit and the expected value of the proposed Rule.
