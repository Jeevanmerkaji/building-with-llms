"""Reranker.

TF-IDF cosine similarity alone can let a fuzzy prose match outrank an exact
alarm-code hit. This reranker applies a deterministic boost when the query
contains a token that exactly matches an alarm code or part number pattern
(e.g. "ALM-4021", "SB-2024-011") — mirroring the "exact code beats fuzzy
text" requirement from the architecture doc.
"""
import re
from .qdrant_service import Chunk

CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}-\d{3,4}(?:-\d+)?)\b")


def rerank(query: str, results: list[tuple[Chunk, float]], top_n: int = 3) -> list[tuple[Chunk, float]]:
    query_codes = set(CODE_PATTERN.findall(query.upper()))
    boosted = []
    for chunk, score in results:
        boost = 0.0
        if query_codes:
            chunk_codes = set(CODE_PATTERN.findall(chunk.text.upper()))
            if query_codes & chunk_codes:
                boost = 1.0  # guarantee exact-code chunk sorts to the top
        if chunk.doc_type == "alarm_code" and query_codes:
            boost += 0.25
        boosted.append((chunk, score + boost))
    boosted.sort(key=lambda pair: pair[1], reverse=True)
    return boosted[:top_n]
