# Case — Promo Abuse via Throwaway Accounts

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q2-066903
- `card_token`: TKN-bc91...3f2e (one of many on the same `device_fingerprint`)
- `merchant_id`: MRC-saas-trial-2204
- `channel`: CNP (trial signup conversion, USD 0.99 auth)
- `amount`: 0.99 USD
- `timestamp`: 2026-05-08T03:17:55Z
- `device_fingerprint`: DEV-7711...22cc
- `ip_country`: US (residential proxy ASN)
- `billing_country`: US (purported)
- `shipping_country`: n/a (digital good)

## Scorer output
- `score`: 0.45
- `reason_codes`: [`device_shared`, `email_fresh`, `low_amount_anomaly`]
- `model_version`: scorer-2026.05.0
- `decision`: `review`

## Analyst investigation
The same `device_fingerprint` had completed the new-account incentive flow on 31 accounts within a rolling 14-day window. Each account's email used a different randomized prefix on the same disposable-mail provider domain. Each account had immediately claimed a USD 25 referral credit and a one-month free trial extension worth USD 18, then ceased activity.

None of the accounts had any usage of the underlying product beyond the actions needed to qualify for the credit. The `card_token` values varied across accounts but two of them had been used on three accounts each, both prepaid debit cards from a provider associated with anonymity-tolerant flows.

The actual loss per individual account is small; the cumulative incentive payout was substantial.

## Disposition
- `recommendation`: block (the promo, not necessarily the underlying Transaction)
- `confidence`: high
- `cited_sources`: [`typologies/promo-abuse.md`, `glossary.md#device_shared`, `glossary.md#email_fresh`, `policies/case-disposition-guidelines.md`]
- `rationale`: 31 accounts on one `device_fingerprint` redeeming the same incentive flow in 14 days is decisive for promo abuse. The Transactions themselves are likely valid authorizations; what should be blocked is the *incentive payout*, not the Transaction — refusing the Transaction outright would harm a hypothetical legitimate buyer. The Decision Engine's incentive-payout cap should apply per `device_fingerprint`, separate from per-Transaction Score logic.

## Candidate Rule proposed
Deny the new-account incentive payout when (`device_shared` redemption count ≥ 3 in 30 days), preserving the Transaction allow path. Coordinate with marketing to determine whether the underlying accounts should be deactivated or merely barred from future incentives. Forwarded to Daniel.

## Outcome (recorded after disposition)
Incentive denied at decision time; Transaction allowed. No chargebacks resulted; the abuser stopped using the device against this merchant. The Rule was promoted from experiment to default after one month of observation. Net incentive savings exceeded the rule's false-positive cost by a comfortable margin.
