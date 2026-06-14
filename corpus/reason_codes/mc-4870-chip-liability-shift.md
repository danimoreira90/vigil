# MasterCard 4870 — Chip / Authentication Liability Shift

## What this code family covers
MasterCard 4870 covers disputes where the issuer shifts liability for fraud back to the merchant because the merchant did not perform a required strong-authentication step that the issuer had made available — for example, accepting a magnetic-stripe Transaction on a chip-capable card, or processing a CNP Transaction without using 3-D Secure when the issuer required it. The dispute is fraud-flavored; the cause is the missing authentication step.

## What it implies for a Vigil Case
- A 4870 chargeback is a confirmed-fraud Label, but its arrival also indicates an authentication-policy gap on the merchant side that should be closed.
- Patterns of 4870 disputes across many cardholders on the same merchant suggest the merchant's integration is skipping strong authentication where it should be invoked, raising the merchant's risk exposure beyond the per-Transaction loss.
- The analyst should escalate to the merchant-monitoring queue when 4870 volume crosses a threshold; closing the integration gap pays off faster than chasing per-Transaction Cases.

## Typical evidence the analyst gathers
- Whether strong authentication was attempted and the outcome.
- The merchant's authentication configuration at the time of the Transaction.
- Any recent changes to the merchant's checkout integration that may have toggled authentication.

## Related reason codes
- MasterCard 4837 / 4863 — unauthorized claims without a liability-shift framing.
- Visa 10.5 — comparable authentication-related dispute family on the Visa side.

## Notes for retrieval
Match queries about "MasterCard 4870", "MC liability shift", "chip liability shift", "MC 3DS dispute".
