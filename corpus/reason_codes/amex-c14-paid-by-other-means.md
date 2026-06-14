# American Express C14 — Paid by Other Means

## What this code family covers
American Express C14 is a consumer dispute reason used when the cardmember asserts that the underlying purchase was paid by a method other than the Amex card — for example, cash paid in person, a different card used at point of sale, or a refund issued that the merchant double-charged.

## What it implies for a Vigil Case
- Not a fraud Label source. The Transaction itself was likely authorized; the dispute is about whether it should have been charged given an out-of-band payment.
- A pattern of C14 disputes at a single merchant points to a billing reconciliation problem on the merchant side, not to a fraud trend on Vigil's surface.
- Useful to filter out of the fraud-Label training pipeline so the model is not trained on operational issues.

## Typical evidence the analyst gathers
- The receipt, invoice, or settlement record for the disputed Transaction.
- Whether a refund was issued through the merchant's normal flow before the chargeback.
- Any duplicate-charge indications.

## Related reason codes
- American Express C08 — non-receipt, distinct consumer-dispute family.
- MasterCard 4853 — broader cardholder dispute family on MasterCard.

## Notes for retrieval
Match queries about "Amex C14", "American Express paid by other means", "Amex duplicate charge dispute".
