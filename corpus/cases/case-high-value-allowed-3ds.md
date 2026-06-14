# Case — High-Value Transaction Allowed After 3-D Secure Success

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q2-095274
- `card_token`: TKN-08a3...d7b9
- `merchant_id`: MRC-electronics-3309
- `channel`: CNP (web checkout)
- `amount`: 4,890.00 USD
- `timestamp`: 2026-06-01T15:11:42Z
- `device_fingerprint`: DEV-1e08...4a55 (new on account)
- `ip_country`: FR
- `billing_country`: FR
- `shipping_country`: FR (matches billing)

## Scorer output
- `score`: 0.48
- `reason_codes`: [`amount_anomaly`, `new_device`]
- `model_version`: scorer-2026.06.0
- `decision`: `review` (above review threshold for high-value tier per policy)

## Analyst investigation
The customer account has six months of consistent activity on `MRC-electronics-3309`, with a median ticket of USD 280. The present Transaction is well above that median (`amount_anomaly`), placed from a `device_fingerprint` not previously seen on this account (`new_device`). Standard tier-based review per the high-value policy.

The merchant's checkout invoked 3-D Secure 2.x. The issuer's risk-based authentication challenged the cardholder; the step-up challenge succeeded with a successful biometric outcome on the cardholder's registered device. Time between Transaction submission and 3-D Secure outcome is consistent with a human user, not a session-hijacking script. No account profile changes in the preceding 30 days. No `chargeback_history` on the `card_token` or account.

Outbound contact to the cardholder via the merchant's confirmed phone-on-file: cardholder confirmed they were purchasing a piece of professional equipment, had borrowed a partner's tablet for the order (explaining the `new_device`), and were not phishing victims.

## Disposition
- `recommendation`: allow
- `confidence`: high
- `cited_sources`: [`policies/high-value-transaction-policy.md`, `regulatory/psd2-sca-summary.md`, `glossary.md#new_device`, `glossary.md#amount_anomaly`, `policies/case-disposition-guidelines.md`]
- `rationale`: the reason codes that triggered review have benign explanations confirmed by the cardholder. The 3-D Secure outcome shifts liability to the issuer under the PSD2 regime, so even in the small remaining probability of fraud the merchant is not the loss-bearer. Blocking a confirmed legitimate Transaction at this amount is a real customer-experience cost; the policy correctly routed the Case to review, and the review correctly resolved to allow.

## Candidate Rule proposed
None. The existing high-value policy worked as intended. This Case is recorded as a non-fraud high-tier review example to balance the training and few-shot example pool — without negative examples, the analyst LLM in c02 will skew toward `block` on amount-anomaly Cases.

## Outcome (recorded after disposition)
Allowed at decision time. No chargeback filed in the subsequent 90-day window. Customer completed two further purchases on the merchant within 60 days, both from the original `device_fingerprint`, neither triggering review.
