# Synthetic Identity Fraud

## Summary
The attacker fabricates an identity by combining real and invented elements — a real but unused tax identifier, a made-up name and date of birth, a fresh email and phone — and builds it slowly over months: opens a checking account, then a low-limit card, services it cleanly, raises the limit, then "busts out" by maxing every credit line at once and disappearing. From a CNP merchant's point of view the cards look real (because they are) and the cardholder profile looks real (because it has history). The loss surfaces only at bust-out time.

## Typical signals
- A `card_token` only recently issued (within weeks or a few months), used to make a sudden high-value Transaction inconsistent with its short clean history.
- Several `card_token` values that share an `email_fresh` signal pattern, a `device_shared` fingerprint, or the same shipping address despite different billing names.
- An account whose phone, email, and shipping address resolve only to itself (no cross-references in public data feeds).
- A `device_fingerprint` appearing across multiple new accounts in a short window — synthetic rings reuse infrastructure.

## Linked Vigil reason codes
- `email_fresh` — strong when combined with newness of every other identifier.
- `device_shared` — the ring's tell.
- `new_card_on_account` — by definition.

## Recommended action
- Per-Transaction Scoring catches synthetic identity poorly; ring-level detection over the account graph is what works. Send aggregated indicators (shared device across new accounts) to a graph-analytics pipeline rather than relying on the live Scorer.
- Candidate Rule: review when (account age < 90 days AND amount > median × 5 AND device shared with ≥2 other accounts created in same 30-day window).
- Coordinate with the issuer when patterns suggest a ring; the issuer has the credit-bureau data the merchant lacks.

## Related typologies
- Clean fraud — both produce quiet single-Transaction Scores; synthetic identity differs by having no real victim, only a fabricated profile.
- Promo abuse — synthetic accounts are also the workhorse for promo abuse, often before bust-out.
