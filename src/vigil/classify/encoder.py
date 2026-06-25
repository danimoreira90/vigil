"""Encoder-only zero-shot classification via DeBERTa-v3-base-MNLI.

``pipeline("zero-shot-classification")`` turns each candidate label into an NLI
hypothesis and scores entailment against the Case (the premise). The 12 fraud
slugs share one hypothesis template; the 13th label, "legitimate", needs its
own hypothesis — the fraud template reads as nonsense for a clean transaction.

To give per-label hypotheses through a single pipeline call, we build the full
hypothesis sentence for each label and pass them as ``candidate_labels`` with an
identity ``hypothesis_template="{}"``; the returned scores are then mapped back
to slugs. ``transformers``/``torch`` are imported lazily (CS-10).
"""
from __future__ import annotations

from dataclasses import dataclass

from vigil.classify.labels import LEGITIMATE, slug_to_phrase

ENCODER_MODEL = "MoritzLaurer/deberta-v3-base-mnli"
FRAUD_HYPOTHESIS = "This payment fraud case is {}."
LEGITIMATE_HYPOTHESIS = "This is a legitimate, non-fraudulent transaction."

_pipeline = None


@dataclass(frozen=True)
class EncoderResult:
    top_label: str
    scores: dict[str, float]  # label slug -> entailment score, descending


def hypothesis_for(slug: str) -> str:
    if slug == LEGITIMATE:
        return LEGITIMATE_HYPOTHESIS
    return FRAUD_HYPOTHESIS.format(slug_to_phrase(slug))


def load_zero_shot_pipeline():
    global _pipeline
    if _pipeline is None:
        from transformers import pipeline

        _pipeline = pipeline("zero-shot-classification", model=ENCODER_MODEL)
    return _pipeline


def classify_encoder(
    case_body: str, labels: tuple[str, ...], pipeline
) -> EncoderResult:
    hypothesis_to_slug = {hypothesis_for(slug): slug for slug in labels}
    output = pipeline(
        case_body,
        candidate_labels=list(hypothesis_to_slug),
        hypothesis_template="{}",
        multi_label=False,
    )
    scores = {
        hypothesis_to_slug[hypothesis]: score
        for hypothesis, score in zip(output["labels"], output["scores"])
    }
    top_label = hypothesis_to_slug[output["labels"][0]]
    return EncoderResult(top_label=top_label, scores=scores)
