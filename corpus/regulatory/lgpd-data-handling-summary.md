# LGPD — Data Handling Summary

> Paraphrased from publicly available regulatory material on Brazil's Lei Geral de Proteção de Dados. Not a legal substitute.

## Why this matters to Vigil
LGPD governs the handling of personal data of individuals in Brazil. Vigil's customers, merchants, and the cardholders behind the Transactions Vigil scores will often include Brazilian residents. The law's relevance here is direct: it constrains how Vigil collects, processes, stores, and explains automated decisions made about Brazilian data subjects.

## Key principles the analyst should reason from
- Personal data must be processed under a lawful basis. For fraud detection, the most often relevant bases are the legitimate interest of the controller (preventing fraud, a recognized purpose) and contract performance.
- Data subjects have rights to access, correct, port, and request deletion of their personal data. Deletion requests collide with the operational need to retain fraud evidence; the resolution is fact-specific and often requires counsel.
- Automated decisions that affect data subjects' interests must be subject to a human-review option on request — directly relevant to Vigil's `review` queue design.
- Data breach notification timelines are short; an incident touching the case store is reportable.

## Implications for Disposition writing
- The rationale text should not contain personal data beyond what is strictly necessary to support the recommendation. Masked tokens are the default form even within analyst notes.
- If the cardholder has invoked an LGPD right that affects the record, that fact should be flagged on the Case for counsel review before deletion or export.

## Out of scope
- The lawful-basis analysis for a particular processing activity is counsel's call.
- This entry is a working orientation, not legal advice.

## Notes for retrieval
Match queries about "LGPD fraud", "Brazil data protection fraud detection", "LGPD automated decisions", "LGPD data subject rights".
