"""Render content.json -> email.html (MJML) + email.txt.

Usage: python tools/render_email.py <slug> [--image-base URL]
Without --image-base, images use file:// paths (local preview only). For publishing,
pass the public URL prefix where img/*.png are hosted.
"""
import argparse
import re
import subprocess

from jinja2 import Environment, FileSystemLoader

from _common import ROOT, TEMPLATES, issue_dir, load_brand, load_content


def main(slug, image_base):
    c, b = load_content(slug), load_brand()
    d = issue_dir(slug)
    image_base = image_base or (d / "img").as_uri()
    mjml = Environment(loader=FileSystemLoader(TEMPLATES)).get_template("email.mjml.j2").render(
        c=c, b=b, image_base=image_base.rstrip("/"))
    (d / "email.mjml").write_text(mjml)
    r = subprocess.run([str(ROOT / "node_modules/.bin/mjml"), str(d / "email.mjml"), "-o", str(d / "email.html")],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"mjml failed:\n{r.stderr or r.stdout}")
    lines = [c["title"], "", c["intro"], ""]
    for s in c["sections"]:
        lines += [s["heading"].upper(), *s["body"], *[f"- {x}" for x in s.get("bullets", [])], ""]
        lines += [f"Source: {u}" for u in s.get("sources", [])] + [""]
    lines += ["KEY TAKEAWAYS"] + [f"{i}. {t}" for i, t in enumerate(c["takeaways"], 1)]
    lines += ["", f"View online: {c['footer']['web_url']}", f"Unsubscribe: {c['footer']['unsubscribe_url']}", c["footer"]["address"]]
    (d / "email.txt").write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(lines)))
    print(f"wrote {d / 'email.html'} and email.txt")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--image-base")
    a = ap.parse_args()
    main(a.slug, a.image_base)
