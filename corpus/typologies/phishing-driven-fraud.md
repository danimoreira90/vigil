# Phishing-Driven Fraud

## Summary
A funnel rather than an end-state: the attacker harvests credentials, card numbers, or one-time codes through a phishing email, SMS, voice call, or fake checkout page, then converts the harvest into one of several downstream typologies (account takeover, clean fraud, card testing). Detection at the merchant rarely catches the phishing itself; the merchant sees the second-order Transaction.

## Typical signals
- A spike in `cvv_fail` events on a particular issuer's BIN range — phishing kits sometimes capture the PAN without the CVV.
- A burst of `new_device` events on previously-stable accounts that share a recent referrer or campaign source.
- A pattern of Transactions whose timing corresponds to known phishing campaign waves reported by industry sharing groups.
- Customers reporting that they "logged in to a page that looked like ours" — a slow signal that should still feed back into Decision Engine policy.

## Linked Vigil reason codes
- `cvv_fail` — when the harvest was incomplete.
- `new_device` — when the harvested credentials are used from the attacker's infrastructure.
- `geo_mismatch` — phishing waves often originate from a tight set of geographies.

## Recommended action
- Phishing-driven fraud is detected via *patterns over time*, not single Scores. Feed cross-Case observations into a periodic review that updates Decision Engine rules.
- Cooperate with industry information-sharing forums so the merchant's view extends beyond its own surface.
- Candidate Rule: increase friction (step-up authentication) on Transactions originating from IP ranges flagged in shared threat feeds within the last 24 hours.

## Related typologies
- Account takeover — the most common downstream conversion of a credential phish.
- Card testing — the most common downstream conversion of a PAN-only phish.
