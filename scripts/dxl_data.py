#!/usr/bin/env python3
"""Shared helpers: the flat metric row is the contract between the daily task,
the dashboard pages and the Google Sheet.

A snapshot file is  data/<source>/<YYYY-MM-DD>.json  and looks like:

    {
      "date": "2026-08-10",
      "source": "social",
      "provenance": "read live in Chrome",
      "window": {"vi": "28 ngày qua: ...", "en": "Last 28 days: ..."},
      "metrics": [
        {"channel": "facebook", "metric": "views", "value": 4503,
         "unit": "count", "change_pct": 171.9, "window": "28d", "note": ""}
      ]
    }

CSV_COLUMNS is what Google Sheets sees. Never reorder them — the sheet's
formulas reference columns by position.
"""
import json
import pathlib

CSV_COLUMNS = [
    "date",
    "source",
    "channel",
    "metric",
    "value",
    "unit",
    "change_pct",
    "window",
    "note",
]

SOURCES = ("social", "seo", "audit")


def row(channel, metric, value, unit="count", change_pct=None, window="28d", note=""):
    return {
        "channel": channel,
        "metric": metric,
        "value": value,
        "unit": unit,
        "change_pct": change_pct,
        "window": window,
        "note": note,
    }


def flatten_legacy_social(snap):
    """Turn a nested social snapshot ({facebook:{views:{v,change_pct}}}) into rows.

    Only scalars and {v, change_pct} pairs are lifted; nested daily series are
    skipped because the sheet wants one number per metric per day.
    """
    rows = []
    for channel in ("facebook", "instagram", "youtube", "linkedin"):
        block = snap.get(channel)
        if not isinstance(block, dict):
            continue
        for metric, val in block.items():
            if isinstance(val, dict) and "v" in val:
                rows.append(row(channel, metric, val.get("v"), change_pct=val.get("change_pct")))
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                rows.append(row(channel, metric, val, window="point"))
    return rows


def read_snapshot(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_snapshot(path, snap):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def snapshot_rows(snap):
    """All CSV rows for one snapshot, stamped with its date and source."""
    date, source = snap.get("date", ""), snap.get("source", "")
    out = []
    for m in snap.get("metrics", []):
        r = {c: "" for c in CSV_COLUMNS}
        r.update(m)
        r["date"], r["source"] = date, source
        out.append([("" if r[c] is None else r[c]) for c in CSV_COLUMNS])
    return out
