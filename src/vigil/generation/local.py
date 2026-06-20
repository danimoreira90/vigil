"""Local generation via GPT4All. Ship path (ADR-003).

Model: Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf from the GPT4All catalog
(auto-downloaded on first load). Context window deliberately capped at 4096
rather than the full 128k to keep VRAM safe on the RTX 3070.

Loader sequence: GPU (Vulkan, GPT4All's `device='gpu'`) first, then CPU.
The GPU path is **self-validating**: after the SDK reports load success, we
run a tiny probe generation. If that probe returns empty/whitespace — the
silent-failure mode observed with GPT4All's CUDA backend on this host — we
discard the GPU model and reload on CPU. _DEVICE always reflects the device
that actually produced output, never the one that merely loaded.

The CPU fallback is intentional and ADR-003-sanctioned: System 2 is async
(off LAT-1), so CPU latency is acceptable.

Module-level cache: the model loads once per process (CS-10).
"""
from __future__ import annotations

import sys

from gpt4all import GPT4All

LOCAL_MODEL_NAME = "Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf"
LOCAL_N_CTX = 4096
LOCAL_MAX_TOKENS = 1024
LOCAL_TEMPERATURE = 0.0

# Probe used to confirm the GPU backend can actually emit tokens. Kept
# tiny so a broken backend reveals itself in well under a second.
_PROBE_PROMPT = "Say OK."
_PROBE_MAX_TOKENS = 8

_MODEL: GPT4All | None = None
_DEVICE: str | None = None
_GPU_FAILURE_REASON: str | None = None


def get_local_model() -> GPT4All:
    """Load the GPT4All model once per process. GPU first with output validation, CPU fallback."""
    global _MODEL, _DEVICE, _GPU_FAILURE_REASON
    if _MODEL is not None:
        return _MODEL
    try:
        candidate = GPT4All(model_name=LOCAL_MODEL_NAME, device="gpu", n_ctx=LOCAL_N_CTX)
        probe = candidate.generate(
            _PROBE_PROMPT, max_tokens=_PROBE_MAX_TOKENS, temp=LOCAL_TEMPERATURE
        )
        if not probe or not probe.strip():
            raise RuntimeError(
                "GPU backend loaded but probe generation was empty — "
                "silent-failure mode (e.g. broken CUDA backend). Discarding."
            )
        _MODEL = candidate
        _DEVICE = "gpu"
        print(
            f"[local] loaded {LOCAL_MODEL_NAME} on GPU (n_ctx={LOCAL_N_CTX}), "
            f"probe ok: {probe.strip()[:40]!r}",
            file=sys.stderr,
        )
    except Exception as gpu_exc:
        _GPU_FAILURE_REASON = repr(gpu_exc)
        print(
            f"[local] GPU path unusable ({gpu_exc!r}); falling back to CPU",
            file=sys.stderr,
        )
        _MODEL = GPT4All(model_name=LOCAL_MODEL_NAME, device="cpu", n_ctx=LOCAL_N_CTX)
        _DEVICE = "cpu"
        print(f"[local] loaded {LOCAL_MODEL_NAME} on CPU (n_ctx={LOCAL_N_CTX})", file=sys.stderr)
    return _MODEL


def get_local_device() -> str | None:
    """Device the local model actually produces output on: 'gpu', 'cpu', or None if not loaded yet."""
    return _DEVICE


def get_gpu_failure_reason() -> str | None:
    """Repr of why the GPU path was rejected (exception or empty probe). None if GPU is in use."""
    return _GPU_FAILURE_REASON


def generate_local(prompt: str) -> tuple[str, str]:
    """Return (text, model_name)."""
    model = get_local_model()
    with model.chat_session():
        text = model.generate(
            prompt,
            max_tokens=LOCAL_MAX_TOKENS,
            temp=LOCAL_TEMPERATURE,
        )
    return text, LOCAL_MODEL_NAME
