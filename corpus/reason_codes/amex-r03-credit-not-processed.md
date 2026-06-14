# American Express R03 — Credit Not Processed

## What this code family covers
American Express R03 is used when the cardmember asserts that the merchant agreed to issue a refund or credit but never processed it. The Transaction itself was authorized; what is in dispute is the missing credit on the cardmember's statement.

## What it implies for a Vigil Case
- Not a fraud Label source. The pattern is a merchant-side operational failure to issue the agreed refund, not a fraud signal on the original Transaction.
- A merchant with rising R03 volume has a refund-processing problem that will eventually become a Visa 13.x / MasterCard 4853 problem on those networks too.
- Useful for the merchant-monitoring queue; not material to per-Transaction scoring.

## Typical evidence the analyst gathers
- The refund authorization record, if one exists.
- The customer-service interaction in which the refund was promised.
- The merchant's refund-processing logs around the relevant period.

## Related reason codes
- American Express C08, C14 — other consumer dispute families on Amex.
- Visa 13.x — analogous consumer dispute family on Visa.

## Notes for retrieval
Match queries about "Amex R03", "American Express credit not processed", "Amex refund not received".
