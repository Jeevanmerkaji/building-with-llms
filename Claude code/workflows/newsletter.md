# Newsletter Automation

## Objective
Given a topic, produce a researched, cited newsletter as (a) email-safe HTML, (b) a web-archive page, (c) 2-4 infographics, then create an ESP **draft**. Never send without explicit user approval.

## Inputs (confirm with user if missing)
topic, audience, tone, length (default ~600-900 words, 3-5 sections), must-include sources, delivery (email draft / web / both).

## Tools (all in `tools/`, run from `tools/` with `.venv` active: `. .venv/bin/activate`)
| Step | Command | Output (`.tmp/<slug>/`) |
|---|---|---|
| 1 Research | `python research.py "<topic>" [--queries ...] [--days N]` | `research.json` (uses Tavily credits; ~4 searches per run, tell user before running) |
| 2 Write | Claude authors `content.json` (schema: `tools/fixtures/sample_content.json`) | `content.json` |
| 3 Validate | `python validate_content.py <slug>` | exit 0 required |
| 4 Infographics | `python make_infographic.py <slug>` | `img/<section#>.png` |
| 5 Render | `python render_email.py <slug> [--image-base URL]`, `python render_web.py <slug>` | `email.html`, `email.txt`, `web.html` |
| 6 QA | `python preview.py <slug>`, then view `preview-*.png` | screenshots |
| 7 Draft | host images, re-render email with `--image-base`, `python publish.py <slug>` | Buttondown draft |

## Writing rules
- Every section and every infographic carries source URL(s) taken from `research.json`. Never invent a statistic; if research lacks a number, leave the infographic out.
- Infographic templates: `stat_row` (2-4 big numbers), `bar_comparison` (numeric items, `unit`), `timeline` (when/what), `process` (title/desc steps, <=4). Keep labels short (<=24 chars). Always give `alt` text.
- Provide 2-3 `subject_variants` (<=60 chars), a `preheader`, 3 `takeaways`.
- Footer needs real `address`, `unsubscribe_url`, `web_url` (compliance); placeholders are fine only for fixtures.

## Edge cases / learnings
- Email images must be public absolute URLs; `render_email.py` defaults to `file://` (local preview only) and `publish.py` refuses those.
- Test the pipeline free with the fixture: `mkdir -p .tmp/sample && cp tools/fixtures/sample_content.json .tmp/sample/content.json`.
- Chrome headless screenshots use the `google-chrome` binary; set `CHROME` in `tools/_common.py` if it differs.
- Brand (colors/fonts/name) lives in `tools/templates/brand.json`.
- Tried and fixed: timeline labels clipping at the edges (margins widened).

## Open items
Image hosting choice, ESP confirmation (Buttondown assumed), brand colors/logo, real footer address.
