# Visa 10.x — Fraud Family Overview

## What this code family covers
The Visa 10.x reason codes are the network's primary chargeback bucket for transactions the issuer claims were not authorized by the cardholder. The family is split by environment (card-present, card-absent) and by whether a strong-authentication outcome is in play. For Vigil's purposes — CNP focus — the most material members of the family are 10.4 (card-absent unauthorized) and 10.5 (disputes around authentication outcomes).

## What it implies for a Vigil Case
- Any incoming 10.x chargeback is a confirmed-fraud Label on the disputed Transaction, with the multi-week lag typical of network disputes.
- Clusters of 10.x chargebacks tied to the same `device_fingerprint`, BIN range, or merchant configuration indicate organized activity, not isolated incidents.
- 10.x is the dominant Label source for the Label Factory's training signal during the early life of the system.

## Typical evidence the analyst gathers
- Sub-code within the 10.x family (which one — and therefore which environment and which authentication context).
- 3-D Secure status and outcome at scoring time.
- The chargeback's compelling-evidence requirements for representment, which depend on the sub-code.

## Related reason codes
- 10.4 — the specific CNP unauthorized member, the most common label source for Vigil.
- 10.5 — disputes around authentication outcomes; relevant when 3-D Secure was attempted but the Transaction is still disputed.
- 11.x — authorization-related disputes (distinct from fraud claims).

## Notes for retrieval
Match queries about "Visa fraud reason codes", "10 series chargeback", "Visa fraud chargeback family".
