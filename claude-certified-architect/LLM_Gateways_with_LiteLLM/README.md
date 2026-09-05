# LLM Gateways with LiteLLM

Notes and a minimal working example on LLM gateway concepts, using [LiteLLM](https://github.com/BerriAI/litellm) as the gateway.

## Contents

- `test.ipynb` — notes on what a gateway does (routing, fallback, caching, rate limiting, guardrails, cost tracking, observability, evals) and what LiteLLM specifically offers (unified OpenAI-compatible API, streaming, tool calls, fallbacks).
- `gateways.py` — a `chat()` helper that calls `litellm.completion()` against a primary model with a fallback model list.

## Setup

This folder has its own `uv`-managed environment (Python 3.11.13, pinned in `.python-version`).

```bash
uv venv --python 3.11.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

Add your provider keys to `.env` (LiteLLM calls providers directly, so use their own keys — no separate gateway key needed):

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

## Run

```bash
python gateways.py
```

## Status

Notes and a minimal `chat()` example are in place. Not yet covered: caching, rate limiting, and guardrails — those are still just notes in `test.ipynb`.
