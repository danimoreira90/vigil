# Case — Clean Fraud Released, Chargeback Six Weeks Later

> Synthetic. All identifiers are masked tokens; no real cardholder or merchant is referenced.

## Masked Transaction snapshot
- `transaction_id`: TX-2026-Q1-104881
- `card_token`: TKN-9c2d...75f0
- `merchant_id`: MRC-electronics-3309
- `channel`: CNP (web checkout)
- `amount`: 2,310.00 USD
- `timestamp`: 2026-01-15T19:22:11Z
- `device_fingerprint`: DEV-3a8f...44b2
- `ip_country`: US
- `billing_country`: US
- `shipping_country`: US (residential address consistent with billing region)

## Scorer output
- `score`: 0.21
- `reason_codes`: [] (no individually material code triggered)
- `model_version`: scorer-2026.01.0
- `decision`: `allow`

## Analyst investigation (post-chargeback)
Six weeks after the Transaction, the issuer filed a Visa 10.4 chargeback. The cardholder denied authorizing the Transaction.

Retrospective analysis: the `device_fingerprint` was novel to the account, but the account had thin history (created 11 weeks before the Transaction), and the device-novelty did not stand out. The IP geolocated to a residential range plausibly consistent with the billing address. The cardholder profile was internally coherent — name, address, phone, and email all resolved to one another in public-data feeds. There was no `cvv_fail`, no `geo_mismatch`, no profile-change-then-spend signature. The Transaction was for a high-value but in-category item.

Cluster analysis across the Label-store update revealed five other confirmed-fraud Cases at similar-tier merchants in the same two-week window, sharing the residential proxy ASN and a specific browser-version fingerprint. The clean-fraud ring signature was visible only at the cluster level; no single Transaction in the cluster would have triggered review under per-Transaction policy.

## Disposition
- `recommendation`: review-continue (post-chargeback Label assignment)
- `confidence`: high
- `cited_sources`: [`typologies/clean-fraud.md`, `reason_codes/visa-10-4-card-absent.md`, `policies/chargeback-response-workflow.md`, `policies/case-disposition-guidelines.md`]
- `rationale`: the chargeback's evidence supports the cardholder's claim; the merchant's representment posture is weak because no strong-authentication step was attempted at the time of the original Transaction. The Transaction is now a confirmed-fraud Label and feeds the Scorer's next training cycle. The ring-level signature suggests a per-Transaction Score will continue to miss this typology; the lever is post-Transaction cluster review for high-value Cases, not lower thresholds at scoring time.

## Candidate Rule proposed
On Transactions above USD 1,500 from accounts younger than 90 days: route to `review` regardless of Score. The cost of false positives at this volume is acceptable against the expected clean-fraud loss. Forwarded to Daniel for risk-appetite ratification (AP-4).

## Outcome (recorded after disposition)
Chargeback accepted; merchant absorbed the loss. The cluster-level pattern was used to seed a graph-analytics review that surfaced four additional Cases for proactive review on the same `MRC-electronics-3309` ring. The proposed Rule's wider review tier was provisionally enabled for one week; false-positive rate observed within tolerance and the Rule was kept.
