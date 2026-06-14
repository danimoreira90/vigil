# MasterCard 4855 — Goods or Services Not Provided

## What this code family covers
MasterCard 4855 covers the specific case where the cardholder claims they paid for goods or services and never received them. Distinct from a general consumer dispute about quality — here the claim is that delivery did not occur at all.

## What it implies for a Vigil Case
- Not a primary fraud Label source. A delivery-failure dispute is most often a fulfillment problem, not a fraud problem.
- The fraud overlap appears via two paths: friendly fraud, in which the cardholder did receive the goods and is lying; and triangulation, in which the original cardholder never received goods because the actual Transaction was placed by an attacker who shipped elsewhere.
- A pattern of 4855 disputes that correlate with `shipping_billing_mismatch` reason codes at the original scoring time is a triangulation signature.

## Typical evidence the analyst gathers
- Carrier tracking history and delivery confirmation.
- The shipping address at the time of the Transaction and any subsequent change requests.
- Whether the same `device_fingerprint` placed orders shipping to many distinct addresses around the disputed Transaction's date.

## Related reason codes
- MasterCard 4853 — broader consumer dispute family.
- Visa 13.x — analogous Visa family.

## Notes for retrieval
Match queries about "MasterCard 4855", "non-receipt chargeback", "goods not received MC".
