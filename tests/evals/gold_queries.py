"""Gold query set for the c03 retrieval eval.

CREATE-only per HR-2: queries already in this file are sacred. To add a query,
append to ``GOLD_QUERIES``; never edit or remove an existing entry. The hit
function is intentionally simple:

  - ``chunk.source_path`` must be in ``target_source_paths``;
  - if ``target_sections`` is non-empty, ``chunk.section_title`` must also be
    in it. This pins glossary queries to a specific H2 so a lucky pick of any
    other code in the same file does not count as a hit.

Rationale, intent, and the original mapping are stored inline so the gold set
is auditable on its own without cross-referencing notebook prose.

A separate ``OUT_OF_DOMAIN_QUERY`` lives at the bottom — it is NOT scored in
recall. The notebook uses it to show that the retriever returns only
low-similarity chunks for irrelevant input, which is the score-threshold
argument c05 will lean on.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GoldQuery:
    query: str
    target_source_paths: tuple[str, ...]
    target_sections: tuple[str, ...] = field(default_factory=tuple)
    intent: str = "semantic"   # "lexical" | "semantic" | "mixed"
    rationale: str = ""


GOLD_QUERIES: tuple[GoldQuery, ...] = (
    # ---- Lexical (BM25-favored) ------------------------------------------------
    GoldQuery(
        query="Visa 10.4",
        target_source_paths=("reason_codes/visa-10-4-card-absent.md",),
        intent="lexical",
        rationale="Exact reason-code ID; one canonical file.",
    ),
    GoldQuery(
        query="MasterCard 4837 chargeback",
        target_source_paths=("reason_codes/mc-4837-no-cardholder-auth.md",),
        intent="lexical",
        rationale="Exact code; one file owns it.",
    ),
    GoldQuery(
        query="MC 4863 CNP unauthorized",
        target_source_paths=("reason_codes/mc-4863-cnp-no-auth.md",),
        intent="lexical",
        rationale="Exact code; CNP-specific analog of Visa 10.4.",
    ),
    GoldQuery(
        query="Visa 10.5 3DS dispute",
        target_source_paths=("reason_codes/visa-10-5-3ds-disputed.md",),
        intent="lexical",
        rationale="Exact code; authentication-outcome disputes.",
    ),
    GoldQuery(
        query="PSD2 SCA exemptions",
        target_source_paths=("regulatory/psd2-sca-summary.md",),
        intent="lexical",
        rationale="Exact regulatory term; one canonical summary.",
    ),
    GoldQuery(
        query="velocity_high definition",
        target_source_paths=("glossary.md",),
        target_sections=("velocity_high",),
        intent="lexical",
        rationale="Glossary section is the definition of record. Pinned to H2.",
    ),
    GoldQuery(
        query="chargeback_history meaning",
        target_source_paths=("glossary.md",),
        target_sections=("chargeback_history",),
        intent="lexical",
        rationale="Term referenced everywhere; defined only here. Pinned to H2.",
    ),
    # ---- Semantic (paraphrased; no shared tokens with target) -----------------
    GoldQuery(
        query="cardholder denies an online purchase they did not make",
        target_source_paths=(
            "reason_codes/visa-10-4-card-absent.md",
            "reason_codes/mc-4863-cnp-no-auth.md",
        ),
        intent="semantic",
        rationale="Two valid groundings; concept 'CNP unauthorized' maps to both.",
    ),
    GoldQuery(
        query="attacker validates many stolen cards using small low-value charges",
        target_source_paths=("typologies/card-testing.md",),
        intent="semantic",
        rationale="Textbook card-testing paraphrase.",
    ),
    GoldQuery(
        query="attacker walks sequential numbers within one bank's issuer range",
        target_source_paths=("typologies/bin-attack.md",),
        intent="semantic",
        rationale="Distinguishes BIN-attack from generic card-testing.",
    ),
    GoldQuery(
        query="hijacked customer account purchasing with the stored card",
        target_source_paths=("typologies/account-takeover.md",),
        intent="semantic",
        rationale="ATO concept paraphrased; no 'takeover' token.",
    ),
    GoldQuery(
        query="real customer files a chargeback after the goods arrived",
        target_source_paths=("typologies/friendly-fraud.md",),
        intent="semantic",
        rationale="First-party chargeback fraud; concept paraphrase.",
    ),
    GoldQuery(
        query="fake online store fulfills orders by buying with stolen card data",
        target_source_paths=("typologies/triangulation-fraud.md",),
        intent="semantic",
        rationale="Three-party scheme; no 'triangulation' token in query.",
    ),
    GoldQuery(
        query="fraud engineered to look legitimate so it passes the risk model with a low score",
        target_source_paths=("typologies/clean-fraud.md",),
        intent="semantic",
        rationale="Clean-fraud signature; deliberately avoids 'stolen identity' so it does not collide with synthetic-identity-fraud.md.",
    ),
    GoldQuery(
        query="refund routed to a card different from the original purchase",
        target_source_paths=("typologies/refund-fraud.md",),
        intent="semantic",
        rationale="The 'alternate card' tell from the refund-fraud typology.",
    ),
    # ---- Mixed lexical + semantic ---------------------------------------------
    GoldQuery(
        query="low_amount_anomaly during a card-testing burst",
        target_source_paths=("glossary.md", "typologies/card-testing.md"),
        target_sections=("low_amount_anomaly",),
        intent="mixed",
        rationale="Glossary chunk is pinned to the low_amount_anomaly section; the typology file accepts any chunk.",
    ),
    GoldQuery(
        query="step-up authentication on transactions above USD 2,500",
        target_source_paths=("policies/high-value-transaction-policy.md",),
        intent="mixed",
        rationale="Policy doc states 'above USD 2,500' verbatim; mixed exact-number + concept.",
    ),
    GoldQuery(
        query="3DS frictionless approval and liability shift in Europe",
        target_source_paths=(
            "regulatory/psd2-sca-summary.md",
            "reason_codes/visa-10-5-3ds-disputed.md",
        ),
        intent="mixed",
        rationale="Two valid groundings; both files describe this.",
    ),
)


# Out-of-domain probe — used by the notebook to demonstrate the retriever
# returns only low-similarity junk for irrelevant input. NOT scored in recall.
OUT_OF_DOMAIN_QUERY: str = "what is the capital of France"


def is_hit(chunk_source_path: str, chunk_section_title: str, gold: GoldQuery) -> bool:
    if chunk_source_path not in gold.target_source_paths:
        return False
    if gold.target_sections and chunk_section_title not in gold.target_sections:
        return False
    return True
