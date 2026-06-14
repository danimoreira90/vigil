# GDPR — Automated Fraud Decisions Summary

> Paraphrased from publicly available regulatory material on the EU General Data Protection Regulation. Not a legal substitute.

## Why this matters to Vigil
GDPR applies to processing of personal data of individuals in the European Union, including the automated decisions Vigil makes about Transactions involving EU cardholders. Article 22 is the most directly relevant provision for an automated fraud-detection system: it constrains decisions made by solely automated means that produce legal or similarly significant effects for the data subject.

## Key principles the analyst should reason from
- A decision to `block` a Transaction can be a "similarly significant" effect under Article 22 depending on context. The mitigation is to ensure meaningful human involvement is available — Vigil's `review` queue and analyst Disposition pattern are the design response.
- Data subjects have the right to obtain human intervention, to express their point of view, and to contest the decision. Operationally, this translates into a customer-facing path to ask for review.
- Information about the logic of an automated decision must be available to the data subject in a meaningful form. The Reason Codes Vigil emits are part of the answer: they translate the Score into something explainable.
- The same data-subject rights (access, correction, deletion, portability) that apply under LGPD apply here under GDPR, with their own procedural specifics.

## Implications for Disposition writing
- A Disposition rationale should be written in language that, if disclosed to the data subject, would explain the decision. Avoid internal shorthand that would not survive an external review.
- When a Transaction is `block`-recommended by an automated path, the Case should preserve the evidence needed for a human reviewer to revisit it. The corpus chunker preserves source citations so the rationale can be reconstructed; the same logic applies to the Case store.

## Out of scope
- The full Article 22 analysis for a specific deployment is counsel's domain.
- This entry is orientation for the analyst, not legal advice.

## Notes for retrieval
Match queries about "GDPR Article 22", "automated decisions fraud", "GDPR fraud detection rights", "right to human review fraud".
