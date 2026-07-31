# Machine Copilot

An embedded, retrieval-grounded AI assistant shipped with every CNC machine.
Answers alarm, feeds/speeds, and maintenance questions using only the
manufacturer's own manuals, alarm tables, and service bulletins — with
safety guardrails and a mandatory eval gate before any release ships.

Built as a working scaffold: real ingestion, real retrieval + reranking, a
real LangGraph agent, real guardrails, a real (if simulated) telemetry +
predictive-maintenance layer, and three functioning UIs. Swap the stubs
noted below for production integrations (real PDF/OCR parsing, a hosted
vector DB, a live PLC feed) without changing the surrounding architecture.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optionally add ANTHROPIC_API_KEY for cloud fallback

# 1. Build the knowledge base from DATA/
python -m app.ingestion.processor --machine Apex-3200

# 2. Run the release-gate eval suite
python -m evals.pipeline

# 3. Start the API
uvicorn app.main:app --reload --port 8000

# 4. Try the UIs (in separate terminals)
streamlit run ui/hmi_chat.py            # shop-floor kiosk chat
streamlit run ui/technician_app.py      # field technician tablet app
streamlit run ui/fleet_dashboard.py     # plant-manager fleet view
streamlit run evals/app.py              # internal QA / release-gate dashboard
```

## Try it via the API directly

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What should I check for alarm ALM-4021?"}'

curl -X POST http://127.0.0.1:8000/telemetry/analyze \
  -H "Content-Type: application/json" \
  -d '{"wear_mode": true}'
```

## Project structure

```
machine-copilot/
├── app/                # core service — agents, gateway, guardrails, ingestion, retrieval, telemetry
├── evals/              # golden dataset + guardrail probes = release gate
├── ui/                 # 3 Streamlit surfaces: HMI chat, technician app, fleet dashboard
├── DATA/                # source manuals, alarm codes, service bulletins (sample data for Apex-3200)
├── processed_data/      # generated vector indexes (git-ignored in a real repo)
├── DOCS/                # architecture docs, one per subsystem
├── requirements.txt / requirements-prod.txt
├── Dockerfile           # edge-deployable image
└── .env.example
```

See `DOCS/01_SYSTEM_OVERVIEW.md` for the full architecture walkthrough, and
`DOCS/05_GUARDRAILS_AND_SAFETY_CASE.md` before making any safety/liability
claim about the product.

## What's stubbed vs. real in this scaffold

| Piece | Status |
|---|---|
| Ingestion (markdown/JSON) | Real — tested end-to-end |
| PDF/Office ingestion | Stubbed — see `app/ingestion/loaders/pdf.py`, `office.py` |
| Retrieval + reranking | Real (local TF-IDF + cosine similarity); swap embedder for a semantic model in production |
| Vector store | Real, local/disk-persisted; swap for hosted Qdrant in production |
| Agent graph (LangGraph) | Real |
| Guardrails | Real, rule-based (Python, not Colang) |
| LLM gateway | Real — calls Claude if `ANTHROPIC_API_KEY` is set, else a fully offline templated fallback |
| Telemetry | Simulated stream; `plc_listener.py` documents the real PLC/OPC-UA integration point |
| Eval suite | Real, 7/7 passing on the sample dataset, guardrail probes all blocked |

## License
MIT — see the [repository LICENSE](../LICENSE).
