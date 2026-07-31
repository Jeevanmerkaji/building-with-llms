"""
Central configuration for Machine Copilot.

All values are overridable via environment variables (see .env.example).
Designed so a plant with no internet access can run in OFFLINE_MODE with
zero external calls, while a connected site can enable the cloud fallback.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class Settings:
    # --- Identity ---
    machine_model: str = os.getenv("MACHINE_MODEL", "Apex-3200")

    # --- Data paths ---
    data_dir: Path = BASE_DIR / "DATA"
    processed_dir: Path = BASE_DIR / "processed_data"

    # --- LLM Gateway ---
    # If no ANTHROPIC_API_KEY is set, the gateway automatically falls back
    # to a deterministic, fully-offline templated responder so the system
    # still functions on an air-gapped shop floor.
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    primary_model: str = os.getenv("PRIMARY_MODEL", "claude-sonnet-4-6")
    offline_mode: bool = os.getenv("OFFLINE_MODE", "false").lower() == "true"

    # --- Retrieval ---
    top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    rerank_top_n: int = int(os.getenv("RERANK_TOP_N", "3"))

    # --- Guardrails ---
    # Hard block list of terms that indicate a request to bypass a physical
    # safety interlock. This list is intentionally simple and auditable —
    # extend it via colang_rules.py rather than hiding logic in the model.
    blocked_intents: tuple = (
        "bypass the interlock",
        "disable the e-stop",
        "override the safety door",
        "defeat the light curtain",
        "remove the guard",
        "disable limit switch",
    )

    # --- Telemetry ---
    telemetry_poll_seconds: float = float(os.getenv("TELEMETRY_POLL_SECONDS", "2.0"))


settings = Settings()
