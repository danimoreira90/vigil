"""The generate() seam. ONE signature, two backends (ADR-003).

The seam is a switch on a Literal — not an ABC. There are exactly two
implementations and they will not multiply; CS-2 (no abstractions with one
implementation) bites with equal force at two.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

Backend = Literal["local", "cloud"]


@dataclass(frozen=True)
class GenerationResult:
    text: str
    latency_ms: float
    backend: str
    model_name: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cost_usd: float | None = None


def generate(prompt: str, *, backend: Backend) -> GenerationResult:
    start = time.perf_counter()
    if backend == "local":
        from vigil.generation.local import generate_local

        text, model_name = generate_local(prompt)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return GenerationResult(
            text=text,
            latency_ms=elapsed_ms,
            backend="local",
            model_name=model_name,
        )
    if backend == "cloud":
        from vigil.generation.cloud import generate_cloud

        text, model_name, prompt_tokens, completion_tokens, cost_usd = generate_cloud(prompt)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return GenerationResult(
            text=text,
            latency_ms=elapsed_ms,
            backend="cloud",
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost_usd,
        )
    raise ValueError(f"unknown backend: {backend!r}")
