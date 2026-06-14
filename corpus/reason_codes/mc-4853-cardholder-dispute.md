# MasterCard 4853 — Cardholder Dispute

## What this code family covers
MasterCard 4853 covers cardholder-initiated disputes about the goods or services associated with a Transaction the cardholder did authorize: not as described, not received, defective, credit not processed, cancelled recurring billing not stopped, or similar. Comparable in spirit to the Visa 13.x family.

## What it implies for a Vigil Case
- Not a fraud Label source by default. The Transaction was authorized; the dispute is about the service the cardholder received.
- Intersects with fraud only as a vehicle for friendly fraud — a cardholder using a 4853 reason as cover for a chargeback on a Transaction they did authorize and did receive.
- Repeat 4853 disputes by the same `card_token` against multiple merchants is a friendly-fraud red flag and should be reflected in the cardholder's `chargeback_history` rather than treated as service-quality data.

## Typical evidence the analyst gathers
- Delivery confirmation and signature where physical goods are involved.
- Account history, prior interactions, and prior refund requests.
- Whether the customer cancelled a recurring billing through the merchant's own flow before disputing.

## Related reason codes
- MasterCard 4855 — non-receipt specifically.
- Visa 13.x — analogous family on the Visa side.

## Notes for retrieval
Match queries about "MasterCard 4853", "cardholder dispute MC", "not as described chargeback".
