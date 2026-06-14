# Case — Friendly Fraud Dispute on Delivered High-Value Goods

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q1-188275
- `card_token`: TKN-2e1a...90c4
- `merchant_id`: MRC-apparel-5102
- `channel`: CNP (web checkout, account purchase)
- `amount`: 428.00 USD
- `timestamp`: 2026-02-10T14:33:02Z
- `device_fingerprint`: DEV-1c3b...77ee
- `ip_country`: US
- `billing_country`: US
- `shipping_country`: US (matches billing)

## Scorer output
- `score`: 0.17
- `reason_codes`: []
- `model_version`: scorer-2026.02.0
- `decision`: `allow`

## Analyst investigation (post-chargeback)
Forty-one days after the Transaction, a chargeback arrived under Visa 13.x consumer-dispute reason ("goods not received").

Retrospective evidence: carrier tracking shows the goods were delivered to the account's shipping address eight days after the order, with a signature captured. The customer account opened the order-confirmation email twice on the day after delivery and once more eleven days after delivery. No prior contact to customer support requesting a refund or reporting non-receipt.

Cross-reference to the `card_token` and customer account: two prior chargebacks against other merchants on the same `card_token` within the preceding six months, both under consumer-dispute reasons, neither against this merchant.

Industry sharing flags this customer's profile as a repeat disputant.

## Disposition
- `recommendation`: review-continue (representment recommended; Label assignment friendly-fraud rather than third-party fraud)
- `confidence`: high
- `cited_sources`: [`typologies/friendly-fraud.md`, `reason_codes/visa-13-consumer-disputes.md`, `policies/chargeback-response-workflow.md`, `glossary.md#chargeback_history`, `policies/case-disposition-guidelines.md`]
- `rationale`: tracking, signature, and post-delivery engagement all establish the cardholder received the goods. The dispute pattern across multiple merchants on the same `card_token` is a friendly-fraud signature. The Label-store assignment for this Transaction is friendly-fraud, not third-party fraud — assigning it to the third-party-fraud bucket would teach the Scorer the wrong lesson and inflate false positives on legitimate post-delivery patterns.

## Candidate Rule proposed
Increase friction (step-up authentication) on Transactions above USD 250 when (`chargeback_history` set on `card_token`). Not a block — a friction. Forwarded to Daniel.

## Outcome (recorded after disposition)
Representment submitted with the compelling-evidence packet. Outcome pending at time of writing. The customer account was flagged with `chargeback_history` and the proposed friction Rule was enabled for the account class as a controlled experiment. Label-store reflects friendly-fraud assignment, not third-party fraud.
