# MasterCard 4849 — Questionable Merchant Activity

## What this code family covers
MasterCard 4849 is used when the issuer asserts that the merchant's activity on the cardholder's account is itself questionable — for example, the merchant appears to be a front for unrelated activity, the merchant has been the subject of a network investigation, or the merchant's processing pattern matches a known abuse template. The dispute is not strictly about the individual cardholder's authorization; it is about the merchant's standing.

## What it implies for a Vigil Case
- When Vigil's own merchant happens to be the target of 4849, the dispute usually signals a network-level investigation that is largely outside per-Transaction Scoring. Escalate to the merchant-monitoring queue.
- When Vigil scores Transactions on behalf of an acquirer who sees 4849 trends across many merchants, this is useful aggregate signal for the merchant-collusion typology.
- Do not treat 4849 as a per-cardholder fraud Label; it is a per-merchant signal.

## Typical evidence the analyst gathers
- Whether the merchant is part of any acquirer's risk-monitoring program.
- Volume and chargeback-rate trends on the merchant in the preceding 90 days.
- Cross-network signals if Visa equivalents are also present.

## Related reason codes
- Visa codes about merchant-status concerns are tracked outside the public chargeback families and arrive through acquirer channels rather than as a single reason code.

## Notes for retrieval
Match queries about "MasterCard 4849", "questionable merchant", "merchant-side chargeback", "MC merchant risk dispute".
