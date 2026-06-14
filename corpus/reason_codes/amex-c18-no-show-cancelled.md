# American Express C18 — No-Show or Cancelled Reservation

## What this code family covers
American Express C18 is used in lodging, travel, and reservation contexts when the cardmember asserts that they cancelled a reservation within the merchant's allowed policy window, or that a no-show charge was applied incorrectly. The dispute is about whether the merchant's no-show charge was contractually valid.

## What it implies for a Vigil Case
- Not a fraud Label source. Travel-specific consumer dispute.
- Relevant to merchants in lodging and travel categories; for other merchants, this reason code does not normally arise.
- The fraud overlap is small: occasionally a cardmember whose card was stolen disputes a hotel hold or no-show charge made by the attacker, but the F-series codes (F24 / F29) are the cleaner fit there.

## Typical evidence the analyst gathers
- The merchant's cancellation-policy terms in effect at the time of the booking.
- The cancellation request record and its timing relative to the policy window.
- Whether the cardmember was charged a no-show fee or a full-stay fee.

## Related reason codes
- American Express C08 — non-receipt, broader family.
- Visa 13.x and MasterCard 4853 — consumer dispute families on the other networks.

## Notes for retrieval
Match queries about "Amex C18", "American Express no-show dispute", "Amex cancellation dispute", "hotel chargeback".
