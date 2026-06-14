# Case — Phishing-Sourced Card Tested at Subscription Merchant

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q2-077091
- `card_token`: TKN-30e2...c91b
- `merchant_id`: MRC-saas-trial-2204
- `channel`: CNP (web checkout)
- `amount`: 1.00 USD
- `timestamp`: 2026-05-19T22:01:09Z
- `device_fingerprint`: DEV-6f4a...0c44
- `ip_country`: BR
- `billing_country`: US (purported)
- `shipping_country`: n/a (digital good)

## Scorer output
- `score`: 0.68
- `reason_codes`: [`cvv_fail`, `geo_mismatch`, `new_device`, `velocity_high`]
- `model_version`: scorer-2026.05.0
- `decision`: `review`

## Analyst investigation
The Transaction's `cvv_fail` plus `geo_mismatch` plus `new_device` combination is the textbook strong-signal stack for a CNP card-testing attempt. Reviewed the broader window: 84 attempts on `MRC-saas-trial-2204` from the same `device_fingerprint` in the preceding hour, 79 of them declined; only 5 approved, all at the USD 1.00 trial-authorization amount.

The targeted `card_token` values had no common BIN pattern, ruling out BIN attack — this was a purchased-batch card-testing pattern instead. Industry sharing flagged a phishing campaign two days prior that targeted users of a popular Brazilian financial app and harvested card credentials; the pattern matches.

Issuer for the present `card_token` had not yet flagged the card as compromised when the Transaction arrived.

## Disposition
- `recommendation`: block
- `confidence`: high
- `cited_sources`: [`typologies/card-testing.md`, `typologies/phishing-driven-fraud.md`, `reason_codes/mc-4863-cnp-no-auth.md`, `glossary.md#cvv_fail`, `glossary.md#velocity_high`, `glossary.md#geo_mismatch`, `glossary.md#new_device`, `policies/case-disposition-guidelines.md`]
- `rationale`: every reason code in the strong-signal stack fired together; the burst pattern at the merchant corroborates the typology; the upstream phishing context explains the source. Releasing the small approvals would seed the attacker's validated-card list for downstream use. The trial-signup amount makes the per-Transaction loss tiny but the secondary loss — once those cards are used elsewhere — is the real cost.

## Candidate Rule proposed
Deny on `MRC-saas-trial-2204` when (`cvv_fail` AND `geo_mismatch` AND `velocity_high` from same device in 10 minutes ≥ 20 attempts). Notify the upstream issuer's risk team about the targeted BINs in the cluster. Forwarded to Daniel.

## Outcome (recorded after disposition)
Blocked at decision time. Subsequent attempts from the same `device_fingerprint` were blocked under the rule. Two chargebacks arrived two weeks later on previously-released Transactions in adjacent merchants in the cluster, confirming the typology fit. The Rule was promoted from review to enforced after a one-week observation window with no false positives detected.
