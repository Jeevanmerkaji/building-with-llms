"""Retriever node — queries the machine-specific vector store and reranks.
Skipped entirely for 'chat' intent (no point retrieving for "thanks!")."""
from pathlib import Path

from app.agents.state import CopilotState
from app.config import settings
from app.services.retrieval.qdrant_service import VectorStore
from app.services.retrieval.ranking_service import rerank

_store_cache: dict[str, VectorStore] = {}


def _get_store(machine_model: str) -> VectorStore:
    collection = machine_model.lower().replace(" ", "_")
    if collection not in _store_cache:
        store = VectorStore(collection_name=collection, persist_dir=settings.processed_dir)
        store.load()
        _store_cache[collection] = store
    return _store_cache[collection]


def retrieve(state: CopilotState) -> CopilotState:
    if state.get("intent") == "chat" or state.get("blocked"):
        state["retrieved_chunks"] = []
        state["reranked_chunks"] = []
        return state

    store = _get_store(state["machine_model"])
    results = store.search(state["question"], top_k=settings.top_k)
    reranked = rerank(state["question"], results, top_n=settings.rerank_top_n)

    state["retrieved_chunks"] = [{"chunk_id": c.chunk_id, "source": c.source, "text": c.text, "score": s} for c, s in results]
    state["reranked_chunks"] = [{"chunk_id": c.chunk_id, "source": c.source, "text": c.text, "score": s} for c, s in reranked]
    return state
