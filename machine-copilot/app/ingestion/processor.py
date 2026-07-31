"""CLI: parse DATA/ -> chunk -> embed -> index, one collection per machine model.

Usage:
    python -m app.ingestion.processor --machine Apex-3200
"""
import argparse
import json
from pathlib import Path

from app.config import settings
from app.ingestion.loaders.text import load_markdown_or_text
from app.ingestion.loaders.json_loader import load_json_records
from app.ingestion.chunking.splitter import split_document
from app.services.retrieval.qdrant_service import VectorStore


def gather_raw_docs():
    docs = []
    for path in (settings.data_dir / "manuals").glob("*.md"):
        docs.extend(load_markdown_or_text(path))
    for path in (settings.data_dir / "service_bulletins").glob("*.md"):
        docs.extend(load_markdown_or_text(path))
    for path in (settings.data_dir / "alarm_codes").glob("*.json"):
        docs.extend(load_json_records(path))
    return docs


def run(machine_model: str) -> dict:
    raw_docs = gather_raw_docs()
    all_chunks = []
    for doc in raw_docs:
        all_chunks.extend(split_document(doc))

    store = VectorStore(collection_name=machine_model.lower().replace(" ", "_"), persist_dir=settings.processed_dir)
    store.build([{"chunk_id": c["chunk_id"], "source": c["source"], "doc_type": c["doc_type"], "text": c["text"]} for c in all_chunks])
    store.save()

    # also dump a human-readable JSON of the chunk set for debugging/audit
    debug_path = settings.processed_dir / f"{store.collection_name}_chunks.json"
    debug_path.write_text(json.dumps(all_chunks, indent=2), encoding="utf-8")

    summary = {
        "machine_model": machine_model,
        "documents_loaded": len(raw_docs),
        "chunks_indexed": len(all_chunks),
        "collection": store.collection_name,
        "index_path": str(store._path),
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", default=settings.machine_model)
    args = parser.parse_args()
    run(args.machine)
