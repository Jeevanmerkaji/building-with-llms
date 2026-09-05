# Claude Certified Architect

Notes and exercises from working through Claude/Anthropic architecture material — a tool-use agentic loop and a set of notes on LLM gateways.

## Contents

- [`agent.py`](agent.py) — a single-agent tool-use loop against the Anthropic Messages API. Defines a `lookup_order` tool, dispatches tool calls through `execute_tool`, and classifies failures into `transient` / `permission` / `validation` / `internal` categories in `handle_tool_call` so the model knows whether to retry, self-correct, or escalate.
- [`LLM_Gateways_with_LiteLLM/`](LLM_Gateways_with_LiteLLM/) — notes on LLM gateway concepts (routing, fallback, caching, rate limiting, guardrails, cost tracking, observability, evals) with [LiteLLM](https://github.com/BerriAI/litellm) as the example gateway.
  - `test.ipynb` — write-up notebook covering the above concepts.
  - `gateways.py` — a minimal working example: a `chat()` helper that calls `litellm.completion()` with a primary model and a fallback list.

## Prerequisites

- Python 3.9+
- An Anthropic API key

## Run

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python agent.py
```

The script uses `claude-haiku-4.5` and a mocked order-lookup tool, so no external backend is required.

## Status

`agent.py` runs without crashing, but the tool name in the `tools` schema (`lookuo_order`) doesn't match the name checked in `execute_tool` (`lookup_order`), so every call currently falls into the "unknown tool" branch — fix the typo to get a real lookup result. `LLM_Gateways_with_LiteLLM/` has its own `uv`-managed environment (Python 3.11.13, `.venv`) — see its [README](LLM_Gateways_with_LiteLLM/README.md) for setup.
