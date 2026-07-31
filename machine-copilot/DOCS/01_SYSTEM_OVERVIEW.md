# 01 · System Overview

Machine Copilot is an embedded, retrieval-grounded AI assistant shipped with
every CNC machine. It answers operator and technician questions about alarm
codes, feeds/speeds, and maintenance procedures using only the manufacturer's
own manuals, alarm tables, and service bulletins — never open-internet
knowledge.

## Request flow

1. A question arrives via one of the three UIs (`ui/hmi_chat.py`,
   `ui/technician_app.py`) or the API directly.
2. `app/main.py` passes it into the LangGraph agent (`app/agents/graph.py`).
3. **Planner** classifies intent and runs the input guardrail
   (safety-bypass detection) before anything else happens.
4. **Retriever** queries the machine-model-specific vector collection and
   reranks so exact alarm-code matches always outrank fuzzy prose matches.
5. **Responder** calls the LLM gateway (cloud model if reachable, local
   templated fallback if not) and runs the output guardrail — any numeric
   technical claim not present in the retrieved source text blocks the
   response rather than shipping a possibly-invented spec.
6. The answer returns with citations back to the exact source file.

## Why this shape

Every design choice traces back to one constraint: **a wrong answer here can
damage a machine or hurt someone**, not just annoy a user. That's why:
- Guardrails run on both input and output, not just output.
- Retrieval is grounded in the manufacturer's own documents, not the model's
  training data.
- The eval suite (`evals/pipeline.py`) is a hard release gate, not an
  optional metric.
- The whole stack degrades gracefully to a fully offline mode rather than
  failing silently when a shop floor has no internet.

See `04_TELEMETRY_AND_PREDICTIVE_MAINTENANCE.md` and
`05_GUARDRAILS_AND_SAFETY_CASE.md` for the two pieces that don't exist in a
generic document-RAG system and are the actual product differentiators here.
