#!/usr/bin/env python3
"""Point each dashboard's own date picker at its per-source index file.

The three pages were built as standalone sites that each read `data/index.json`
and expect `snapshot.report` to be a single HTML path. In this repo one day
produces three reports, so the master index cannot satisfy them. freeze_day.py
therefore also writes data/index-<source>.json in that older single-report
shape, and this patch redirects each page to its own file.

The shared nav block is left alone — it reads the master index on purpose.

Idempotent. Run after any dashboard page is regenerated.

    python3 scripts/patch_pages.py --repo .
"""
import argparse
import pathlib
import re

START, END = "<!--DXLNAV:START-->", "<!--DXLNAV:END-->"
PAGES = {"social.html": "social", "seo.html": "seo", "audit.html": "audit"}


def patch_outside_nav(html: str, source: str) -> tuple[str, int]:
    """Replace the index path everywhere except inside the nav block."""
    target = f"data/index-{source}.json"
    parts = re.split(f"({re.escape(START)}.*?{re.escape(END)})", html, flags=re.S)
    total = 0
    for i, part in enumerate(parts):
        if part.startswith(START):
            continue  # the nav keeps reading the master index
        new, n = re.subn(r"data/index\.json", target, part)
        parts[i], total = new, total + n
    return "".join(parts), total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    root = pathlib.Path(a.repo)
    for name, source in PAGES.items():
        p = root / name
        if not p.exists():
            print(f"  skip {name} (missing)")
            continue
        html = p.read_text(encoding="utf-8")
        out, n = patch_outside_nav(html, source)
        if n:
            p.write_text(out, encoding="utf-8")
        already = out.count(f"data/index-{source}.json")
        print(f"  {name}: {n} path(s) redirected -> data/index-{source}.json ({already} total)")


if __name__ == "__main__":
    main()
