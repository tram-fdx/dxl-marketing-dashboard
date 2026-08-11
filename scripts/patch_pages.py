#!/usr/bin/env python3
"""Make the three imported dashboards behave as pages of THIS site.

Each page was built as a standalone site whose index.html was that dashboard.
Here index.html is the Overview, and one day produces three reports, so three
assumptions have to be corrected on every build:

1. Manifest path — each page reads data/index-<source>.json, not the shared
   data/index.json, because their date pickers expect one report path per day.

2. "Today" — audit.html hardcodes `const PK_TODAY`. Left stale, its date picker
   believes the live page is an older day: the chip for that old date goes dead
   (the handler returns early for "the day you are already on") and the chip for
   the real current day navigates to an archive copy identical to what is on
   screen, so both clicks look broken. It is stamped with the build date here.

3. Self-link — "the latest day" resolved to 'index.html', which now lands on the
   Overview instead of the dashboard you are browsing. Each page points at its
   own filename.

The shared nav block is never touched; it reads the master index on purpose.

    python3 scripts/patch_pages.py --repo . --date 2026-08-11
"""
import argparse
import pathlib
import re

START, END = "<!--DXLNAV:START-->", "<!--DXLNAV:END-->"
PAGES = {"social.html": "social", "seo.html": "seo", "audit.html": "audit"}

# (pattern, replacement template) applied outside the nav block. {page} is the
# page's own filename, {date} the build date. Each is idempotent: re-running
# matches its own output and rewrites it to the same thing.
RULES = {
    "social.html": [
        (r'data/index\.json', 'data/index-{source}.json'),
        (r'if\(iso===DPI\.latest\)return "[^"]*";', 'if(iso===DPI.latest)return "{page}";'),
    ],
    "seo.html": [
        (r'data/index\.json', 'data/index-{source}.json'),
        (r"if \(r\.date === LATEST\) return '[^']*';", "if (r.date === LATEST) return '{page}';"),
        (r"if \(url === '[^']*'\)\{", "if (url === '{page}'){{"),
    ],
    "audit.html": [
        (r'data/index\.json', 'data/index-{source}.json'),
        (r"const PK_TODAY = '[^']*'", "const PK_TODAY = '{date}'"),
        (r"h!=='[^']*'\) location\.href", "h!=='{page}') location.href"),
        (r"report:'[^']*',data:'data/'", "report:'{page}',data:'data/'"),
    ],
}


def outside_nav(html, fn):
    """Apply fn to every part of the document except the shared nav block."""
    parts = re.split(f"({re.escape(START)}.*?{re.escape(END)})", html, flags=re.S)
    total = 0
    for i, part in enumerate(parts):
        if part.startswith(START):
            continue
        parts[i], n = fn(part)
        total += n
    return "".join(parts), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--date", help="YYYY-MM-DD stamped as the page's own day; "
                                   "defaults to data/index.json's latest")
    a = ap.parse_args()
    root = pathlib.Path(a.repo)

    date = a.date
    if not date:
        import json
        with open(root / "data" / "index.json", encoding="utf-8") as fh:
            date = json.load(fh)["latest"]
        print(f"  date not given — using latest from data/index.json: {date}")

    for name, source in PAGES.items():
        p = root / name
        if not p.exists():
            print(f"  skip {name} (missing)")
            continue
        html = p.read_text(encoding="utf-8")
        applied = []
        for pattern, template in RULES[name]:
            repl = template.format(page=name, source=source, date=date)
            html, n = outside_nav(html, lambda part, _p=pattern, _r=repl: re.subn(_p, _r, part))
            applied.append(f"{n}×{pattern.split('(')[0][:22]}")
        p.write_text(html, encoding="utf-8")
        print(f"  {name}: {' · '.join(applied)}")


if __name__ == "__main__":
    main()
