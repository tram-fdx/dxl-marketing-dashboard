#!/usr/bin/env python3
"""Freeze today's three dashboard pages into archive/<date>/ and register the
day in data/index.json so the date pickers can offer it.

A frozen day is final: this refuses to overwrite an existing archive folder
unless --force is passed, so history cannot be quietly rewritten.

    python3 scripts/freeze_day.py --repo . --date 2026-08-10 \
        --label-vi "..." --label-en "..." --dry-run
"""
import argparse
import json
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import SOURCES  # noqa: E402

PAGES = ("social.html", "seo.html", "audit.html")


def load_index(repo):
    path = repo / "data" / "index.json"
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {
        "site": "DX Living — Marketing Dashboard",
        "description": "Social / SEO / Website audit. One snapshot set per day.",
        "latest": None,
        "snapshots": [],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--label-vi", default="")
    ap.add_argument("--label-en", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite an already-frozen day")
    a = ap.parse_args()

    repo = pathlib.Path(a.repo).resolve()
    date = a.date
    dest = repo / "archive" / date

    missing = [p for p in PAGES if not (repo / p).exists()]
    if missing:
        raise SystemExit(f"missing dashboard pages: {', '.join(missing)}")

    have = [s for s in SOURCES if (repo / "data" / s / f"{date}.json").exists()]
    if not have:
        raise SystemExit(f"no snapshot for {date} under data/*/ — write the data first")

    if dest.exists() and not a.force:
        raise SystemExit(f"archive/{date} already frozen — pass --force only if you mean it")

    idx = load_index(repo)
    entry = {
        "date": date,
        "sources": have,
        "data": {s: f"data/{s}/{date}.json" for s in have},
        "report": {
            "social": f"archive/{date}/social.html",
            "seo": f"archive/{date}/seo.html",
            "audit": f"archive/{date}/audit.html",
        },
        "label_vi": a.label_vi,
        "label_en": a.label_en,
    }

    print(f"date          {date}")
    print(f"sources       {', '.join(have)}  (missing: {', '.join(set(SOURCES) - set(have)) or 'none'})")
    print(f"archive       archive/{date}/ <- {', '.join(PAGES)}")
    print(f"label vi/en   {a.label_vi!r} / {a.label_en!r}")
    print(f"snapshots     {len(idx['snapshots'])} -> {len([s for s in idx['snapshots'] if s['date'] != date]) + 1}")
    if a.dry_run:
        print("\ndry run — nothing written")
        return

    dest.mkdir(parents=True, exist_ok=True)
    for p in PAGES:
        shutil.copyfile(repo / p, dest / p)
    fix_archive_nav(dest)

    idx["snapshots"] = [s for s in idx["snapshots"] if s["date"] != date] + [entry]
    idx["snapshots"].sort(key=lambda s: s["date"])
    idx["latest"] = idx["snapshots"][-1]["date"]
    with open(repo / "data" / "index.json", "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    write_source_indexes(repo, idx)
    print(f"\nfrozen. latest = {idx['latest']}")


def fix_archive_nav(dest):
    """Inside archive/<date>/, the three sibling pages link to each other fine —
    that is the point, you can browse one whole day. Only the two links that
    mean "back to live" have to climb out of the folder.
    """
    for p in PAGES:
        path = dest / p
        html = path.read_text(encoding="utf-8")
        head, sep, rest = html.partition("<!--DXLNAV:END-->")
        if not sep:
            continue
        head = head.replace('href="index.html"', 'href="../../index.html"')
        path.write_text(head + sep + rest, encoding="utf-8")


def write_source_indexes(repo, idx):
    """Each dashboard's own date picker wants one report path per day.

    See scripts/patch_pages.py — the pages read these, not the master index.
    A day only appears in a source's index if that source actually has data,
    so a channel that could not be read does not show a phantom entry.
    """
    for source in SOURCES:
        snaps = [
            {
                "date": s["date"],
                "data": s["data"][source],
                "report": s["report"][source],
                "label_vi": s.get("label_vi", ""),
                "label_en": s.get("label_en", ""),
            }
            for s in idx["snapshots"]
            if source in s.get("sources", []) and source in s.get("data", {})
        ]
        out = {
            "site": f"DX Living — {source}",
            "latest": snaps[-1]["date"] if snaps else None,
            "snapshots": snaps,
        }
        with open(repo / "data" / f"index-{source}.json", "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"  data/index-{source}.json: {len(snaps)} day(s)")


if __name__ == "__main__":
    main()
