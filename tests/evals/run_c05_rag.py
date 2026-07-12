"""Standalone runner for the c05 RAG eval — a clone of run_c02_prompting.py.

Same crash-safe contract: persist to tests/evals/c05_results.json and
c05_raw_outputs.json **after every single generation**, so a crash, timeout, or
Ctrl-C preserves all work done so far. The notebook reads the JSON and renders
tables instead of running the loop.

Two arms per (case x run), one variable only (D2/D3):

    baseline_t3 = technique_t3(case_body)            # no retrieved context
    rag_t3      = technique_t3 + RETRIEVED KNOWLEDGE  # trusted reference block

Same 10 cases, same Ollama llama3.1:8b, same conditions. Retrieval runs once
per case and both arms share the identical case body; the reference block is the
sole difference. rec_match is scored against the shared GOLD map; the
knowledge-only index (HR-4) means no gold answer can be retrieved.

HYPOTHESIS (pre-registered): context lifts the two review-continue cases T3
missed 0/3 in c02 (friendly-fraud-chargeback, refund-fraud-pattern). Success =
both reach >=2/3 in rag_t3 AND no case that passed 3/3 in baseline regresses.

Usage:
    python tests/evals/run_c05_rag.py [N_CASES] [N_RUNS]

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

from vigil.generation.case_loader import (  # noqa: E402
    MissingDispositionHeader,
    load_case_body,
)
from vigil.generation.disposition_parse import parse_disposition  # noqa: E402
from vigil.generation.generate import generate  # noqa: E402
from vigil.generation.prompt import technique_t3  # noqa: E402
from vigil.generation.schema import Disposition  # noqa: E402
from vigil.rag.pipeline import build_rag_prompt, retrieve_context  # noqa: E402

# Plain import (not relative): this script's own directory is on sys.path[0]
# when run as `python tests/evals/run_c05_rag.py`.
from gold_dispositions import GOLD  # noqa: E402


CASES_DIR = PROJECT_ROOT / "corpus" / "cases"
CORPUS_ROOT = PROJECT_ROOT / "corpus"
EVALS_DIR = PROJECT_ROOT / "tests" / "evals"
RESULTS_PATH = EVALS_DIR / "c05_results.json"
RAW_OUTPUTS_PATH = EVALS_DIR / "c05_raw_outputs.json"

ALL_CORPUS_PATHS = {
    str(p.relative_to(CORPUS_ROOT)).replace("\\", "/")
    for p in CORPUS_ROOT.rglob("*.md")
}


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

            # Retrieve once per case; both arms share the identical case body.
            hits = retrieve_context(case_body)
            retrieved_paths = [
                f"{h.chunk.source_path}#{h.chunk.section_title}" for h in hits
            ]
            arms = {
                "baseline_t3": technique_t3(case_body),
                "rag_t3": build_rag_prompt(case_body, hits),
            }

            for arm_name, prompt in arms.items():
                elapsed = time.perf_counter() - start
                if elapsed > time_budget_sec:
                    print(
                        f"[budget] elapsed {elapsed:.0f}s > {time_budget_sec:.0f}s; "
                        f"stopping early with {len(results)} rows saved.",
                        flush=True,
                    )
                    save(results, raw_outputs)
                    return

                t0 = time.perf_counter()
                try:
                    gen_result = generate(prompt, backend="local")
                    text = gen_result.text
                    err: str | None = None
                except Exception as exc:
                    text = ""
                    err = repr(exc)
                latency_ms = (time.perf_counter() - t0) * 1000.0

                arm_paths = retrieved_paths if arm_name == "rag_t3" else None
                if err:
                    row = {
                        "case": case_path.name, "arm": arm_name, "run": run_idx,
                        "gold": gold, "parse_status": "gen_error", "schema_valid": False,
                        "rec_match": None, "emitted_rec": None, "confidence": None,
                        "citation_faithfulness": None, "latency_ms": latency_ms,
                        "retrieved_paths": arm_paths, "error": err,
                    }
                else:
                    raw_outputs[f"{case_path.name}::{arm_name}::run{run_idx}"] = text
                    parsed, status = parse_disposition(text)
                    row = {
                        "case": case_path.name, "arm": arm_name, "run": run_idx,
                        "gold": gold, "parse_status": status, "schema_valid": parsed is not None,
                        "rec_match": (parsed.recommendation.value == gold) if parsed else None,
                        "emitted_rec": parsed.recommendation.value if parsed else None,
                        "confidence": parsed.confidence.value if parsed else None,
                        "citation_faithfulness": citation_faithfulness(parsed) if parsed else None,
                        "latency_ms": latency_ms, "retrieved_paths": arm_paths,
                    }
                results.append(row)
                save(results, raw_outputs)
                print(
                    f"  run{run_idx} {arm_name:12s} {case_path.name[:40]:40s} "
                    f"{row['parse_status']:14s} "
                    f"valid={str(row['schema_valid']):5s} "
                    f"emitted={row['emitted_rec'] or '-':16s} "
                    f"match={str(row['rec_match']):5s} "
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
