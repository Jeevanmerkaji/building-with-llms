"""Screenshot email.html and web.html at desktop and mobile widths for visual QA.
Usage: python tools/preview.py <slug>   -> .tmp/<slug>/preview-*.png
"""
import sys

from _common import chrome_screenshot, issue_dir

SHOTS = [("email.html", "email-desktop", 700, 2600), ("email.html", "email-mobile", 390, 4200),
         ("web.html", "web-desktop", 1200, 3200), ("web.html", "web-mobile", 390, 5200)]


def main(slug):
    d = issue_dir(slug)
    for src, name, w, h in SHOTS:
        if (d / src).exists():
            out = d / f"preview-{name}.png"
            chrome_screenshot((d / src).as_uri(), out, w, h)
            print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1])
