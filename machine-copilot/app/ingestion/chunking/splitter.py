"""Chunking tuned for maintenance/service content.

Two strategies:
  - alarm_code docs are already atomic (one alarm = one chunk) — passed through.
  - manual/bulletin docs are split on markdown headers (## / ###) so a chunk
    never straddles two unrelated procedures. This matters more here than in
    generic RAG: a chunk that merges "torque spec" from one procedure with
    "warm-up time" from another is how you get a wrong-but-plausible answer.
"""
import re
from typing import Iterator
from ..loaders.text import RawDoc

HEADER_RE = re.compile(r"^(#{2,3})\s+(.*)$", re.MULTILINE)


def split_document(doc: RawDoc, max_chars: int = 900) -> Iterator[dict]:
    if doc["doc_type"] == "alarm_code":
        yield {
            "chunk_id": doc["doc_id"],
            "source": doc["source"],
            "doc_type": doc["doc_type"],
            "text": doc["text"],
        }
        return

    text = doc["text"]
    matches = list(HEADER_RE.finditer(text))
    if not matches:
        # no headers — fall back to fixed-size chunks
        for i in range(0, len(text), max_chars):
            piece = text[i : i + max_chars].strip()
            if piece:
                yield {
                    "chunk_id": f"{doc['doc_id']}::{i}",
                    "source": doc["source"],
                    "doc_type": doc["doc_type"],
                    "text": piece,
                }
        return

    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section = text[start:end].strip()
        if not section:
            continue
        # further split if a section is unusually long
        if len(section) <= max_chars * 1.5:
            yield {
                "chunk_id": f"{doc['doc_id']}::{idx}",
                "source": doc["source"],
                "doc_type": doc["doc_type"],
                "text": section,
            }
        else:
            for j in range(0, len(section), max_chars):
                piece = section[j : j + max_chars].strip()
                if piece:
                    yield {
                        "chunk_id": f"{doc['doc_id']}::{idx}.{j}",
                        "source": doc["source"],
                        "doc_type": doc["doc_type"],
                        "text": piece,
                    }
