# Refund Fraud

## Summary
The attacker exploits a merchant's refund or return policy rather than the authorization itself. Variants include: claiming non-receipt on goods that were delivered, returning a different (lower-value or empty) item, social-engineering customer support into refunding to a different card, and abusing duplicate-charge claims. The Score at authorization time is silent; the fraud appears post-Transaction.

## Typical signals
- A `card_token` with an unusually high refund-to-purchase ratio across a short window.
- Refund requests on Transactions where delivery confirmation, signature, or photo evidence exists.
- A customer support interaction asking for the refund to be routed to a different `card_token` than the original Transaction (the "alternate card" tell).
- A cluster of refund-on-arrival reports from one shipping region within a week.

## Linked Vigil reason codes
- `chargeback_history` — overlaps when the refund attempt fails and the customer escalates to a chargeback.
- The other reason codes are silent here by design: scoring acts before refund, not at refund time.

## Recommended action
- Refund fraud is a customer-support and policy problem at least as much as a scoring problem. The Decision Engine can flag accounts where Score is benign but refund rate has crossed a threshold, for human review of refund requests rather than authorization.
- Never refund to a different `card_token` than the original Transaction without out-of-band identity verification — that flow is the most exploited single channel.
- Candidate Rule: flag for support review when (refund-request count > N in last 30 days on account).

## Related typologies
- Friendly fraud — friendly fraud disputes the charge; refund fraud manipulates the merchant's refund process directly.
- Triangulation fraud — different but shares the property that authorization-time signals look clean.
