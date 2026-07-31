"""Conversation state passed through the LangGraph nodes.

Keeps per-machine context (model, recent alarm history) alongside the
per-turn fields, so the Planner/Retriever/Responder nodes always have
enough context to ground an answer to *this* machine, not a generic one.
"""
from typing import TypedDict, Literal, Optional


Intent = Literal["alarm_lookup", "feeds_and_speeds", "procedure", "chat", "blocked"]


class CopilotState(TypedDict, total=False):
    machine_id: str
    machine_model: str
    thread_id: str

    question: str
    intent: Intent

    retrieved_chunks: list[dict]
    reranked_chunks: list[dict]

    answer: str
    citations: list[str]
    blocked: bool
    block_reason: Optional[str]
