# BIN Attack

## Summary
A variant of card testing in which the attacker walks a Bank Identification Number (BIN) range sequentially, generating candidate card numbers from a single issuer and submitting them against a merchant in rapid bursts. The attacker does not start from a purchased card batch; they start from a guess at which BINs are still active and which check-digit patterns will yield issued cards.

## Typical signals
- High `velocity_high` concentrated on a tight numeric neighborhood of `card_token` values — very different from generic card testing, which spans many BINs.
- A burst of authorization attempts on one merchant followed by a long quiet period, repeating across days or weeks (the attacker is rotating BINs, not surfaces).
- Many declines for "card not found" or "invalid number" interleaved with a small set of approvals.
- A geographic narrowness in the IP source (single ASN, single hosting provider) at odds with the apparent issuer diversity in the BIN range.

## Linked Vigil reason codes
- `velocity_high` — by definition.
- `decline_then_success` — the BIN walk's hit pattern produces this in tight clusters.
- `low_amount_anomaly` — the attacker still wants cheap validation per attempt.

## Recommended action
- The Decision Engine should treat a single-BIN burst differently from a multi-BIN burst: a single-BIN burst is BIN-attack, not card-testing, and is best blocked at the BIN+IP pair rather than at the BIN alone. Blocking a whole BIN harms legitimate cardholders.
- Inform the issuer associated with the targeted BIN range when the volume crosses a coordination threshold; they can rotate or revoke generated numbers.
- Candidate Rule: review when (`velocity_high` from same IP AND single BIN AND decline ratio > 50% in 10 min).

## Related typologies
- Card testing — broader: a purchased batch across many BINs, rather than a sequential walk inside one.
