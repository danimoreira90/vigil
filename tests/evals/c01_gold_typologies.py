"""Gold typology labels for the c01 encoder-vs-decoder classification eval.

Daniel-authored, confirmed against each case body AND its (stripped) disposition.
CREATE-once and sacred per HR-2 / HR-4: entries here are the ground truth the
accuracy headline is measured against — never edit a label to make a model look
better. To extend the eval, append a new case; never mutate an existing row.

Two deliberate traps live in this set, both confirmed by reading the bodies:

  - ``case-cnp-velocity-burst`` is filename-"velocity" but dispositions as
    card-testing (low-amount burst, high BIN diversity, decline-then-success).
    The filename is the trap; the body is the label.
  - ``case-high-value-allowed-3ds`` is a confirmed-legit allow — label
    ``legitimate``, the 13th non-typology label. A classifier that cannot
    abstain to "clean" is broken triage (rubric #5).

The label string MUST be one of the 13 from ``vigil.classify.labels.load_labels``
(the 12 corpus typologies + ``legitimate``). The accompanying test asserts this,
so a typo'd gold slug fails loudly rather than silently scoring every model as a
miss on that case.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoldTypology:
    case_file: str   # filename under corpus/cases/
    typology: str    # one of the 13 labels (12 typology slugs + "legitimate")
    rationale: str


GOLD_TYPOLOGIES: tuple[GoldTypology, ...] = (
    GoldTypology(
        case_file="case-account-takeover-shipping-change.md",
        typology="account-takeover",
        rationale="Account-recovery from an unrecognized IP, new device, shipping "
        "address rewritten minutes before checkout — textbook ATO.",
    ),
    GoldTypology(
        case_file="case-bin-attack-blocked.md",
        typology="bin-attack",
        rationale="Sequential card numbers walked within one issuer BIN range.",
    ),
    GoldTypology(
        case_file="case-clean-fraud-released-then-cb.md",
        typology="clean-fraud",
        rationale="Engineered to pass the risk model with a low score; confirmed "
        "fraud only via the later chargeback.",
    ),
    GoldTypology(
        case_file="case-cnp-velocity-burst.md",
        typology="card-testing",
        rationale="TRAP: filename says velocity, body dispositions card-testing — "
        "low-amount burst, high BIN diversity, decline-then-success.",
    ),
    GoldTypology(
        case_file="case-friendly-fraud-chargeback.md",
        typology="friendly-fraud",
        rationale="Real cardholder disputes a legitimately-received purchase "
        "(first-party chargeback fraud).",
    ),
    GoldTypology(
        case_file="case-high-value-allowed-3ds.md",
        typology="legitimate",
        rationale="Confirmed-legit allow: known device, long approved history, "
        "frictionless 3DS. The 13th label — NOT a fraud typology.",
    ),
    GoldTypology(
        case_file="case-phishing-card-test.md",
        typology="card-testing",
        rationale="Primary typology is card-testing; phishing is the source/context "
        "of the stolen cards, not the on-merchant pattern.",
    ),
    GoldTypology(
        case_file="case-promo-abuse-multi-account.md",
        typology="promo-abuse",
        rationale="Many coordinated accounts farming a promotion.",
    ),
    GoldTypology(
        case_file="case-refund-fraud-pattern.md",
        typology="refund-fraud",
        rationale="Refund routed to a card different from the original purchase.",
    ),
    GoldTypology(
        case_file="case-triangulation-marketplace.md",
        typology="triangulation-fraud",
        rationale="Fake marketplace storefront fulfilling orders with stolen card "
        "data — three-party scheme.",
    ),
)
