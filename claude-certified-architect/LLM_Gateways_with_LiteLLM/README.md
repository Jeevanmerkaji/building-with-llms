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

Fill in `.env` — no spaces around `=`, no quotes (some tools, notably `docker run --env-file`, parse this strictly):

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LITELLM_MASTER_KEY=sk-litellm-local-dev
LITELLM_SALT_KEY=<a long random value>
```

`LITELLM_MASTER_KEY` isn't issued by anyone — you invent it yourself (any string; generate one with `openssl rand -hex 32`). `LITELLM_SALT_KEY` is only needed for Option C below (it encrypts provider keys stored in the database).

## Run

Two processes: start the proxy, then run the client against it. Pick one way to run the proxy — don't run both at once, they'll fight over port 4000.

### Option A: proxy via the venv CLI

```bash
# terminal 1 — the gateway itself
litellm --config config.yaml --port 4000

# terminal 2 — your application
python gateways.py
```

### Option B: proxy via Docker

No venv/Python needed for this half — Docker pulls a self-contained image with LiteLLM already installed, so nothing here touches your local Python setup. `config.yaml` is mounted in read-only; provider keys are passed as env vars, same as `.env`.

```bash
docker run -d --name litellm-proxy \
  -v "$(pwd)/config.yaml:/app/config.yaml" \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e LITELLM_MASTER_KEY="$LITELLM_MASTER_KEY" \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:latest \
  --config /app/config.yaml

# terminal 2 — your application (same either way)
python gateways.py
```

Stop it with `docker rm -f litellm-proxy`. `gateways.py` doesn't know or care which one is serving port 4000 — that's the point of routing everything through the proxy's OpenAI-compatible API.

### Option C: Docker Compose, with Postgres — needed for the admin UI

Options A and B don't have a database, which is fine for the `/chat/completions` API but breaks the browser dashboard at `http://localhost:4000/ui` — login fails with `Not connected to DB!` without one. `docker-compose.yml` adds Postgres alongside LiteLLM to fix that, matching the official ["standard deployment"](https://docs.litellm.ai/docs/proxy/docker_quick_start).

Requires the `docker compose` plugin (`sudo apt-get install docker-compose-plugin` if you don't have it).

```bash
docker compose up -d
```

First boot runs Prisma DB migrations and takes noticeably longer than Option B (a minute or so) — check readiness with:

```bash
curl http://localhost:4000/health/readiness   # {"status":"healthy","db":"connected"} once ready
```

Then log into `http://localhost:4000/ui` with username `admin` and your `LITELLM_MASTER_KEY` as the password. Stop the stack with `docker compose down` (add `-v` to also wipe the Postgres volume).

## Status

All three ways of running the proxy verified working end-to-end (including a real `claude-haiku-4-5` completion through each): the venv CLI, plain Docker, and Docker Compose with Postgres (confirmed `db":"connected"` on `/health/readiness` and successful UI-style auth). Not yet covered: caching, rate limiting, and guardrails — those are still just notes in `test.ipynb`.
