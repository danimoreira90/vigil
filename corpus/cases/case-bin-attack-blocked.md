# Case — BIN Attack on Subscription Merchant

> Synthetic. All identifiers are masked tokens; no real cardholder, issuer, or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q1-309442
- `card_token`: TKN-4f01...88aa (one of many in a tight numeric neighborhood)
- `merchant_id`: MRC-saas-trial-2204
- `channel`: CNP (web checkout, trial signup flow)
- `amount`: 1.00 USD (authorization for trial, not capture)
- `timestamp`: 2026-03-22T06:08:54Z
- `device_fingerprint`: DEV-c7e2...0193
- `ip_country`: SG
- `billing_country`: varies across the burst (purported)

## Scorer output
- `score`: 0.74
- `reason_codes`: [`velocity_high`, `decline_then_success`, `low_amount_anomaly`]
- `model_version`: scorer-2026.03.0
- `decision`: `review`

## Analyst investigation
Reviewed the surrounding 15-minute window on `MRC-saas-trial-2204`. 612 authorization attempts arrived from three IP addresses in the same hosting-provider ASN. The `card_token` values clustered tightly within a single BIN range from one issuer, with attempts walking the candidate numbers sequentially — a BIN walk rather than a purchased-batch testing pattern. The decline ratio was 87%; the successful authorizations clustered in the last third of the window, suggesting the attacker found a valid check-digit range.

Cross-checked the targeted BIN with the issuer's published BIN catalog: the range corresponds to a recently-issued debit-card program with a narrow numeric span, consistent with the attacker treating it as a guessable target.

The merchant's trial signup flow does not require a CVV match for the USD 1.00 authorization, lowering the attacker's per-attempt cost.

## Disposition
- `recommendation`: block
- `confidence`: high
- `cited_sources`: [`typologies/bin-attack.md`, `typologies/card-testing.md`, `glossary.md#velocity_high`, `glossary.md#decline_then_success`, `policies/case-disposition-guidelines.md`]
- `rationale`: single-BIN burst with sequential `card_token` neighborhood is a BIN walk against a vulnerable trial-signup flow that does not require CVV. The IP cluster and ASN identity rule out distributed legitimate demand. Releasing approvals from this burst would seed the attacker's validated-card list at the issuer's expense and the merchant's eventual chargeback expense.

## Candidate Rule proposed
On `MRC-saas-trial-2204`-class trial-signup flows: deny when (`velocity_high` from same IP in 15 minutes >= 100 attempts) AND (single BIN >= 80% of attempts). Coordinate with issuer to notify them of the targeted BIN range. Forwarded to Daniel.

## Outcome (recorded after disposition)
Blocked at decision time. IP cluster added to the merchant's cool-down list. Issuer notified through the acquirer's risk-coordination channel. No subsequent chargebacks observed on the burst's approvals because they were reversed before capture.
