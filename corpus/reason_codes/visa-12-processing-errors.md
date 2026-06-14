# Visa 12.x — Processing Errors

## What this code family covers
The Visa 12.x family covers chargebacks where the merchant's processing of the Transaction is alleged to have been incorrect: a duplicate charge, an incorrect amount, a Transaction processed in the wrong currency, a Transaction processed without acceptance of the cardholder, or a similar procedural mistake. The cardholder is not necessarily disputing intent — they are disputing the mechanics of the charge.

## What it implies for a Vigil Case
- Not a fraud Label source. A 12.x chargeback indicates that the merchant's billing process produced an error, not that the underlying Transaction was unauthorized.
- A spike in 12.x against a merchant correlates with billing-system bugs or recent integration changes, not with fraud activity.
- For Vigil's fraud-model training pipeline, 12.x outcomes should be filtered out of the Label set — including them would teach the model patterns that are about merchant configuration rather than fraud.

## Typical evidence the analyst gathers
- Whether multiple authorizations were obtained on the same Transaction reference.
- Whether the captured amount matches the cardholder's order confirmation.
- Recent changes to the merchant's billing or checkout integration.

## Related reason codes
- 11.x — authorization-specific procedural disputes.
- 13.x — consumer disputes about goods or services rather than mechanics.

## Notes for retrieval
Match queries about "duplicate charge dispute", "wrong amount chargeback", "Visa 12 series", "processing error chargeback".
