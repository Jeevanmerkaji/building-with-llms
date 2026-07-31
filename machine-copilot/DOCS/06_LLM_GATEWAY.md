# 06 · LLM Gateway

`app/gateway/client.py` — the piece that matters most for uptime on a
factory floor.

## Routing logic
1. If `OFFLINE_MODE=true` or no `ANTHROPIC_API_KEY` is set, go straight to
   the local templated fallback — an extractive, no-network answer built
   only from retrieved chunks. Guaranteed to work air-gapped.
2. Otherwise, call the cloud model (`PRIMARY_MODEL`, default
   `claude-sonnet-4-6`) with the retrieved context and the question.
3. Any exception (network blip, bad key, rate limit) falls back to the same
   offline path rather than surfacing an error to the operator — the
   assistant should degrade gracefully, never go silent.

## Why this matters more here than in a typical SaaS RAG app
A generic chatbot going down for five minutes is an inconvenience. A shop
floor assistant going silent mid-shift, with no offline fallback, either
gets ignored forever afterward or (worse) gets a workaround built around it.
The offline fallback is what lets you sell the Base tier as "works with zero
setup, zero internet dependency" and still upsell the Pro tier's cloud
reasoning on top.

## Extending
Add a second model provider (e.g. a self-hosted small model on an edge box)
by branching inside `generate()` on a new config flag — the call sites in
`app/agents/nodes/responder.py` don't need to know which provider answered.
