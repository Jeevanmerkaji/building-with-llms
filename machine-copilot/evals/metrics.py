"""Metrics for the golden-dataset eval run.

Kept deliberately simple and literal (substring/keyword checks) rather than
an LLM-graded rubric, so a failing test always points to an exact, explainable
reason — important when these evals are the release gate for something
safety-adjacent.
"""


def intent_correct(actual_intent: str, expected_intent: str) -> bool:
    return actual_intent == expected_intent


def source_grounded(citations: list[str], expected_source_contains: str | None) -> bool:
    if expected_source_contains is None:
        return True  # chat/blocked cases have no expected source
    return any(expected_source_contains in c for c in citations)


def mentions_required_terms(answer: str, must_mention: list[str]) -> tuple[bool, list[str]]:
    lowered = answer.lower()
    missing = [term for term in must_mention if term.lower() not in lowered]
    return (len(missing) == 0, missing)
