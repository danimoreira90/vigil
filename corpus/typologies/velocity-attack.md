# Velocity Attack

## Summary
A single stolen `card_token` is fired at many merchants in rapid succession to extract value before the cardholder reports the loss. Distinct from card testing: the goal is not to validate the card (the attacker already knows it works) but to monetize it as fast as possible across as many surfaces as possible before the issuer freezes it.

## Typical signals
- The same `card_token` authorizing or attempting at many distinct merchants in a tight window (minutes to hours), often crossing categories — gift cards, electronics, peer-to-peer transfers.
- Each individual merchant sees only one Transaction, so per-merchant `velocity_high` looks ordinary — the pattern is only visible network-wide.
- Geographic dispersion of the merchants relative to the cardholder's normal pattern.
- A preference for instantly-fungible goods at each stop.

## Linked Vigil reason codes
- `velocity_high` — when computed cross-merchant via the network's view, not per-merchant.
- `geo_mismatch` — frequently corroborative.
- `chargeback_history` — after the fact.

## Recommended action
- Single-merchant defenses are blunt against velocity attack because the merchant sees only one Transaction. Defenses depend on issuer cooperation and on inter-merchant signal sharing where available.
- For Vigil, the practical lever is amount-based: a single Transaction on a fresh `card_token` for an instantly-fungible high-value good warrants friction even when the per-merchant Score is benign.
- Candidate Rule: review when (amount > category-specific high-fungibility threshold AND `new_card_on_account` AND first-time-merchant).

## Related typologies
- Card testing — the typology that often produces the validated cards a velocity attack then monetizes.
- Clean fraud — both attempt to defeat per-Transaction Scoring; clean fraud is patient, velocity attack is impatient.
