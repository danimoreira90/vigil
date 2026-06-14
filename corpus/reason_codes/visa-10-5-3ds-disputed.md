# Visa 10.5 — Disputes Involving 3-D Secure Outcomes

## What this code family covers
Visa 10.5 covers chargebacks where 3-D Secure authentication was part of the Transaction flow but the cardholder still disputes the charge. The dispute may rest on a claim that the authentication outcome was achieved by an attacker who controlled the cardholder's phone or device, that the issuer's risk-based authentication frictionlessly approved a Transaction that should have been challenged, or that the authentication evidence presented does not match the cardholder's behavior.

## What it implies for a Vigil Case
- A 10.5 dispute on a Transaction that scored low at the time often indicates account takeover or sophisticated phishing — the attacker had enough control to defeat authentication.
- The presence of a 3-D Secure attempt does not guarantee liability shift; the outcome must be the right kind of outcome under the issuer's and the network's rules at the time.
- Cluster patterns in 10.5 chargebacks across cardholders often point to a common phishing source.

## Typical evidence the analyst gathers
- The specific 3-D Secure outcome on the disputed Transaction (frictionless approval, step-up challenge attempted, step-up challenge succeeded, no attempt).
- Timing relative to known phishing campaign reports.
- Whether the disputing cardholder had any preceding account profile changes on the merchant side.

## Related reason codes
- 10.4 — the simpler unauthorized-CNP case without authentication context.
- MasterCard 4870 — the equivalent chip / authentication liability-shift family on the MasterCard network.

## Notes for retrieval
Match queries about "3DS chargeback", "authentication disputed", "10.5 dispute", "EMV 3DS fraud claim".
