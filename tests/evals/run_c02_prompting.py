"""Standalone runner for the c02 prompt-engineering eval.

Why this exists, not just an in-notebook loop: the full sweep is
N_CASES x N_RUNS x 3 techniques local generations on the Ollama
`llama3.1:8b` path (90 generations at the 10x3 default, ~9 min on this
host). A single notebook cell exceeds nbconvert's per-cell timeout window
in practice (the cell timed out before emitting any captured output). This
runner persists results to tests/evals/c02_results.json **after every
single generation**, so a crash, timeout, or Ctrl-C preserves all work
done so far. The notebook reads the JSON file and renders the same tables,
instead of running the loop itself.

Multi-run: single-run recommendation results are stochastic — rec_match
drifts run-to-run on the local engine. N_RUNS repeats the full
(case x technique) sweep so the notebook can average over runs and report
per-case stability. Each row carries a 0-based "run" field.

Usage:
    python tests/evals/run_c02_prompting.py [N_CASES] [N_RUNS]

A soft TIME_BUDGET_SEC (default 3500 = ~58 min) makes the runner exit
cleanly before any wall-clock killer fires; combined with incremental
save, the worst case is fewer rows than requested with all completed rows
persisted.

NOT a test (no test_ prefix). Pytest does not collect it.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from pydantic import ValidationError  # noqa: E402

from vigil.generation.case_loader import (  # noqa: E402
    MissingDispositionHeader,
    load_case_body,
)
from vigil.generation.generate import generate  # noqa: E402
from vigil.generation.json_repair import (  # noqa: E402
    InvalidDispositionError,
    extract_json,
    repair_json,
)
from vigil.generation.prompt import (  # noqa: E402
    technique_t1,
    technique_t2,
    technique_t3,
)
from vigil.generation.schema import Disposition, Recommendation  # noqa: E402


CASES_DIR = PROJECT_ROOT / "corpus" / "cases"
CORPUS_ROOT = PROJECT_ROOT / "corpus"
EVALS_DIR = PROJECT_ROOT / "tests" / "evals"
RESULTS_PATH = EVALS_DIR / "c02_results.json"
RAW_OUTPUTS_PATH = EVALS_DIR / "c02_raw_outputs.json"

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

TECHNIQUES = {"T1": technique_t1, "T2": technique_t2, "T3": technique_t3}

ALL_CORPUS_PATHS = {
    str(p.relative_to(CORPUS_ROOT)).replace("\\", "/")
    for p in CORPUS_ROOT.rglob("*.md")
}


def parse_disposition(raw: str) -> tuple[Disposition | None, str]:
    try:
        parsed = extract_json(raw)
        status = "extract_ok"
    except InvalidDispositionError:
        try:
            parsed = repair_json(raw)
            status = "repair_ok"
        except InvalidDispositionError:
            return None, "invalid_json"
    try:
        return Disposition(**parsed), status
    except (ValidationError, TypeError, ValueError):
        return None, "schema_invalid"


def citation_faithfulness(parsed: Disposition) -> float:
    if not parsed.cited_sources:
        return 0.0
    hits = sum(
        1 for src in parsed.cited_sources
        if src.split("#", 1)[0] in ALL_CORPUS_PATHS
    )
    return hits / len(parsed.cited_sources)


def save(results: list[dict], raw_outputs: dict[str, str]) -> None:
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    RAW_OUTPUTS_PATH.write_text(json.dumps(raw_outputs, indent=2), encoding="utf-8")


def run(n_cases: int, n_runs: int, time_budget_sec: float) -> None:
    all_cases = sorted(CASES_DIR.glob("case-*.md"))
    assert len(all_cases) == 10, f"expected 10 cases, found {len(all_cases)}"
    cases = all_cases[:n_cases]
    print(
        f"N_CASES={n_cases}; N_RUNS={n_runs}; corpus_paths={len(ALL_CORPUS_PATHS)}; "
        f"time_budget_sec={time_budget_sec:.0f}",
        flush=True,
    )

    results: list[dict] = []
    raw_outputs: dict[str, str] = {}
    start = time.perf_counter()

    for run_idx in range(n_runs):
        for case_path in cases:
            try:
                case_body = load_case_body(case_path)
            except MissingDispositionHeader as exc:
                raise SystemExit(f"anti-leak guard fired: {exc}")
            gold = GOLD[case_path.name]

            for tech_name, tech_fn in TECHNIQUES.items():
                elapsed = time.perf_counter() - start
                if elapsed > time_budget_sec:
                    print(
                        f"[budget] elapsed {elapsed:.0f}s > {time_budget_sec:.0f}s; "
                        f"stopping early with {len(results)} rows saved.",
                        flush=True,
                    )
                    save(results, raw_outputs)
                    return

                prompt = tech_fn(case_body)
                t0 = time.perf_counter()
                try:
                    gen_result = generate(prompt, backend="local")
                    text = gen_result.text
                    err: str | None = None
                except Exception as exc:
                    text = ""
                    err = repr(exc)
                latency_ms = (time.perf_counter() - t0) * 1000.0

                if err:
                    row = {
                        "case": case_path.name, "technique": tech_name, "run": run_idx,
                        "gold": gold, "parse_status": "gen_error", "schema_valid": False,
                        "rec_match": None, "emitted_rec": None, "confidence": None,
                        "citation_faithfulness": None, "latency_ms": latency_ms,
                        "error": err,
                    }
                else:
                    raw_outputs[f"{case_path.name}::{tech_name}::run{run_idx}"] = text
                    parsed, status = parse_disposition(text)
                    row = {
                        "case": case_path.name, "technique": tech_name, "run": run_idx,
                        "gold": gold, "parse_status": status, "schema_valid": parsed is not None,
                        "rec_match": (parsed.recommendation.value == gold) if parsed else None,
                        "emitted_rec": parsed.recommendation.value if parsed else None,
                        "confidence": parsed.confidence.value if parsed else None,
                        "citation_faithfulness": citation_faithfulness(parsed) if parsed else None,
                        "latency_ms": latency_ms,
                    }
                results.append(row)
                save(results, raw_outputs)
                print(
                    f"  run{run_idx} {tech_name} {case_path.name[:44]:44s} "
                    f"{row['parse_status']:14s} "
                    f"valid={str(row['schema_valid']):5s} "
                    f"emitted={row['emitted_rec'] or '-':16s} "
                    f"lat={latency_ms:7.0f}ms",
                    flush=True,
                )

    print(
        f"\nDONE n_rows={len(results)} elapsed_sec={time.perf_counter() - start:.0f}",
        flush=True,
    )


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    n_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    budget = float(os.environ.get("TIME_BUDGET_SEC", "3500"))
    run(n, n_runs, budget)
