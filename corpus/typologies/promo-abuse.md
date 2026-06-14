# Promo Abuse

## Summary
Abuse of merchant incentives — sign-up coupons, free-trial conversions, cashback offers, referral credits, first-purchase discounts — by a single actor or ring creating many accounts to claim the incentive repeatedly. The Transactions individually look small and ordinary; what is fraudulent is the multiplicity and the identity reuse behind it.

## Typical signals
- The same `device_fingerprint` or residential IP completing the new-account incentive flow on many accounts within a short window.
- Email addresses that share a structural pattern (sequential, randomized, or rotated through a single disposable-mail provider).
- A burst of low-value purchases concentrated on the SKU or category that earns the promo, with no follow-up purchases after the promo window closes.
- Shipping addresses that cluster around reshipping facilities or use slight address variations to defeat per-address dedup.

## Linked Vigil reason codes
- `device_shared` — the cleanest single indicator.
- `email_fresh` — supports `device_shared`; promo rings prefer cheap throwaway addresses.
- `low_amount_anomaly` — promo abuse purchases hug the minimum threshold to qualify.

## Recommended action
- Promo abuse is rarely a Score problem at the Transaction level; it is an account-creation and incentive-policy problem. Most defenses live upstream of the Scorer.
- The Decision Engine can apply a cap on incentive payouts per `device_fingerprint` per rolling window, independent of per-Transaction Score.
- Candidate Rule: deny the promo (not the Transaction) when (`device_shared` AND account age < 24h AND already-redeemed-this-device count ≥ N).

## Related typologies
- Synthetic identity fraud — promo rings often graduate to synthetic-identity bust-outs.
- Card testing — promo abuse occasionally co-occurs when free-trial flows accept and store the card for later validation.
