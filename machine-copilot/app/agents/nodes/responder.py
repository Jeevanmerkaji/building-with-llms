"""Responder node — generates the final answer via the LLM gateway, then
runs the output guardrail before returning. Every answer carries citations
back to the specific source file each chunk came from."""
from app.agents.state import CopilotState
from app.gateway.client import generate
from app.guardrails.rails import check_output

SYSTEM_PROMPT = (
    "You are Machine Copilot, an assistant embedded in a CNC machine's "
    "control software. You answer operator and technician questions about "
    "alarms, feeds/speeds, and maintenance procedures. Ground every answer "
    "strictly in the retrieved source material you are given — never invent "
    "a numeric spec (RPM, torque, temperature, feed rate) that isn't present "
    "in that material. If the material doesn't cover the question, say so "
    "plainly and suggest contacting a qualified technician."
)


def respond(state: CopilotState) -> CopilotState:
    if state.get("blocked"):
        state["answer"] = state.get("block_reason", "This request can't be completed.")
        state["citations"] = []
        return state

    if state.get("intent") == "chat":
        state["answer"] = (
            "Hi — I'm Machine Copilot for your " + state.get("machine_model", "CNC machine") +
            ". Ask me about alarm codes, feeds and speeds, or maintenance procedures."
        )
        state["citations"] = []
        return state

    chunks = state.get("reranked_chunks", [])
    context_texts = [c["text"] for c in chunks]
    answer = generate(state["question"], context_texts, SYSTEM_PROMPT)

    source_context = "\n".join(context_texts)
    guard = check_output(answer, source_context)
    if not guard.allowed:
        state["answer"] = guard.reason
        state["citations"] = []
        state["blocked"] = True
        return state

    state["answer"] = answer
    state["citations"] = sorted({c["source"] for c in chunks})
    return state
