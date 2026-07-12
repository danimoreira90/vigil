"""Gold recommendations per eval case — the ground truth for rec_match scoring.

Extracted verbatim from run_c02_prompting.py (D2) so c02 and c05 score against
one identical GOLD map. Keyed by case filename; value is the expected
Recommendation string. These are the human-assigned dispositions the local
model is graded against; they are NEVER placed into any prompt (HR-4 — the
case_loader strips `## Disposition` on the query side).
"""
from __future__ import annotations

from vigil.generation.schema import Recommendation

GOLD: dict[str, str] = {
    "case-account-takeover-shipping-change.md": Recommendation.BLOCK.value,
    "case-bin-attack-blocked.md": Recommendation.BLOCK.value,
    "case-clean-fraud-released-then-cb.md": Recommendation.REVIEW_CONTINUE.value,
    "case-cnp-velocity-burst.md": Recommendation.BLOCK.value,
    "case-friendly-fraud-chargeback.md": Recommendation.REVIEW_CONTINUE.value,
    "case-high-value-allowed-3ds.md": Recommendation.ALLOW.value,
    "case-phishing-card-test.md": Recommendation.BLOCK.value,
    "case-promo-abuse-multi-account.md": Recommendation.BLOCK.value,
    "case-refund-fraud-pattern.md": Recommendation.REVIEW_CONTINUE.value,
    "case-triangulation-marketplace.md": Recommendation.BLOCK.value,
}
