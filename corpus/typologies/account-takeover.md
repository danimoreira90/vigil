# Account Takeover

## Summary
An attacker gains control of a legitimate customer account — typically via credential stuffing, phishing, or SIM swap — then uses the stored payment methods to make purchases that look superficially like the rightful owner's behavior. The Transaction passes the issuer's authorization checks because the card is genuine and the account is genuine; what is fraudulent is the controller of the session.

## Typical signals
- A profile change (shipping address, email, password, phone) within a short window before a high-value Transaction.
- `new_device` plus `night_hour_activity` plus a deviation from the customer's historic merchant mix.
- A `card_token` previously associated with low-amount, frequent purchases now used for a single large-amount order.
- Outbound shipping to an address or country never used on this account before.

## Linked Vigil reason codes
- `new_device` — first time this `device_fingerprint` has touched the account.
- `night_hour_activity` — outside the customer's usual active window.
- `amount_anomaly` — Transaction amount well above the customer's normal ticket.
- `shipping_billing_mismatch` — destination differs from prior history.
- `new_card_on_account` — when the attacker also added a new payment method as cover.

## Recommended action
- Account-takeover Cases should be reviewed even when each individual reason code is weak, because the *combination* is the signature. The Decision Engine policy should weight a profile-change-then-anomaly sequence higher than the sum of its parts.
- Notify the legitimate cardholder via the issuer or the merchant's account-recovery flow; do not reveal that the Transaction was blocked for fraud detection until identity is reconfirmed.
- Candidate Rule: review when (profile change within 24h) AND (`amount_anomaly` OR `shipping_billing_mismatch`).

## Related typologies
- Phishing-driven fraud — the credential source that often precedes account takeover.
- Synthetic identity fraud — distinct in that no legitimate customer ever existed; account takeover hijacks a real one.
