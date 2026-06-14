# BSA / AML — Suspicious Activity Reporting Summary

> Paraphrased from publicly available regulatory material on the United States Bank Secrecy Act and the broader anti-money-laundering regime. Not a legal substitute.

## Why this matters to Vigil
Some fraud patterns Vigil scores intersect with anti-money-laundering obligations: structuring (deliberately keeping Transactions below reporting thresholds to avoid scrutiny), use of payment surfaces to move proceeds of unrelated crime, and patterns suggesting human trafficking, drug proceeds, or sanctions evasion. Where Vigil's surface is operated by or for a regulated financial institution, the institution may have AML obligations independent of and additional to fraud-loss management.

## Key principles the analyst should reason from
- AML and fraud overlap but are not the same. A pattern can be AML-reportable without being fraud, and fraud can be present without an AML obligation arising.
- Structuring patterns — many small Transactions just under a known reporting threshold — are an AML concern regardless of whether the underlying Transactions are fraudulent.
- A Suspicious Activity Report, where required, is a regulated communication with strict timing and confidentiality rules. The subject of the report must not be informed (tipping off is a separate violation).
- Sanctions screening is adjacent: a Transaction involving a sanctioned party can require freezing the funds, not blocking the Transaction; the legal mechanism is different from a fraud `block`.

## Implications for Disposition writing
- A Disposition that suspects AML or sanctions exposure should flag for escalation to counsel rather than recording the substantive AML reasoning in the rationale. The Case enters the regulatory-hold path (see `regulatory-hold-procedure.md`).
- Customer-facing communication for a Case in this state uses neutral "additional verification required" language, never anything that could constitute tipping off.

## Out of scope
- The decision to file a Suspicious Activity Report or freeze funds is a compliance function, not an analyst one.
- This entry is orientation, not legal or compliance advice.

## Notes for retrieval
Match queries about "BSA AML fraud", "suspicious activity report fraud", "structuring fraud detection", "AML and fraud overlap".
