# Case — Refund Fraud Pattern on Returned-Empty Packages

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q1-251449
- `card_token`: TKN-44b0...e7c1
- `merchant_id`: MRC-electronics-3309
- `channel`: CNP (web checkout)
- `amount`: 989.00 USD
- `timestamp`: 2026-03-09T17:45:30Z
- `device_fingerprint`: DEV-2d77...8e90
- `ip_country`: US
- `billing_country`: US
- `shipping_country`: US (matches billing)

## Scorer output
- `score`: 0.19
- `reason_codes`: []
- `model_version`: scorer-2026.03.0
- `decision`: `allow`

## Analyst investigation (post-refund-request)
Twenty days after the Transaction, the customer requested a refund through the merchant's return-merchandise-authorization flow, stating that the item was defective. The carrier-tracked return arrived 7 days later; the merchant's receiving department documented that the package contained packing material and a brick of comparable weight rather than the original product.

Cross-checked the customer account history: this was the third return request in 90 days on the same account, the second to allege defect on arrival. The first return was processed without inspection per the merchant's at-the-time policy; the inspection on the second return revealed a substituted item; the third (this Case) confirmed the pattern.

The original Transaction scored low because no third-party-fraud signal was present. The fraud was post-Transaction, against the refund policy.

## Disposition
- `recommendation`: review-continue (deny the refund; do not chargeback the Transaction; flag the account)
- `confidence`: high
- `cited_sources`: [`typologies/refund-fraud.md`, `policies/chargeback-response-workflow.md`, `policies/case-disposition-guidelines.md`]
- `rationale`: the receiving department's documented evidence establishes the return was a substituted shipment, not the original product. The pattern across three return requests is decisive. The Transaction itself is valid; the refund request is the fraud. Denying the refund is the correct action; treating the Transaction as third-party fraud and assigning a fraud Label would be wrong and would teach the Scorer noise.

## Candidate Rule proposed
Flag accounts for support review on refund requests when (return-request count in 90 days ≥ 2 AND one prior return alleged defect on arrival). The Decision Engine's policy here is on the refund flow, not the Score; route to a human in customer support rather than auto-refunding. Forwarded to Daniel.

## Outcome (recorded after disposition)
Refund denied. The customer escalated to a chargeback under a consumer-dispute reason; representment succeeded on the basis of the inspection evidence. The account was deactivated under the merchant's terms-of-service refund-fraud clause. No fraud Label was assigned to the original Transaction in the Label store.
