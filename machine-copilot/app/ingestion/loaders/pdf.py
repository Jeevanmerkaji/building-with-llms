"""PDF loader — production stub.

Wire this up with the `pdf` skill / pypdf + pdfplumber (for tables like
torque-spec charts) once real scanned manuals are available. Kept separate
from text.py because OEM manuals are frequently scanned/image-based and need
OCR (pytesseract) before chunking.
"""
from pathlib import Path
from typing import Iterator
from .text import RawDoc


def load_pdf(path: Path) -> Iterator[RawDoc]:
    raise NotImplementedError(
        "PDF ingestion not wired in this scaffold — "
        "hook up pypdf/pdfplumber (+ OCR fallback) here for real scanned manuals."
    )
