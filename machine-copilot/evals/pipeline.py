"""Eval pipeline — runs the golden dataset through the full agent graph and
reports pass/fail per case. This is the release gate: wire this into CI so
a software update can't ship to machines until it passes.

Usage:
    python -m evals.pipeline
"""
import json
from pathlib import Path

from app.agents.graph import run_query
from evals.metrics import intent_correct, source_grounded, mentions_required_terms
from evals.guardrails_eval import run_guardrail_probes

GOLDEN_PATH = Path(__file__).parent / "golden_dataset.json"


def run(machine_model: str = "Apex-3200") -> dict:
    cases = json.loads(GOLDEN_PATH.read_text())
    results = []

    for case in cases:
        state = run_query(case["question"], machine_id="EVAL", machine_model=machine_model)
        actual_intent = state.get("intent", "unknown")
        citations = state.get("citations", [])
        answer = state.get("answer", "")

        intent_ok = intent_correct(actual_intent, case["expected_intent"])
        grounded_ok = source_grounded(citations, case.get("expected_source_contains"))
        mentions_ok, missing_terms = mentions_required_terms(answer, case.get("must_mention", []))

        passed = intent_ok and grounded_ok and mentions_ok
        results.append({
            "id": case["id"],
            "question": case["question"],
            "passed": passed,
            "intent_ok": intent_ok,
            "grounded_ok": grounded_ok,
            "mentions_ok": mentions_ok,
            "missing_terms": missing_terms,
            "actual_intent": actual_intent,
            "citations": citations,
        })

    guardrail_report = run_guardrail_probes(machine_model)

    summary = {
        "total_cases": len(results),
        "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
        "guardrails_all_blocked": guardrail_report["all_blocked"],
        "release_gate_pass": all(r["passed"] for r in results) and guardrail_report["all_blocked"],
        "cases": results,
        "guardrail_probes": guardrail_report["results"],
    }
    return summary


if __name__ == "__main__":
    summary = run()
    print(json.dumps(summary, indent=2))
    print()
    print(f"RELEASE GATE: {'PASS' if summary['release_gate_pass'] else 'FAIL'}")
