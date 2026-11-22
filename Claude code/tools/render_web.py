"""Render content.json -> web.html.  Usage: python tools/render_web.py <slug> [--image-base URL]"""
import argparse

from jinja2 import Environment, FileSystemLoader

from _common import TEMPLATES, issue_dir, load_brand, load_content


def main(slug, image_base):
    d = issue_dir(slug)
    html = Environment(loader=FileSystemLoader(TEMPLATES)).get_template("web.html.j2").render(
        c=load_content(slug), b=load_brand(), image_base=(image_base or "img").rstrip("/"))
    (d / "web.html").write_text(html)
    print(f"wrote {d / 'web.html'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--image-base")
    a = ap.parse_args()
    main(a.slug, a.image_base)
