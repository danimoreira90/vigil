# Vigil Reason-Code Glossary

> Vigil's own reason codes — emitted by the Scorer (System 1) and consumed by the analyst (System 2). One H2 per code so a citation like `glossary.md#velocity_high` resolves to a single chunk. Each entry: plain meaning + the action the analyst should consider, never the action the system takes (policy lives in the Decision Engine, AP-2).

## velocity_high
The same `card_token`, `device_fingerprint`, or IP has produced an unusually high number of authorization attempts within a short time window. The threshold is per-merchant (a flash-sale merchant tolerates more bursts than a furniture merchant). Analyst action: look at the decline ratio in the window and at whether the surface is shared across many cards (suggests card testing) or one card hitting many merchants (suggests an attacker validating a single stolen card).

## bin_diversity_high
The same IP or `device_fingerprint` has been used with many distinct issuer BINs in a short window. Strong card-testing signal: a legitimate buyer rarely owns cards from many banks. Analyst action: cross-reference with `velocity_high` and `low_amount_anomaly`; one of the three alone is weak, all three together is decisive.

## low_amount_anomaly
The Transaction amount is well below the merchant's typical ticket — often 10–30% of the median. Classic card-testing signature: the attacker minimizes per-attempt cost while validating a batch. Analyst action: compare the burst's amount distribution against the merchant's normal distribution, not against an absolute floor.

## decline_then_success
A `card_token` or `device_fingerprint` produced multiple declines immediately followed by a successful authorization. Suggests the attacker iterated until something authorized — a higher confidence indicator of bad intent than declines alone. Analyst action: if the successful charge is in the same low-amount range as the declines, treat as a confirmed test hit.

## geo_mismatch
The IP country and the billing country (or, for physical goods, the shipping country) do not match. Real customers travel, so this is a weak signal alone, but is corroborative when paired with `new_device` or `cvv_fail`. Analyst action: check whether the cardholder has prior cross-border activity; first-time mismatch is more suspicious than repeated mismatch.

## new_device
The `device_fingerprint` is being seen for the first time on this `card_token`. Legitimate but worth weighting up when other anomalies are present. Analyst action: weak alone; combine with `geo_mismatch` or `night_hour_activity` to escalate.

## new_card_on_account
A `card_token` is being used for the first time on a customer account. Especially relevant after a recent profile change (shipping address, email, password). Analyst action: check timestamp of the account change relative to the Transaction — change-then-new-card within 24 hours is the account-takeover fingerprint.

## shipping_billing_mismatch
The shipping address country or region differs materially from the billing address. Common in gift purchases but also a freight-forwarder signal. Analyst action: if the shipping address resolves to a known reshipping or freight-forwarder facility, escalate; if to a residential address consistent with a relative's location, weight down.

## cvv_fail
The CVV/CVC check returned a non-match. Issuer policies vary on whether to decline; many still authorize. Analyst action: a hard `cvv_fail` with `new_device` is among the strongest CNP fraud signals and warrants a block recommendation absent strong offsetting evidence.

## avs_partial
Address verification returned a partial match (zip matches, street does not, or vice versa). Common with apartment numbers and international issuers. Analyst action: weak alone; combine with `cvv_fail` or `shipping_billing_mismatch` for material weight.

## amount_anomaly
The Transaction amount is well above the customer's typical ticket on this merchant or in general. Distinct from `low_amount_anomaly` — high-side outlier instead of low-side. Analyst action: cross-reference with `new_device` and channel; a high-side spike at a new device on a CNP channel is a textbook account-takeover signature.

## night_hour_activity
The Transaction landed outside the customer's normal active window (local time). A single late-night charge is unremarkable; a cluster of them at a previously-quiet account is not. Analyst action: pair with `new_device` for a useful account-takeover indicator.

## email_fresh
The email on the account was registered very recently, or has a low reputation score from external feeds. Strong synthetic-identity signal when paired with `avs_partial`. Analyst action: check whether the email pattern matches known disposable-mail providers; freshness alone is not enough.

## device_shared
The same `device_fingerprint` is associated with many distinct customer accounts. Possible legitimate cases exist (family devices, public terminals) but the pattern is also a synthetic-identity-ring and promo-abuse signature. Analyst action: count the distinct accounts and how recently they were created; ten accounts in a week from one device is decisive.

## chargeback_history
The `card_token` or the customer account has at least one prior confirmed-fraud chargeback. The strongest available prior. Analyst action: any new score above the review threshold with `chargeback_history` set should be treated as a block recommendation pending strong counter-evidence; the Decision Engine policy may already auto-block.
