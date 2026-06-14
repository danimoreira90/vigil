# PSD2 — Strong Customer Authentication Summary

> Paraphrased from publicly available regulatory material. Not a legal substitute.

## Why this matters to Vigil
The European Union's revised Payment Services Directive (PSD2) requires Strong Customer Authentication (SCA) for most electronic payments to or from EU consumers. SCA changes the liability landscape: a Transaction that completed under a successful SCA flow shifts fraud liability toward the issuer; a Transaction that should have used SCA but did not leaves the merchant exposed. This is directly relevant to which `block` decisions cost the merchant money and which do not.

## Key principles the analyst should reason from
- SCA requires two of three independent factors: something the cardholder knows (password, PIN), something they have (a device, a card), something they are (biometric).
- The most common SCA implementation in CNP commerce is 3-D Secure 2.x, with frictionless authentication for low-risk Transactions and step-up challenges for higher-risk Transactions.
- Several exemptions allow merchants or issuers to skip SCA in specific circumstances: low-value Transactions, Transaction Risk Analysis when both acquirer and issuer fraud rates are below threshold, trusted-beneficiary lists, recurring identical-amount Transactions, and merchant-initiated Transactions in certain contexts.
- An SCA failure or omission affects chargeback liability — the relevant network reason codes (e.g. Visa 10.5, MasterCard 4870) reflect this.

## Implications for Disposition writing
- A `block` recommendation that would have been the merchant's loss anyway (no SCA, no liability shift) is more valuable than one on a Transaction whose loss would have shifted to the issuer.
- Cite the SCA outcome in the rationale when the recommendation depends on it. "No SCA attempted" is a material fact, not a footnote.

## Out of scope
- PSD3 changes still in flight at the time of writing; counsel will update guidance as the regime evolves.
- Non-EU Transactions where PSD2 does not apply — reason from the local regime instead.

## Notes for retrieval
Match queries about "PSD2 SCA", "Strong Customer Authentication", "3DS liability shift Europe", "PSD2 exemptions".
