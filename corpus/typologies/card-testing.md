# Card Testing

## Summary
A fraud pattern in which an attacker validates stolen card numbers by submitting low-value, high-frequency authorization attempts across one or more merchants. The goal is to confirm which cards still authorize before reselling the batch or escalating to higher-value purchases. Most attempts will fail; the attacker only needs a small success rate to monetize the working subset.

## Typical signals
- A burst of low-amount authorizations on the same merchant from many distinct `card_token` values within a short window.
- Multiple declines followed by a successful authorization on the same `card_token` or `device_fingerprint`.
- A high ratio of unique BINs to unique IP addresses, indicating a script rotating through purchased card data.
- Activity concentrated on merchants that accept small charges with minimal address verification (digital goods, small subscriptions, trial signups).

## Linked Vigil reason codes
- `velocity_high` — many attempts in a short window on the same surface.
- `bin_diversity_high` — many distinct BINs from a single IP or device.
- `low_amount_anomaly` — amount well below the merchant's typical ticket.
- `decline_then_success` — repeated declines preceding a small approved charge on the same token or device.

## Recommended action
- If the decline ratio crosses the testing threshold for an IP or device, the Decision Engine should route subsequent attempts to `block` and flag the source for cool-down. Policy thresholds live in the Decision Engine, not in the Scorer (AP-2).
- Successful low-amount charges from the burst should be queued as `review` Cases; they are the only ones that confirm a working card and therefore matter most for downstream label accrual.
- A Rule candidate worth proposing: deny when (decline count from the same IP within window >= N) AND (amount below merchant low-watermark).

## Related typologies
- BIN attack — a card-testing variant that walks a BIN range sequentially rather than rotating a purchased batch.
- Promo abuse — when the validation target is a coupon, trial, or new-account incentive rather than card authorization itself.
