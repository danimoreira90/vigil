# Case — Account Takeover with Last-Minute Shipping Change

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q1-227510
- `card_token`: TKN-7b2c...4d11
- `merchant_id`: MRC-electronics-3309
- `channel`: CNP (web checkout)
- `amount`: 1,849.00 USD
- `timestamp`: 2026-02-04T23:51:47Z
- `device_fingerprint`: DEV-aa17...c803
- `ip_country`: US (East Coast)
- `billing_country`: US (West Coast)
- `shipping_country`: US (different state from billing, address changed 28 minutes before order)

## Scorer output
- `score`: 0.62
- `reason_codes`: [`amount_anomaly`, `new_device`, `night_hour_activity`, `shipping_billing_mismatch`]
- `model_version`: scorer-2026.02.0
- `decision`: `review`

## Analyst investigation
The customer account had a stable two-year purchase history on `MRC-electronics-3309`, predominantly daytime activity from a consistent `device_fingerprint` and IP range. Twenty-eight minutes before the Transaction, the account's shipping address was changed to a new address in a different state. Eleven minutes before the Transaction, a previously-unseen `device_fingerprint` logged in successfully. The Transaction itself is for a single high-value consumer electronics item, well above the customer's median ticket.

Cross-checked recent phishing-campaign reports from industry sharing: a campaign targeting customers of a popular SaaS product had been active in the preceding 72 hours; the customer's email matches the target pattern in plausible-victim ways.

Outbound contact to the cardholder via the merchant's confirmed phone-on-file (not the recently-added email) reached the cardholder, who confirmed they had not placed the order, had not changed the shipping address, and had recently received a phishing email matching the campaign description.

## Disposition
- `recommendation`: block
- `confidence`: high
- `cited_sources`: [`typologies/account-takeover.md`, `typologies/phishing-driven-fraud.md`, `glossary.md#new_device`, `glossary.md#amount_anomaly`, `glossary.md#shipping_billing_mismatch`, `policies/case-disposition-guidelines.md`]
- `rationale`: profile change (shipping address + new device login) followed within an hour by a Transaction at the customer's amount-anomaly tier is the textbook account-takeover signature. The independently confirmed phishing campaign and the cardholder's own statement remove ambiguity. The merchant's checkout did not invoke step-up authentication on this Transaction; the merchant retains the loss if released.

## Candidate Rule proposed
On categories above USD 1,000 ticket: require step-up authentication when (profile change to shipping address within 60 minutes) AND (`new_device`). Forwarded to Daniel for threshold tuning.

## Outcome (recorded after disposition)
Blocked at decision time. Account placed in protective hold; cardholder rotated credentials via the merchant's recovery flow. No chargeback filed (because the Transaction was blocked); the merchant's exposure was prevented.
