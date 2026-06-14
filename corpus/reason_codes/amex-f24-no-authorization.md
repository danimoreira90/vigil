# American Express F24 — No Cardmember Authorization

## What this code family covers
American Express F24 is the network's chargeback reason for transactions the cardmember asserts they did not authorize, applicable across card-present and card-absent contexts. Broader in scope than F29 (which is CNP-specific), and used where the dispute does not pivot specifically on the card-not-present environment.

## What it implies for a Vigil Case
- A confirmed-fraud Label source for Amex Transactions, comparable to F29 but with somewhat broader applicability.
- The choice between F24 and F29 by the issuer affects representment evidence requirements but, for Vigil's labeling pipeline, both should be ingested as confirmed-fraud labels.
- Cross-reference with `device_fingerprint`-level patterns from other Cases is the main analyst lever, as with F29.

## Typical evidence the analyst gathers
- The environment in which the Transaction was processed (CNP, CP, MOTO, recurring).
- Authentication evidence collected at the time.
- Cross-Case linkage on `device_fingerprint`, IP, or shipping address.

## Related reason codes
- American Express F29 — CNP-specific variant.
- Visa 10.4 and MasterCard 4837 — bank-card analogs.

## Notes for retrieval
Match queries about "Amex F24", "American Express no authorization", "Amex unauthorized cardmember".
