"""Guardrail rule definitions.

In the original repo these rules live in NeMo Guardrails' Colang DSL. Here
they're expressed as plain, auditable Python so the rule set itself can be
reviewed as part of a safety/compliance sign-off without requiring a Colang
runtime. Swap this module for real `.co` files + `nemoguardrails` if/when
you need the full dialogue-rail feature set.

Two rule families:
  1. INPUT rules — refuse before retrieval even runs (safety-bypass intent).
  2. OUTPUT rules — verify the generated answer's numeric technical claims
     are actually grounded in the retrieved source chunks, not invented.
"""
import re

# --- Input rules: safety-bypass intent ---------------------------------
# Matched as verb + safety-noun co-occurrence rather than brittle exact
# phrases, so "bypass the safety door interlock" and "override safety door"
# both trigger even though neither is a literal phrase in this list.
BYPASS_VERBS = (
    "bypass", "disable", "override", "defeat", "remove", "trick",
    "jump", "circumvent", "disconnect", "cut out", "hack", "spoof",
    "keep running with the door open", "run with the door open",
)
SAFETY_NOUNS = (
    "interlock", "e-stop", "estop", "safety door", "light curtain",
    "guard", "limit switch", "safety relay", "safety circuit",
    "safety sensor", "door sensor", "safety switch",
)

# --- Output rules: numeric technical claims must be grounded ------------
# Matches things like "115%", "85°C", "28 Nm", "9,500 RPM", "2,400 mm/min"
NUMERIC_CLAIM_PATTERN = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?\s?(?:%|°C|Nm|N·m|RPM|rpm|mm/min|mm|hours?|hrs?|minutes?|min)\b"
)


def matches_blocked_intent(text: str) -> str | None:
    lowered = text.lower()
    matched_verb = next((v for v in BYPASS_VERBS if v in lowered), None)
    matched_noun = next((n for n in SAFETY_NOUNS if n in lowered), None)
    if matched_verb and matched_noun:
        return f"{matched_verb} + {matched_noun}"
    # also catch the "run with the door open" phrasing on its own — it implies
    # bypassing the door interlock even without an explicit bypass verb
    if "door open" in lowered and ("keep running" in lowered or "run" in lowered):
        return "run with door open"
    return None


def extract_numeric_claims(text: str) -> list[str]:
    return NUMERIC_CLAIM_PATTERN.findall(text)
