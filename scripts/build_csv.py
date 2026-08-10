#!/usr/bin/env python3
"""Rebuild the CSV files that Google Sheets pulls with IMPORTDATA.

Writes data/social.csv, data/seo.csv, data/audit.csv and data/all.csv from
every snapshot under data/<source>/. Safe to re-run — it always rebuilds from
the snapshots, so a corrected snapshot fixes the sheet on the next run.

    python3 scripts/build_csv.py --repo .
"""
import argparse
import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import CSV_COLUMNS, SOURCES, read_snapshot, snapshot_rows  # noqa: E402


def build(repo: pathlib.Path) -> None:
    everything = []
    for source in SOURCES:
        rows = []
        folder = repo / "data" / source
        # *.pages.json is the raw per-URL dump that sits beside an audit
        # snapshot — a list, not a snapshot, and not part of the CSV.
        for path in sorted(p for p in folder.glob("*.json") if not p.name.endswith(".pages.json")):
            try:
                rows.extend(snapshot_rows(read_snapshot(path)))
            except Exception as exc:  # a bad snapshot must not kill the whole build
                print(f"  !! {path.name}: {exc}", file=sys.stderr)
        rows.sort(key=lambda r: (r[0], r[2], r[3]))
        out = repo / "data" / f"{source}.csv"
        with open(out, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(CSV_COLUMNS)
            w.writerows(rows)
        everything.extend(rows)
        print(f"  {out.relative_to(repo)}: {len(rows)} rows")

    everything.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    out = repo / "data" / "all.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNS)
        w.writerows(everything)
    print(f"  {out.relative_to(repo)}: {len(everything)} rows")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    build(pathlib.Path(a.repo).resolve())
