# MasterCard 4837 — No Cardholder Authorization

## What this code family covers
MasterCard 4837 is the network's chargeback code for transactions the issuer asserts were not authorized by the cardholder, applicable across CNP and some CP contexts. The cardholder denies having authorized the charge and the issuer files on their behalf. The merchant is on the hook unless representment evidence rebuts the claim, which is hard in a CNP context without strong authentication.

## What it implies for a Vigil Case
- A primary confirmed-fraud Label source for MasterCard transactions, analogous to Visa 10.4 on the Visa side.
- Pattern overlap with Visa 10.4 across the same `device_fingerprint` or BIN range is a strong indicator of organized CNP fraud rather than isolated incidents.
- When the disputed Transaction had no successful strong-authentication step, the merchant retains the loss; this is the merchant-at-risk default for CNP.

## Typical evidence the analyst gathers
- The strong-authentication status at scoring time (no attempt, frictionless approval, step-up succeeded).
- Address verification and CVV match outcomes.
- Whether the same `device_fingerprint` appears in other confirmed-fraud Cases on either MasterCard or Visa networks.

## Related reason codes
- MasterCard 4863 — the CNP-specific variant; some processors apply 4863 where others apply 4837.
- Visa 10.4 — the Visa-side equivalent.

## Notes for retrieval
Match queries about "MasterCard 4837", "no cardholder authorization", "MC unauthorized chargeback".
