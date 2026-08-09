#!/usr/bin/env python3
"""One-off: seed the 7 Aug 2026 baseline so the dashboard is not empty on day one.

Social numbers are converted from the published social snapshot; SEO and audit
numbers are read out of the published report pages of the same date. Every row
is stamped with that provenance — the daily task replaces them with live reads
from then on.
"""
import json
import pathlib
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import flatten_legacy_social, row, write_snapshot  # noqa: E402

DATE = "2026-08-07"
LEGACY = f"https://tram-fdx.github.io/dxl-social-dashboard-site/data/{DATE}.json"
REPO = pathlib.Path(__file__).resolve().parent.parent


def seed_social():
    with urllib.request.urlopen(LEGACY, timeout=30) as r:
        legacy = json.load(r)
    write_snapshot(
        REPO / "data" / "social" / f"{DATE}.json",
        {
            "date": DATE,
            "source": "social",
            "provenance": "baseline converted from the published social snapshot of 7 Aug 2026",
            "window": legacy.get("window", {}),
            "metrics": flatten_legacy_social(legacy),
        },
    )


def seed_seo():
    write_snapshot(
        REPO / "data" / "seo" / f"{DATE}.json",
        {
            "date": DATE,
            "source": "seo",
            "provenance": "baseline read from the published SEO report of 7 Aug 2026",
            "window": {
                "vi": "28 ngày qua, so với tháng 6",
                "en": "Last 28 days, compared with June",
            },
            "metrics": [
                row("gsc", "clicks", 72, change_pct=53.0),
                row("gsc", "impressions", 1288, change_pct=119.0),
                row("gsc", "ctr", 5.6, unit="percent", note="down from 8.0% in June"),
                row("gsc", "avg_position", 29.6, unit="position", note="down from 13.8, wider coverage"),
                row("ga4", "sessions", 287, note="under-counted, tracking fault from ~29 Jul"),
                row("ga4", "engaged_sessions", 194, note="under-counted, tracking fault from ~29 Jul"),
                row("ahrefs", "referring_domains", 366, window="point"),
                row("ahrefs", "backlinks", 372, window="point"),
            ],
        },
    )


def seed_audit():
    write_snapshot(
        REPO / "data" / "audit" / f"{DATE}.json",
        {
            "date": DATE,
            "source": "audit",
            "provenance": "baseline read from the published technical audit dashboard of 7 Aug 2026",
            "window": {"vi": "Lần quét ngày 7/8/2026", "en": "Crawl of 7 Aug 2026"},
            "metrics": [
                row("site", "overall_score", 88, unit="score", change_pct=None, window="point",
                    note="+5 vs 5 Aug (83)"),
                row("site", "pages_crawled", 76, window="point", note="sitemap holds at 75 URLs"),
                row("site", "avg_load_time", 0.86, unit="seconds", window="point",
                    note="11 of 17 core pages under 1s"),
                row("site", "crawlability", 96, unit="score", window="point"),
                row("site", "structured_data", 87, unit="score", window="point"),
                row("site", "performance", 92, unit="score", window="point"),
                row("site", "errors_4xx_5xx", 0, window="point", note="third consecutive clean day"),
            ],
        },
    )


if __name__ == "__main__":
    seed_social()
    seed_seo()
    seed_audit()
    print(f"seeded {DATE} for social / seo / audit")
