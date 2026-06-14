# Clean Fraud

## Summary
Sophisticated card-not-present fraud that deliberately presents a low Score. The attacker uses high-quality stolen identity data — matching billing address, working CVV, an email and phone that resolve, a residential IP near the cardholder, an established device profile rented from a proxy network — to defeat statistical detection. The Score is low, signals are quiet, and the chargeback arrives weeks later. The most expensive fraud per Transaction.

## Typical signals
- A Transaction that scores low individually but participates in a small cluster that share a subtle commonality: same residential proxy ASN, same browser version with an unusual configuration, same SKU.
- The cardholder's previous activity is unusually thin (recently opened account, no friction history) — clean fraud rings prefer cards that have not been exercised much.
- High-value goods that are easily resold: electronics, gift cards, branded apparel.
- Shipping to a real address that, on lookup, is a recently-rented residence or a known reshipping endpoint.

## Linked Vigil reason codes
- Often none individually material. Detection comes from cluster-level features built across many Transactions, not from a single Score.
- `chargeback_history` is the only feature reliably useful, and it only kicks in after the first wave has already landed.

## Recommended action
- The Decision Engine cannot block clean fraud on per-Transaction Scores at acceptable false-positive rates. Defenses are mostly behind-the-scenes: device intelligence, behavioral biometrics, post-Transaction monitoring.
- Manual analyst review of high-value Cases — even when Score is low — is a deliberate cost-of-doing-business decision. Make it a policy, not an exception.
- Candidate Rule: route to review when (amount > threshold AND new_card_on_account AND device intelligence score below confidence floor).

## Related typologies
- Account takeover — clean fraud sometimes overlaps when the attacker hijacks an established account specifically because its historical signature reduces Score.
- Synthetic identity fraud — different in that the identity behind clean fraud is real (a victim's), whereas synthetic identity is fabricated.
