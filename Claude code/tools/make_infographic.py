"""Render every infographic in content.json to SVG + PNG.

Usage: python tools/make_infographic.py <slug>
Each section may carry an `infographic` {template,title,items,unit?,alt,source}.
Writes .tmp/<slug>/img/<section-index>.svg|png
"""
import sys
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from _common import TEMPLATES, chrome_screenshot, issue_dir, load_brand, load_content

TEMPLATE_HEIGHT = {"stat_row": 520, "timeline": 460, "process": 440}


def main(slug):
    content, brand = load_content(slug), load_brand()
    env = Environment(loader=FileSystemLoader(TEMPLATES))
    img = issue_dir(slug) / "img"
    made = 0
    for i, sec in enumerate(content["sections"]):
        ig = sec.get("infographic")
        if not ig:
            continue
        tpl = env.get_template(f"{ig['template']}.svg.j2")
        svg = tpl.render(b=brand, title=ig["title"], items=ig["items"], unit=ig.get("unit", ""),
                         source_label=urlparse(ig["source"]).netloc)
        svg_path = img / f"{i}.svg"
        svg_path.write_text(svg)
        h = TEMPLATE_HEIGHT.get(ig["template"], 170 + len(ig["items"]) * 70)
        html = img / f"{i}.html"
        html.write_text(f"<body style='margin:0;background:#fff'>{svg}</body>")
        chrome_screenshot(html.as_uri(), img / f"{i}.png", 1200, h)
        html.unlink()
        made += 1
        print(f"wrote {img / f'{i}.png'}")
    print(f"{made} infographic(s) rendered")


if __name__ == "__main__":
    main(sys.argv[1])
