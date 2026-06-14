# American Express F29 — Card-Not-Present Fraud

## What this code family covers
American Express F29 is the network's chargeback reason for card-not-present transactions the cardmember asserts were not authorized by them. Applies to e-commerce and other remote channels where the physical card was not presented. The merchant is the residual loss-bearer absent strong authentication evidence.

## What it implies for a Vigil Case
- A primary confirmed-fraud Label source for Amex transactions in CNP contexts, analogous in role to Visa 10.4 and MasterCard 4863.
- Amex's chargeback timing and evidence requirements differ from the bank-card networks; the analyst should track time-to-chargeback separately when computing label-arrival statistics.
- Patterns of F29 chargebacks alongside Visa 10.4 and MasterCard 4863 on the same `device_fingerprint` indicate organized cross-network CNP fraud.

## Typical evidence the analyst gathers
- The authentication status at scoring time.
- Address verification and CID match outcomes.
- Cross-network confirmed-fraud presence on the same `device_fingerprint` or shipping address.

## Related reason codes
- American Express F24 — broader no-authorization family, distinct in scope.
- Visa 10.4 and MasterCard 4863 — analogous CNP unauthorized reasons on the other networks.

## Notes for retrieval
Match queries about "Amex F29", "Amex CNP chargeback", "American Express card not present fraud".
