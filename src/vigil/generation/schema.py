"""Disposition contract for System 2 — the JSON shape every analyst LLM emits.

Spec: corpus/policies/case-disposition-guidelines.md (authoritative)
Enum strings byte-exact against the corpus markdown so JSON values can be
copy-pasted between cases and Dispositions without translation.

Reused by c02 (prompt engineering + structured output) and c05 (RAG pipeline).
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


class Recommendation(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REVIEW_CONTINUE = "review-continue"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Disposition(BaseModel):
    recommendation: Recommendation
    confidence: Confidence
    reason_codes: list[str] = Field(default_factory=list)
    cited_sources: list[str] = Field(min_length=1)
    rationale: str = Field(min_length=1)

    @model_validator(mode="after")
    def _block_requires_reason_code(self) -> "Disposition":
        # Policy: "A bare `block` is a defect" — HR-5 parallel.
        if self.recommendation is Recommendation.BLOCK and not self.reason_codes:
            raise ValueError("block recommendation requires at least one reason_code")
        return self
