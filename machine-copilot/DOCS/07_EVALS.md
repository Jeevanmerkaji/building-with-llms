# 07 · Evals

`python -m evals.pipeline` — the release gate. Wire this into CI so a
software update can't ship to machines in the field until it passes.

## What it checks
- **`golden_dataset.json`** — real technician-style questions with expected
  intent, expected source file, and required terms the answer must mention.
  Kept as literal substring/keyword checks (`metrics.py`) rather than an
  LLM-graded rubric, so a failing case always points to an exact,
  explainable reason.
- **`guardrails_eval.py`** — a separate, higher-priority check: fires a set
  of safety-bypass probe questions and confirms every single one is
  blocked. A guardrail regression is the highest-severity bug category for
  this product, so it's checked independently of the golden dataset rather
  than being just one more test case among many.

## Release gate logic
`release_gate_pass` is `True` only if **every** golden-dataset case passes
**and** every guardrail probe is blocked. Either failing fails the whole
gate.

## Internal QA view
`streamlit run evals/app.py` gives a visual pass/fail breakdown per case —
useful for a human reviewer signing off on a release, not just a CI
green/red.

## Adding a new test case
1. Add a question + expected intent/source/terms to `golden_dataset.json`.
2. Run `python -m evals.pipeline` and confirm it passes against the current
   build — if it doesn't, that's either a real bug (fix the code) or a gap
   in the knowledge base (add the missing document and re-ingest).
