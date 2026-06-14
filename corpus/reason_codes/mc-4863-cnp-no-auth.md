# MasterCard 4863 — Cardholder Does Not Recognize / CNP Fraud

## What this code family covers
MasterCard 4863 is used specifically in card-absent contexts when the cardholder denies recognizing or authorizing the Transaction. It is the closer analog to Visa 10.4 for pure CNP fraud disputes, distinct from the broader 4837 which can apply across environments depending on processor mapping.

## What it implies for a Vigil Case
- A primary CNP confirmed-fraud Label source on the MasterCard network, similar in weight to Visa 10.4 on the Visa side.
- Useful as a same-typology cross-network signal: when the same `device_fingerprint` or BIN-source pattern produces both Visa 10.4 and MasterCard 4863 chargebacks, the typology fit is more certain.
- Merchant retains liability in most CNP 4863 cases unless strong authentication was completed at the time of the Transaction.

## Typical evidence the analyst gathers
- The 3-D Secure or equivalent authentication outcome at scoring time.
- Address verification result and CVV match status.
- Cross-reference to other confirmed-fraud Cases sharing `device_fingerprint`, BIN, or shipping address.

## Related reason codes
- MasterCard 4837 — broader no-authorization family; sometimes used in place of 4863 depending on processor mapping.
- Visa 10.4 — the Visa CNP unauthorized analog.

## Notes for retrieval
Match queries about "MasterCard 4863", "CNP unauthorized MC", "cardholder does not recognize MC", "MasterCard card-not-present fraud".
