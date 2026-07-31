"""Vector store service.

Named `qdrant_service` to match the interface shape a production deployment
would use (one collection per machine model/family), but implemented here as
a local, disk-persisted store (pickle + scipy sparse matrix) so the whole
system runs with zero external services for the demo/edge case.

Swapping to real Qdrant in production means replacing the body of this class
with `qdrant_client` calls — `search()` and `add()` are the only two methods
the rest of the app depends on.
"""
from __future__ import annotations
import pickle
from pathlib import Path
from dataclasses import dataclass, field

from sklearn.metrics.pairwise import cosine_similarity

from .embedding import LocalTfidfEmbedder


@dataclass
class Chunk:
    chunk_id: str
    source: str
    doc_type: str
    text: str


class VectorStore:
    """One VectorStore instance = one collection = one machine model."""

    def __init__(self, collection_name: str, persist_dir: Path):
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedder = LocalTfidfEmbedder()
        self.chunks: list[Chunk] = []
        self.matrix = None

    @property
    def _path(self) -> Path:
        return self.persist_dir / f"{self.collection_name}.pkl"

    def build(self, chunks: list[dict]) -> None:
        """Fit the embedder and index a full set of chunks (fresh ingestion run)."""
        self.chunks = [Chunk(**c) for c in chunks]
        texts = [c.text for c in self.chunks]
        self.matrix = self.embedder.fit_transform(texts)

    def save(self) -> None:
        with open(self._path, "wb") as f:
            pickle.dump({"embedder": self.embedder, "chunks": self.chunks, "matrix": self.matrix}, f)

    def load(self) -> bool:
        if not self._path.exists():
            return False
        with open(self._path, "rb") as f:
            state = pickle.load(f)
        self.embedder = state["embedder"]
        self.chunks = state["chunks"]
        self.matrix = state["matrix"]
        return True

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if self.matrix is None:
            raise RuntimeError(
                f"Collection '{self.collection_name}' is empty — run "
                f"`python -m app.ingestion.processor` first."
            )
        q_vec = self.embedder.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        ranked_idx = sims.argsort()[::-1][:top_k]
        return [(self.chunks[i], float(sims[i])) for i in ranked_idx]
