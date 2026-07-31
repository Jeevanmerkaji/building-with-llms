"""Loader for plain text and markdown source documents (manuals, bulletins)."""
from pathlib import Path
from typing import Iterator, TypedDict


class RawDoc(TypedDict):
    doc_id: str
    source: str
    text: str
    doc_type: str


def load_markdown_or_text(path: Path) -> Iterator[RawDoc]:
    """Yield one RawDoc per file. Markdown headers are preserved so the
    chunker can split on section boundaries rather than arbitrary length."""
    text = path.read_text(encoding="utf-8")
    yield RawDoc(
        doc_id=path.stem,
        source=path.name,
        text=text,
        doc_type="manual" if "manual" in path.name else "bulletin",
    )
