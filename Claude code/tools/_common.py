"""Shared helpers for the newsletter tools."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".tmp"
TEMPLATES = Path(__file__).resolve().parent / "templates"
CHROME = "google-chrome"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def issue_dir(slug):
    d = TMP / slug
    (d / "img").mkdir(parents=True, exist_ok=True)
    return d


def load_content(slug):
    return json.loads((issue_dir(slug) / "content.json").read_text())


def load_brand():
    return json.loads((TEMPLATES / "brand.json").read_text())


def chrome_screenshot(url, out, width, height):
    """Headless Chrome screenshot of a file:// or http(s) URL."""
    subprocess.run(
        [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--window-size={width},{height}", f"--screenshot={out}", url],
        check=True, capture_output=True, timeout=60,
    )
