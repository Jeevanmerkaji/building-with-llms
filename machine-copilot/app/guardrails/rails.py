"""Guardrail runtime — called by the API layer before/after the agent graph.

check_input()  runs BEFORE retrieval: refuses safety-bypass requests outright,
                so they never reach the LLM or logs as a "normal" question.

check_output() runs AFTER the responder node: any numeric technical claim in
                the generated answer (an RPM, a torque spec, a temperature)
                must appear in the retrieved source text. A claim that isn't
                grounded is the exact failure mode this product exists to
                prevent, so the response is blocked rather than shown.
"""
from dataclasses import dataclass

from .colang_rules import matches_blocked_intent, extract_numeric_claims


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str | None = None


def check_input(user_query: str) -> GuardrailResult:
    matched = matches_blocked_intent(user_query)
    if matched:
        return GuardrailResult(
            allowed=False,
            reason=(
                "This request appears to ask for a way to bypass a physical "
                "safety interlock. I can't help with that. If a safety device "
                "is malfunctioning, contact a qualified technician or your "
                "site's safety officer — do not attempt to defeat it."
            ),
        )
    return GuardrailResult(allowed=True)


def check_output(generated_answer: str, source_context: str) -> GuardrailResult:
    claims = extract_numeric_claims(generated_answer)
    ungrounded = [c for c in claims if c.replace(" ", "") not in source_context.replace(" ", "")]
    if ungrounded:
        return GuardrailResult(
            allowed=False,
            reason=(
                "The generated answer contained technical values "
                f"({', '.join(ungrounded)}) that weren't found in the retrieved "
                "source documents. Blocking this response rather than risk "
                "showing an invented spec — please rephrase or consult the "
                "manual directly for this value."
            ),
        )
    return GuardrailResult(allowed=True)
