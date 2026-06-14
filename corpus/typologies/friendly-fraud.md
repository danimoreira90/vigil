# Friendly Fraud (First-Party Chargeback Fraud)

## Summary
The legitimate cardholder makes a real Transaction, receives the goods or services, then files a chargeback claiming non-receipt or unauthorized use. Sometimes deliberate, sometimes a result of confusion (a forgotten subscription, a family member's purchase). From the merchant's point of view the loss is identical to third-party fraud, but the signature at scoring time is the opposite: everything looks normal because everything *was* normal.

## Typical signals
- A chargeback filed weeks after delivery on a Transaction that scored low at the time, with no concurrent third-party fraud signals.
- The same `card_token` has filed previous chargebacks across multiple merchants.
- The dispute reason on the chargeback is "did not receive" or "unauthorized" despite delivery confirmation and successful prior account interactions.
- A pattern of refunds-then-disputes on the same customer across months.

## Linked Vigil reason codes
- `chargeback_history` — the only strong pre-decision signal for first-party fraud.
- Most other reason codes are by definition silent here because the Transaction itself is normal.

## Recommended action
- Friendly fraud is mostly a post-decision problem; the analyst's role is in chargeback response, not in pre-authorization scoring.
- Maintain delivery evidence (carrier tracking, signature, IP at order time, account history) so a chargeback representment has the strongest possible packet.
- The Decision Engine policy may apply a friction step (extra verification at checkout) when `chargeback_history` is set, even when the Score is low, to deter repeat offenders.
- Candidate Rule: require step-up authentication when (`chargeback_history` set AND amount > customer median × 2).

## Related typologies
- Refund fraud — overlapping in that both exploit post-Transaction policies, but refund fraud manipulates the refund flow itself rather than disputing the underlying charge.
