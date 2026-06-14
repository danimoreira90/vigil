# American Express C08 — Goods or Services Not Received

## What this code family covers
American Express C08 is a consumer dispute reason used when the cardmember paid for goods or services and asserts they were never delivered. Comparable in role to MasterCard 4855 and to the relevant Visa 13.x members.

## What it implies for a Vigil Case
- Not a primary fraud Label source. The dispute is about delivery, not authorization, by default.
- Fraud overlap appears via friendly fraud (cardmember received goods and is disputing anyway) and via triangulation (cardmember authorized a Transaction whose actual fulfillment routed to an attacker).
- A C08 paired with a `shipping_billing_mismatch` reason code at scoring time is a triangulation red flag.

## Typical evidence the analyst gathers
- Tracking and delivery confirmation.
- The shipping address at scoring time and any later change requests.
- Whether the same `device_fingerprint` shipped to many distinct addresses in the relevant window.

## Related reason codes
- American Express C14 — paid by other means (a distinct consumer dispute).
- MasterCard 4855 — analogous non-receipt family on MasterCard.

## Notes for retrieval
Match queries about "Amex C08", "American Express non-receipt", "Amex goods not received".
