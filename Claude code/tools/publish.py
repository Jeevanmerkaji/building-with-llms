"""Create a DRAFT email in Buttondown from the rendered issue. Never sends.
Usage: python tools/publish.py <slug>
Needs BUTTONDOWN_API_KEY in .env. Images must already be hosted at --image-base
(email clients need public absolute URLs); re-render with render_email.py --image-base first.
"""
import argparse
import os

import requests
from dotenv import load_dotenv

from _common import ROOT, issue_dir, load_content

load_dotenv(ROOT / ".env")


def main(slug):
    key = os.getenv("BUTTONDOWN_API_KEY")
    if not key:
        raise SystemExit("BUTTONDOWN_API_KEY missing in .env")
    d, c = issue_dir(slug), load_content(slug)
    html = (d / "email.html").read_text()
    if "file://" in html:
        raise SystemExit("email.html still has file:// image URLs; host images and re-render with --image-base")
    r = requests.post("https://api.buttondown.com/v1/emails", timeout=60,
                      headers={"Authorization": f"Token {key}"},
                      json={"subject": c["subject_variants"][0], "body": f"<!-- buttondown-editor-mode: fancy -->\n{html}",
                            "status": "draft"})
    r.raise_for_status()
    print("draft created:", r.json().get("absolute_url") or r.json().get("id"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    main(ap.parse_args().slug)
