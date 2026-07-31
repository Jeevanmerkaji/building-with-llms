# 03 · Node Intelligence (LangGraph agent core)

`app/agents/graph.py` wires three nodes in sequence: **Planner → Retriever →
Responder**. Every question — including blocked ones — flows through all
three so the audit trail is complete and uniform.

## Planner (`app/agents/nodes/planner.py`)
Classifies intent with deterministic keyword heuristics, not an LLM call —
the label set is small (`alarm_lookup`, `feeds_and_speeds`, `procedure`,
`chat`, `blocked`) and keeping it deterministic makes routing behavior easy
to test and audit. Also runs `check_input()` here, before retrieval or
generation ever happen — a safety-bypass question is refused before it
touches the knowledge base or the model.

## Retriever (`app/agents/nodes/retriever.py`)
Looks up the machine-model-specific `VectorStore`, searches, then reranks.
Skipped for `chat` intent and for blocked questions — no point retrieving
context for "thanks!" or for a refused request.

## Responder (`app/agents/nodes/responder.py`)
Calls the LLM gateway with a system prompt that explicitly instructs the
model to ground every answer in the retrieved material and say so plainly
if the material doesn't cover the question. Runs `check_output()` afterward
— any numeric claim not traceable to the retrieved text blocks the response.
Citations are attached from the actual source filenames of the chunks used.

## State (`app/agents/state.py`)
`CopilotState` carries per-machine identity (`machine_id`, `machine_model`)
alongside per-turn fields, so every node has enough context to ground an
answer to *this specific machine* rather than a generic one of that model.
