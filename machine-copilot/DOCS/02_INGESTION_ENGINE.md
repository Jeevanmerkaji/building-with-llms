# 02 · Ingestion Engine

`python -m app.ingestion.processor --machine Apex-3200`

## Pipeline
`DATA/` → loaders → `chunking/splitter.py` → `services/retrieval/embedding.py`
→ `services/retrieval/qdrant_service.py` (one collection per machine model,
persisted to `processed_data/<model>.pkl`).

## Loaders (`app/ingestion/loaders/`)
- `text.py` — markdown/text manuals and service bulletins.
- `json_loader.py` — structured alarm-code tables; each alarm becomes one
  atomic, retrievable chunk rather than a fragment of prose.
- `pdf.py`, `office.py` — stubs. Wire up `pypdf`/`pdfplumber` (+ OCR for
  scanned manuals) and `python-docx`/`python-pptx` here for real OEM
  document sets; the demo dataset uses markdown equivalents instead.

## Chunking (`app/ingestion/chunking/splitter.py`)
Manual/bulletin text splits on markdown headers (`##`/`###`) so a chunk
never straddles two unrelated procedures — merging "torque spec" from one
procedure with "warm-up time" from another is exactly how you get a
wrong-but-plausible answer. Alarm-code records pass through unsplit; they're
already atomic.

## Embedding & retrieval (`app/services/retrieval/`)
- `embedding.py` — a local TF-IDF vectorizer by default. Runs with zero
  network calls (important on an offline shop floor) and handles exact
  lexical matches (alarm codes, part numbers) well. Swap in a semantic
  embedding provider by implementing the same `fit_transform`/`transform`
  interface — nothing else in the pipeline needs to change.
- `qdrant_service.py` — named for the interface shape a production
  deployment would use, implemented here as a local disk-persisted store so
  the whole system runs with no external services. `search()`/`add()` are
  the only methods the rest of the app depends on, so swapping to real
  Qdrant means replacing this file's internals only.
- `ranking_service.py` — deterministic rerank: any query containing a
  code-shaped token (`ALM-4021`, `SB-2024-011`) boosts chunks containing an
  exact match to the top, regardless of raw cosine similarity.

## Adding a new machine model
1. Drop its manuals/bulletins/alarm tables into `DATA/`.
2. Run `python -m app.ingestion.processor --machine <Model Name>`.
3. Set `MACHINE_MODEL=<Model Name>` in `.env`, or pass it per-request via the
   API's `machine_model` field.
