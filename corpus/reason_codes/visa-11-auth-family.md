# Visa 11.x — Authorization Disputes

## What this code family covers
The Visa 11.x family addresses chargebacks tied to authorization process failures: the issuer asserts the merchant did not obtain proper authorization, processed after a decline, processed late, or processed without the required authorization step. These are not fraud claims; they are procedural disputes about whether the authorization itself was valid.

## What it implies for a Vigil Case
- Not a primary Label source for fraud-model training. 11.x disputes do not mean the Transaction was unauthorized by the cardholder — they mean the authorization process did not satisfy network rules.
- Still relevant to the Decision Engine for operational reasons: a high 11.x rate may indicate a misconfiguration in the merchant's authorization integration.
- The analyst's task is to separate procedural failures from underlying fraud; sometimes a 11.x and a 10.x are filed on the same Transaction and the underlying story is fraud dressed as procedure.

## Typical evidence the analyst gathers
- The authorization response code returned at the time of the Transaction.
- Time between authorization and capture.
- Whether the merchant attempted a re-authorization after a decline.

## Related reason codes
- 12.x — processing errors broader than authorization specifically.
- 10.x — sometimes filed on the same Transaction when the cardholder also disputes the underlying charge.

## Notes for retrieval
Match queries about "authorization chargeback", "no authorization on file", "Visa 11 series", "declined then captured".
