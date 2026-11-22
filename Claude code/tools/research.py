"""Research a topic via Tavily -> .tmp/<slug>/research.json
Usage: python tools/research.py "<topic>" [--queries q1 q2 ...] [--days 30] [--max 6]
Defaults to 4 angle queries derived from the topic. Needs TAVILY_API_KEY in .env.
Each Tavily search call uses API credits.
"""
import argparse
import json
import os

import requests
from dotenv import load_dotenv

from _common import ROOT, issue_dir, slugify

load_dotenv(ROOT / ".env")


def search(query, days, max_results, key):
    r = requests.post("https://api.tavily.com/search", timeout=60, json={
        "api_key": key, "query": query, "topic": "news" if days else "general", "days": days,
        "max_results": max_results, "search_depth": "advanced", "include_answer": False})
    r.raise_for_status()
    return r.json().get("results", [])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--queries", nargs="*")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--max", type=int, default=6)
    a = ap.parse_args()
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise SystemExit("TAVILY_API_KEY missing in .env")
    queries = a.queries or [f"{a.topic} latest developments", f"{a.topic} statistics data",
                            f"{a.topic} expert analysis", f"{a.topic} risks challenges"]
    seen, out = set(), []
    for q in queries:
        for res in search(q, a.days, a.max, key):
            if res["url"] in seen:
                continue
            seen.add(res["url"])
            out.append({"query": q, "title": res.get("title"), "url": res["url"],
                        "published": res.get("published_date"), "score": res.get("score"),
                        "content": res.get("content")})
    slug = slugify(a.topic)
    path = issue_dir(slug) / "research.json"
    path.write_text(json.dumps({"topic": a.topic, "results": out}, indent=2))
    print(f"{len(out)} sources from {len(queries)} queries -> {path}\nslug: {slug}")


if __name__ == "__main__":
    main()
