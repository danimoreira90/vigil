"""Deterministic tests for the local generation engine selector (ADR-003 amendment).

GPU paths through GPT4All are unworkable on this host (CUDA broken; Vulkan
too slow for CoT/RAG-length output). The ship engine becomes Ollama
(llama3.1:8b) via its OpenAI-compatible endpoint. GPT4All stays as a
reproducible escape hatch for c04 — selected via VIGIL_LOCAL_ENGINE=gpt4all.

These tests pin the *seam*, not a live model:
- The default engine is ollama.
- VIGIL_LOCAL_ENGINE=gpt4all selects the gpt4all path.
- The public symbols the c04 notebook imports (LOCAL_MODEL_NAME, LOCAL_N_CTX,
  get_local_device, get_gpu_failure_reason) resolve under BOTH engines.

No model is loaded here. importlib.reload re-runs the module body so the
selector is re-evaluated against the current environment.
"""
from __future__ import annotations

import importlib
import sys

import pytest


def _reload_local(monkeypatch: pytest.MonkeyPatch, engine: str | None):
    """Reload vigil.generation.local with VIGIL_LOCAL_ENGINE set/unset."""
    if engine is None:
        monkeypatch.delenv("VIGIL_LOCAL_ENGINE", raising=False)
    else:
        monkeypatch.setenv("VIGIL_LOCAL_ENGINE", engine)
    sys.modules.pop("vigil.generation.local", None)
    return importlib.import_module("vigil.generation.local")


def test_default_engine_is_ollama(monkeypatch: pytest.MonkeyPatch):
    local = _reload_local(monkeypatch, None)
    assert local.LOCAL_ENGINE == "ollama"


def test_env_override_selects_gpt4all(monkeypatch: pytest.MonkeyPatch):
    local = _reload_local(monkeypatch, "gpt4all")
    assert local.LOCAL_ENGINE == "gpt4all"


def test_env_override_selects_ollama_explicitly(monkeypatch: pytest.MonkeyPatch):
    local = _reload_local(monkeypatch, "ollama")
    assert local.LOCAL_ENGINE == "ollama"


def test_unknown_engine_raises(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(ValueError, match="VIGIL_LOCAL_ENGINE"):
        _reload_local(monkeypatch, "vllm")


def test_ollama_public_surface(monkeypatch: pytest.MonkeyPatch):
    """c04 imports these names directly — they must resolve under ollama."""
    local = _reload_local(monkeypatch, "ollama")
    assert local.LOCAL_MODEL_NAME == "llama3.1:8b"
    assert isinstance(local.LOCAL_N_CTX, int) and local.LOCAL_N_CTX > 0
    assert local.get_local_device() == "ollama"
    assert local.get_gpu_failure_reason() is None
    # The seam called by generate() must still exist.
    assert callable(local.generate_local)


def test_gpt4all_public_surface(monkeypatch: pytest.MonkeyPatch):
    """The gpt4all escape hatch must still expose the same public names."""
    local = _reload_local(monkeypatch, "gpt4all")
    # Constant kept identical to what c04 recorded in its reproducibility footer.
    assert local.LOCAL_MODEL_NAME == "Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf"
    assert isinstance(local.LOCAL_N_CTX, int) and local.LOCAL_N_CTX > 0
    # No model loaded yet -> device is None, no failure recorded.
    assert local.get_local_device() is None
    assert local.get_gpu_failure_reason() is None
    assert callable(local.generate_local)
