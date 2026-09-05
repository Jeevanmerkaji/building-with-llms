# LLM Gateways with LiteLLM

Notes and a minimal working example on LLM gateway concepts, using [LiteLLM](https://github.com/BerriAI/litellm) as the gateway — run as a **local proxy server** so the application only ever needs one key.

## Contents

- `test.ipynb` — notes on what a gateway does (routing, fallback, caching, rate limiting, guardrails, cost tracking, observability, evals) and what LiteLLM specifically offers.
- `config.yaml` — proxy config: maps model names to providers, holds provider keys (server-side only), and configures a fallback (`claude-haiku-4-5` → `gpt-4o-mini`).
- `gateways.py` — the application side: a `chat()` helper that calls the running proxy through the `openai` SDK, using only `LITELLM_MASTER_KEY`.

## How the single-key setup works

- **Provider keys** (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) live only in `.env`, read by the **proxy** (`config.yaml`). Application code never touches them.
- **`LITELLM_MASTER_KEY`** is the only key `gateways.py` uses. Adding or swapping a provider means editing `config.yaml`, not application code.

## Setup

This folder has its own `uv`-managed environment (Python 3.11.13, pinned in `.python-version`).

```bash
uv venv --python 3.11.13
source .venv/bin/activate
uv pip install -r requirements.txt
```

Fill in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LITELLM_MASTER_KEY=sk-litellm-local-dev   # any string, for local dev
```

## Run

Two processes: start the proxy, then run the client against it.

```bash
# terminal 1 — the gateway itself
litellm --config config.yaml --port 4000

# terminal 2 — your application
python gateways.py
```

## Status

Proxy config verified to boot cleanly and register both models (`litellm --config config.yaml` → `/health/liveliness` returns 200). Not yet covered: caching, rate limiting, and guardrails — those are still just notes in `test.ipynb`.
