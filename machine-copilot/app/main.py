"""FastAPI entrypoint — /query for the copilot, /telemetry for fleet signals.

Run with: uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.graph import run_query
from app.telemetry.plc_listener import simulate_stream
from app.telemetry.predictive_signals import analyze_window
from app.config import settings

app = FastAPI(title="Machine Copilot API", version="0.1.0")


class QueryRequest(BaseModel):
    question: str
    machine_id: str = "M-101"
    machine_model: str = settings.machine_model
    thread_id: str = "default"


class QueryResponse(BaseModel):
    answer: str
    citations: list[str]
    intent: str
    blocked: bool


class TelemetryRequest(BaseModel):
    machine_id: str = "M-101"
    window_size: int = 40
    wear_mode: bool = False


@app.get("/health")
def health():
    return {"status": "ok", "machine_model": settings.machine_model, "offline_mode": settings.offline_mode}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    state = run_query(
        question=req.question,
        machine_id=req.machine_id,
        machine_model=req.machine_model,
        thread_id=req.thread_id,
    )
    return QueryResponse(
        answer=state.get("answer", ""),
        citations=state.get("citations", []),
        intent=state.get("intent", "unknown"),
        blocked=state.get("blocked", False),
    )


@app.post("/telemetry/analyze")
def telemetry_analyze(req: TelemetryRequest):
    events = list(simulate_stream(req.machine_id, req.window_size, wear_mode=req.wear_mode))
    return analyze_window(events)
