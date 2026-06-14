# Case — Triangulation Pattern, Marketplace Side Surfaced

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q2-040118
- `card_token`: TKN-6d44...2b9a
- `merchant_id`: MRC-electronics-3309
- `channel`: CNP (web checkout)
- `amount`: 312.00 USD
- `timestamp`: 2026-04-02T11:09:25Z
- `device_fingerprint`: DEV-5e89...01ff
- `ip_country`: US (Pacific Northwest)
- `billing_country`: US (Northeast)
- `shipping_country`: US (Southeast — residential address in a third region)

## Scorer output
- `score`: 0.34
- `reason_codes`: [`shipping_billing_mismatch`, `device_shared`]
- `model_version`: scorer-2026.04.0
- `decision`: `review`

## Analyst investigation
The Transaction in isolation looks like a gift purchase to a relative — billing and shipping in different regions is common at this merchant. What changed the picture was the `device_shared` reason code: the same `device_fingerprint` had placed twelve Transactions to twelve distinct shipping addresses across the preceding 14 days, spread across five regions, each using a different `card_token`.

Cross-referenced the destination addresses against external marketplace listings: each shipping address corresponded to a recent buyer of the same SKU on a popular consumer marketplace, listed at roughly 60% of the merchant's retail price. The pattern matches triangulation: a fake-storefront seller takes the buyer's payment, then fulfills using stolen card data at the legitimate retailer with the buyer's address.

No `velocity_high` per-Transaction, no `cvv_fail`, no `chargeback_history` yet. The detection here is at the cluster level over `device_fingerprint`, not at the Score level.

## Disposition
- `recommendation`: block
- `confidence`: medium
- `cited_sources`: [`typologies/triangulation-fraud.md`, `glossary.md#shipping_billing_mismatch`, `glossary.md#device_shared`, `policies/case-disposition-guidelines.md`]
- `rationale`: the per-Transaction signals are weak, but the cluster pattern over the shared `device_fingerprint` — twelve Cases to twelve distinct addresses across regions — is decisive. The marketplace correlation removes the gift-purchase alternative. Releasing the Transaction would complete an instance of the triangulation cycle and produce a future chargeback when the original cards' owners discover the charges.

## Candidate Rule proposed
Route to `review` when (`device_shared` count ≥ 5 distinct shipping addresses in 14 days) — independent of Score. Forward intelligence to the marketplace partner to take down the fake storefront, since per-Transaction defense alone cannot solve a triangulation ring. Forwarded to Daniel.

## Outcome (recorded after disposition)
Blocked at decision time. Three subsequent Transactions on the same `device_fingerprint` arrived within 48 hours and were blocked under the same Rule. Marketplace partner removed the storefront. No chargebacks accumulated on the blocked Transactions; chargebacks on the previously-released Cases in the cluster arrived over the following six weeks, confirming the typology fit.
