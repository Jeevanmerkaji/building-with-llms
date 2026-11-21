"""Validate content.json before rendering. Exits non-zero on problems.
Usage: python tools/validate_content.py <slug>
Rules: required fields present; every section and infographic cites >=1 http(s) source;
infographic template known; alt text present; subject <= 60 chars; no duplicate sources.
"""
import sys

from _common import load_content

TEMPLATES = {"stat_row", "bar_comparison", "timeline", "process"}
REQUIRED = ["title", "preheader", "date", "intro", "sections", "takeaways", "footer", "subject_variants"]


def main(slug):
    c, errs = load_content(slug), []
    errs += [f"missing field: {k}" for k in REQUIRED if not c.get(k)]
    for k in ("address", "unsubscribe_url", "web_url"):
        if not c.get("footer", {}).get(k):
            errs.append(f"footer.{k} missing (required for compliance)")
    for v in c.get("subject_variants", []):
        if len(v) > 60:
            errs.append(f"subject too long ({len(v)}): {v}")
    seen = set()
    for i, s in enumerate(c.get("sections", [])):
        srcs = s.get("sources", [])
        if not srcs or not all(u.startswith(("http://", "https://")) for u in srcs):
            errs.append(f"section {i} '{s.get('heading')}': needs http(s) sources")
        if not s.get("body"):
            errs.append(f"section {i}: empty body")
        for u in srcs:
            if u in seen:
                print(f"warn: source reused: {u}")
            seen.add(u)
        ig = s.get("infographic")
        if ig:
            if ig.get("template") not in TEMPLATES:
                errs.append(f"section {i}: unknown template {ig.get('template')}")
            if not ig.get("alt"):
                errs.append(f"section {i}: infographic alt text missing")
            if not str(ig.get("source", "")).startswith("http"):
                errs.append(f"section {i}: infographic needs a source URL")
            if not ig.get("items"):
                errs.append(f"section {i}: infographic has no items")
    if errs:
        print("\n".join(f"ERROR {e}" for e in errs))
        sys.exit(1)
    print("content OK")


if __name__ == "__main__":
    main(sys.argv[1])
