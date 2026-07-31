"""Loader for structured alarm-code tables (JSON). Each alarm becomes its
own retrievable record so an exact code match is a single, precise chunk
rather than a fragment of a longer prose block."""
import json
from pathlib import Path
from typing import Iterator
from .text import RawDoc


def load_json_records(path: Path) -> Iterator[RawDoc]:
    records = json.loads(path.read_text(encoding="utf-8"))
    for rec in records:
        text = (
            f"Alarm {rec['code']} — {rec['title']}\n"
            f"Severity: {rec['severity']}\n"
            f"Description: {rec['description']}\n"
            f"Recommended action: {rec['recommended_action']}"
        )
        yield RawDoc(
            doc_id=f"{path.stem}::{rec['code']}",
            source=rec.get("source", path.name),
            text=text,
            doc_type="alarm_code",
        )
