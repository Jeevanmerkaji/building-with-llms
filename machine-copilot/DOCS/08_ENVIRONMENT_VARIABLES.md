# 08 · Environment Variables

See `.env.example` for the full list with defaults. Summary:

| Variable | Default | Purpose |
|---|---|---|
| `MACHINE_MODEL` | `Apex-3200` | Which machine model this instance serves — must match a `processed_data/<model>.pkl` collection built by the ingestion pipeline. |
| `ANTHROPIC_API_KEY` | *(blank)* | Enables the cloud-fallback model. Left blank, the gateway runs fully offline via the local templated responder. |
| `PRIMARY_MODEL` | `claude-sonnet-4-6` | Model used when the cloud gateway is reachable. |
| `OFFLINE_MODE` | `false` | Force the offline code path even with a key present — useful for testing air-gapped behavior or sites with a no-outbound-internet policy. |
| `RETRIEVAL_TOP_K` | `5` | Chunks pulled from the vector store before reranking. |
| `RERANK_TOP_N` | `3` | Chunks kept after reranking, passed to the responder as context. |
| `TELEMETRY_POLL_SECONDS` | `2.0` | Simulated telemetry poll interval — production replaces this with the real PLC/OPC-UA event cadence. |
