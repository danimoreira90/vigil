# Visa 10.4 — Card-Absent Environment Fraud

## What this code family covers
Visa reason code 10.4 is used by issuers to dispute transactions that occurred in a card-absent environment (e-commerce, mail-order, telephone) when the cardholder asserts the charge was not authorized by them. The acquirer accepted the transaction without the physical card present and without a successful strong-authentication flow that would shift liability away from the merchant.

## What it implies for a Vigil Case
- The merchant bore the fraud risk for the transaction. Vigil's Decision Engine had its only chance to prevent loss at scoring time.
- Receiving a 10.4 chargeback means a previously-allowed Transaction is now a confirmed-fraud Label with a multi-week lag. This is a primary Label source for the Label Factory and for cold-start training.
- A cluster of 10.4 chargebacks across many merchants on similar `device_fingerprint` or BIN signals indicates organized card-absent fraud, not isolated incidents — it is a typology signal, not just a single Label.

## Typical evidence the analyst gathers
- Whether 3-D Secure was attempted and the outcome (no challenge presented, frictionless flow, failed challenge, successful challenge).
- Address verification result and CVV match status at scoring time.
- Whether the `device_fingerprint` or shipping address appears in any other confirmed-fraud Case.
- Time-to-chargeback and the geographic relationship between the issuing BIN and the shipping destination.

## Related reason codes
- Visa 10.5 — disputes related to authentication outcomes; relevant when 3-D Secure was attempted but the cardholder still denies the charge.
- MasterCard 4837 and 4863 — equivalent card-absent unauthorized families on the MasterCard network. A useful cross-network signal when the same actor targets BINs on more than one network.
- American Express F29 — Amex's card-not-present unauthorized family, comparable in intent.

## Notes for retrieval
This entry should match queries about "CNP chargeback", "card not present unauthorized", "cardholder denies online purchase", and "10.4 dispute reason".
