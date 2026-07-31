"""Planner node — classifies the incoming question so the rest of the graph
can route it appropriately. Uses lightweight keyword heuristics rather than
an LLM call here, since intent classification for this small, well-defined
label set doesn't need one and keeping it deterministic makes the routing
behavior easy to test and audit.
"""
import re
from app.agents.state import CopilotState
from app.guardrails.rails import check_input

ALARM_CODE_RE = re.compile(r"\b[A-Z]{2,4}-\d{3,4}\b", re.IGNORECASE)
FEEDS_SPEEDS_KEYWORDS = ("rpm", "feed rate", "spindle speed", "depth of cut", "mm/min", "feeds and speeds")
PROCEDURE_KEYWORDS = ("how do i", "how to", "replace", "procedure", "steps to", "install", "calibrat")
CHAT_KEYWORDS = ("hello", "hi", "thanks", "thank you", "who are you")


def plan(state: CopilotState) -> CopilotState:
    question = state["question"]

    guard = check_input(question)
    if not guard.allowed:
        state["intent"] = "blocked"
        state["blocked"] = True
        state["block_reason"] = guard.reason
        return state

    lowered = question.lower()
    if ALARM_CODE_RE.search(question):
        intent = "alarm_lookup"
    elif any(k in lowered for k in FEEDS_SPEEDS_KEYWORDS):
        intent = "feeds_and_speeds"
    elif any(k in lowered for k in PROCEDURE_KEYWORDS):
        intent = "procedure"
    elif any(k in lowered for k in CHAT_KEYWORDS):
        intent = "chat"
    else:
        intent = "procedure"  # safe default: treat unknown technical questions as retrieval-worthy

    state["intent"] = intent
    state["blocked"] = False
    return state
