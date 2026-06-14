# Visa 13.x — Consumer Disputes

## What this code family covers
The Visa 13.x family addresses chargebacks where the cardholder authorized the Transaction but is unhappy with the result: goods or services not received, goods or services not as described, defective goods, credit not processed, cancelled recurring billing not stopped, or a similar consumer complaint. The card was charged with the cardholder's knowledge; the disagreement is about delivery or quality.

## What it implies for a Vigil Case
- Not a fraud Label source by default. A 13.x dispute is a service-quality story, not a fraud story.
- The intersection with fraud appears via friendly-fraud — a 13.x reason code used as cover for a chargeback on a Transaction the cardholder did authorize and did receive. The dispute reason is the cover; the underlying intent is to reverse a real Transaction.
- Patterns of repeated 13.x claims by the same `card_token` or customer account against multiple merchants are a friendly-fraud red flag and should feed the `chargeback_history` reason code rather than be treated as service-quality issues.

## Typical evidence the analyst gathers
- Delivery confirmation, tracking, and signature evidence.
- Refund and cancellation request history on the customer account.
- Repeat-disputant pattern across merchants if such data is available through industry sharing.

## Related reason codes
- 10.4 — the genuine unauthorized-CNP case, distinct from a consumer dispute.
- 12.x — disputes about Transaction mechanics rather than the goods themselves.

## Notes for retrieval
Match queries about "goods not received chargeback", "not as described dispute", "Visa 13 series", "consumer dispute", "friendly fraud reason code".
