"""Word/PowerPoint loader — production stub.

Wire up with python-docx / python-pptx for Word-based service bulletins and
PowerPoint training decks. Left as a stub in this scaffold — see
DATA/service_bulletins for the markdown equivalent used in the demo index.
"""
from pathlib import Path
from typing import Iterator
from .text import RawDoc


def load_office(path: Path) -> Iterator[RawDoc]:
    raise NotImplementedError(
        "Office-doc ingestion not wired in this scaffold — "
        "hook up python-docx / python-pptx here."
    )
