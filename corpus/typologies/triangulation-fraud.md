# Triangulation Fraud

## Summary
A three-party scheme: the attacker runs a fake online store offering goods at attractive prices, collects payment and shipping details from real customers, then fulfills those customer orders by using stolen card data at a legitimate retailer with the customer's address as the ship-to. The legitimate customer receives goods and is satisfied; the merchant that authorized the stolen-card purchase eats a chargeback; the attacker keeps the customer's payment as profit.

## Typical signals
- A `card_token` whose billing address differs sharply from the shipping address, and whose order pattern matches a popular consumer-facing listing on a separate marketplace.
- Repeated shipments to addresses with no historical connection to the billing identity, often spread across regions in a few-day window.
- The same `device_fingerprint` placing orders that ship to addresses scattered across multiple states or countries — uncommon for a legitimate buyer.
- A statistical concentration of orders for a single SKU at a single merchant, all using different cards but identical buyer behavior.

## Linked Vigil reason codes
- `shipping_billing_mismatch` — by construction.
- `device_shared` — when the attacker's automation reveals one device behind many cards.
- `chargeback_history` — appears later, after the first wave of disputes lands.

## Recommended action
- A single triangulation Transaction in isolation can be hard to distinguish from a gift purchase. Detection improves with windowed aggregation over the `device_fingerprint`.
- Candidate Rule: review when (`shipping_billing_mismatch` AND same `device_fingerprint` has shipped to ≥3 distinct addresses in 7 days).
- For the customer-facing side, work with marketplace partners to surface the underlying fake-storefront pattern, not just the per-Transaction signal.

## Related typologies
- Refund fraud — different mechanism but shares the property that the legitimate customer is satisfied and may even defend the Transaction.
- Promo abuse — similar use of a network of throwaway accounts as cover.
