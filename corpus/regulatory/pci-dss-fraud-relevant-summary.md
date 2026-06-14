# PCI-DSS — Fraud-Relevant Summary

> Paraphrased from the publicly-available standard. Not a legal substitute. Vigil's compliance posture is owned by counsel; this corpus entry only captures what the analyst needs to reason about.

## Why this matters to Vigil
The Payment Card Industry Data Security Standard governs how cardholder data is handled by any party touching the payment flow. Vigil's hardest constraint — HR-3, never store raw PAN or CVV — is in part a PCI-DSS posture: by handling only `card_token` and not the underlying PAN, Vigil keeps a large portion of the cardholder-data scope out of its systems.

## Key principles the analyst should reason from
- Cardholder data, especially the PAN, must not appear in logs, screenshots, exports, or analyst notes. Masked tokens are the only form permitted.
- Sensitive authentication data (CVV, full magnetic-stripe, PIN block) must not be stored after authorization. Vigil does not need this data and does not receive it.
- Access to systems handling cardholder data must follow least-privilege, with role-based access and auditable changes.
- Cryptography of stored cardholder data is required where storage is permitted at all; Vigil's design choice is to not store it.

## Implications for Disposition writing
- A Disposition or Case note that includes a raw PAN, CVV, or any sensitive authentication data is a PCI-DSS reportable incident, not just a fraud-process error. The corpus-load PII test enforces this at the chunk boundary.
- Even masked tokens should appear in the abbreviated form (`TKN-abcd...wxyz`), not the full token string, in any text exposed to external review.

## Out of scope
- Compliance attestation, ROC scope determination, and remediation timelines are counsel's domain.
- This entry is not legal advice and does not substitute for the council of a Qualified Security Assessor.

## Notes for retrieval
Match queries about "PCI-DSS for fraud", "PCI fraud detection scope", "cardholder data analyst handling".
