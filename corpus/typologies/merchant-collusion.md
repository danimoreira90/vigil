# Merchant Collusion

## Summary
A merchant (or someone with merchant credentials) deliberately processes Transactions they know to be fraudulent — often using card data the merchant or an accomplice obtained — and shares the proceeds with the cardholder side of the scheme. Distinct from third-party fraud because the merchant is an active participant, not a victim. Often shows up at small merchants opened specifically for the scheme ("bust-out merchants") or at compromised merchant accounts whose owners do not know the credentials have been resold.

## Typical signals
- A merchant's processing volume jumps sharply with no corresponding marketing event or seasonal explanation.
- The merchant's chargeback rate is disproportionate to its category baseline within the first 30 to 90 days of activity.
- A high concentration of approvals for round-number amounts, often the maximum allowed per Transaction under the merchant's acquirer agreement.
- A pattern of `card_token` values that have no prior history at the merchant's category and an unusual geographic source distribution.

## Linked Vigil reason codes
- Per-Transaction reason codes are unreliable here; detection is merchant-level.
- `chargeback_history` at the merchant level (not the cardholder level) is the strongest single indicator.

## Recommended action
- Vigil's role in merchant collusion is limited at the per-Transaction Scorer; the acquirer's risk team owns the merchant relationship.
- Where the merchant is also a Vigil customer, raise the Case to the merchant-monitoring queue rather than treat it as a per-Transaction signal.
- Candidate Rule: alert (not block) when (merchant chargeback rate > category 95th percentile) AND (merchant tenure < 90 days).

## Related typologies
- Triangulation fraud — distinct in that triangulation uses a legitimate merchant as the unwitting fulfillment leg; merchant collusion makes the merchant a knowing participant.
- Friendly fraud — both involve a participant on the merchant or cardholder side acting against the network; merchant collusion is the merchant-side version.
