"""Local generation. Ship path is Ollama; GPT4All kept as reproducible escape hatch.

ADR-003 amendment (2026-06-20): GPT4All's GPU paths are unworkable on this
host — CUDA loads but silently emits nothing; Vulkan is too slow for
CoT/RAG-length generation (a 3-call cell exceeded 600 s). The ship engine
becomes Ollama (llama3.1:8b) via its OpenAI-compatible endpoint at
http://localhost:11434/v1, which keeps inference on-box (HR-3) while
giving usable latency.

The c04 notebook was recorded against GPT4All and must remain
reproducible, so the gpt4all path is retained behind an env switch:

    VIGIL_LOCAL_ENGINE=ollama   (default — c02, c05, and the ship path)
    VIGIL_LOCAL_ENGINE=gpt4all  (c04 reproduction only)

The selector mirrors the local/cloud switch style in generate.py: one
small if/else, no class tree, no framework. Both branches return the same
(text, model_name) tuple generate() already consumes.
"""
from __future__ import annotations

import os
import sys

LOCAL_ENGINE = os.environ.get("VIGIL_LOCAL_ENGINE", "ollama").lower()
if LOCAL_ENGINE not in {"ollama", "gpt4all"}:
    raise ValueError(
        f"VIGIL_LOCAL_ENGINE={LOCAL_ENGINE!r} is not supported. "
        f"Use 'ollama' (default, ship path) or 'gpt4all' (c04 reproduction)."
    )

LOCAL_N_CTX = 4096
LOCAL_MAX_TOKENS = 1024
LOCAL_TEMPERATURE = 0.0


# --- Ollama backend -----------------------------------------------------------

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL_NAME = "llama3.1:8b"

# Probe used to confirm the GPU backend can actually emit tokens (gpt4all only).
# Kept tiny so a broken backend reveals itself in well under a second.
_PROBE_PROMPT = "Say OK."
_PROBE_MAX_TOKENS = 8

# Module-level cache: load/connect once per process (CS-10).
_MODEL: object | None = None
_DEVICE: str | None = None
_GPU_FAILURE_REASON: str | None = None


if LOCAL_ENGINE == "ollama":
    LOCAL_MODEL_NAME = OLLAMA_MODEL_NAME
    _DEVICE = "ollama"

    def _get_ollama_client():
        global _MODEL
        if _MODEL is not None:
            return _MODEL
        from openai import OpenAI

        # api_key is required by the SDK but ignored by Ollama's OpenAI
        # shim. Nothing leaves the host (HR-3).
        _MODEL = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        print(
            f"[local] ollama client ready (base_url={OLLAMA_BASE_URL}, "
            f"model={LOCAL_MODEL_NAME})",
            file=sys.stderr,
        )
        return _MODEL

    def generate_local(prompt: str) -> tuple[str, str]:
        """Return (text, model_name) — Ollama OpenAI-compatible chat completion."""
        client = _get_ollama_client()
        response = client.chat.completions.create(
            model=LOCAL_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=LOCAL_MAX_TOKENS,
            temperature=LOCAL_TEMPERATURE,
        )
        text = response.choices[0].message.content or ""
        return text, LOCAL_MODEL_NAME

else:  # LOCAL_ENGINE == "gpt4all"
    from gpt4all import GPT4All

    LOCAL_MODEL_NAME = "Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf"

    def _get_gpt4all_model() -> GPT4All:
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
            print(
                f"[local] loaded {LOCAL_MODEL_NAME} on CPU (n_ctx={LOCAL_N_CTX})",
                file=sys.stderr,
            )
        return _MODEL

    def generate_local(prompt: str) -> tuple[str, str]:
        """Return (text, model_name) — GPT4All chat session (c04 reproduction path)."""
        model = _get_gpt4all_model()
        with model.chat_session():
            text = model.generate(
                prompt,
                max_tokens=LOCAL_MAX_TOKENS,
                temp=LOCAL_TEMPERATURE,
            )
        return text, LOCAL_MODEL_NAME


# --- Public surface (c04 imports these by name, both engines) -----------------

def get_local_device() -> str | None:
    """Device the local engine produces output on.

    'ollama' for the ship path; 'gpu' or 'cpu' for the gpt4all path (set
    after first load); None before any load.
    """
    return _DEVICE


def get_gpu_failure_reason() -> str | None:
    """Repr of why the gpt4all GPU path was rejected. None under ollama or when GPU is in use."""
    return _GPU_FAILURE_REASON
