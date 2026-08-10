#!/usr/bin/env python3
"""Re-crawl dxliving.com and produce an audit snapshot.

Measures the same things the audit dashboard has always shown, the same way:
every URL in the sitemap fetched sequentially, TTFB taken as the better of two
passes to suppress network jitter, word count with script/style/noscript
stripped, JSON-LD counted as script blocks in the raw HTML.

Scoring weights are the ones printed on the dashboard itself:
Crawl 25% · Perf 25% · Schema 20% · On-page 15% · Content 15%.

    python3 scripts/crawl_audit.py --date 2026-08-10 --repo .
"""
import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import row, write_snapshot  # noqa: E402

SITE = "https://dxliving.com"
SITEMAP = f"{SITE}/sitemap.xml"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
TIMEOUT = 15

TAG = re.compile(r"<[^>]+>")
STRIP = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.S | re.I)
JSONLD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\']', re.I)
HREF = re.compile(r'<a\b[^>]*href=["\']([^"\']+)["\']', re.I)
IMG = re.compile(r"<img\b[^>]*>", re.I)
ALT = re.compile(r'\balt=["\'][^"\']', re.I)
LAZY = re.compile(r'\bloading=["\']lazy["\']', re.I)
H = re.compile(r"<h([1-6])\b", re.I)
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
META_DESC = re.compile(r'<meta[^>]+name=["\']description["\'][^>]*>', re.I)
CANON = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*>', re.I)


def fetch(url):
    """Return (status, ttfb_ms, body). status 0 means the request failed."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            head = r.read(1)  # first byte — this is the TTFB boundary
            ttfb = (time.perf_counter() - t0) * 1000
            body = head + r.read()
            return r.status, ttfb, body.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, (time.perf_counter() - t0) * 1000, ""
    except Exception:
        return 0, (time.perf_counter() - t0) * 1000, ""


def measure(html):
    text = TAG.sub(" ", STRIP.sub(" ", html))
    words = len(text.split())
    links = {
        h.split("#")[0].split("?")[0]
        for h in HREF.findall(html)
        if h.startswith("/") or h.startswith(SITE)
    }
    imgs = IMG.findall(html)
    levels = [int(x) for x in H.findall(html)]
    jumps = sum(1 for a, b in zip(levels, levels[1:]) if b - a > 1)
    return {
        "words": words,
        "schema": len(JSONLD.findall(html)),
        "links": len(links),
        "imgs": len(imgs),
        "imgs_alt": sum(1 for i in imgs if ALT.search(i)),
        "imgs_lazy": sum(1 for i in imgs if LAZY.search(i)),
        "h1": levels.count(1),
        "heading_jumps": jumps,
        "has_title": bool(TITLE.search(html)),
        "has_meta_desc": bool(META_DESC.search(html)),
        "has_canonical": bool(CANON.search(html)),
    }


def sitemap_urls():
    _s, _t, body = fetch(SITEMAP)
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body)
    out, seen = [], set()
    for u in locs:
        if u.endswith(".xml"):
            _s2, _t2, sub = fetch(u)
            locs.extend(re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sub))
            continue
        p = u.split("#")[0].rstrip("/") or "/"
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def group(path):
    if path.startswith("/articles/"):
        return "art"
    if path.startswith("/projects/"):
        return "proj"
    return "core"


def crawl():
    urls = sitemap_urls()
    print(f"sitemap: {len(urls)} URLs", flush=True)
    pages = []
    for i, u in enumerate(urls, 1):
        s1, t1, body = fetch(u)
        _s2, t2, _b2 = fetch(u)  # second pass, best-of-two like the original method
        m = measure(body)
        m.update(url=u.replace(SITE, "") or "/", status=s1,
                 rt=round(min(t1, t2)), grp=group(u.replace(SITE, "")))
        pages.append(m)
        if i % 10 == 0 or i == len(urls):
            print(f"  {i}/{len(urls)}", flush=True)
    return pages


def score(pages):
    n = len(pages)
    ok = [p for p in pages if p["status"] == 200]
    fast = sum(1 for p in ok if p["rt"] < 1000)
    schema = sum(1 for p in ok if p["schema"] > 0)
    titled = sum(1 for p in ok if p["has_title"] and p["has_meta_desc"] and p["has_canonical"])
    alt_ok = sum(p["imgs_alt"] for p in ok)
    alt_all = sum(p["imgs"] for p in ok) or 1
    clean_head = sum(1 for p in ok if p["heading_jumps"] == 0 and p["h1"] == 1)
    arts = [p for p in ok if p["grp"] == "art"]
    thin = sum(1 for p in ok if p["words"] < 300)

    crawl_s = round(100 * len(ok) / n) if n else 0
    perf_s = round(100 * fast / len(ok)) if ok else 0
    schema_s = round(100 * schema / len(ok)) if ok else 0
    onpage_s = round((100 * titled / len(ok)) * 0.4 + (100 * alt_ok / alt_all) * 0.3 +
                     (100 * clean_head / len(ok)) * 0.3) if ok else 0
    content_s = round(100 * (1 - thin / len(ok))) if ok else 0
    raw = (crawl_s * .25 + perf_s * .25 + schema_s * .20 + onpage_s * .15 + content_s * .15)

    return {
        "overall": round(raw), "raw": round(raw, 1),
        "crawl": crawl_s, "perf": perf_s, "schema": schema_s,
        "onpage": onpage_s, "content": content_s,
        "pages": n, "ok": len(ok), "fast": fast, "schema_pages": schema,
        "errors": n - len(ok),
        "avg_rt": round(sum(p["rt"] for p in ok) / len(ok) / 1000, 2) if ok else 0,
        "slowest": round(max((p["rt"] for p in ok), default=0) / 1000, 2),
        "articles": len(arts),
        "avg_words_art": round(sum(p["words"] for p in arts) / len(arts)) if arts else 0,
        "thin": thin,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    repo = pathlib.Path(a.repo).resolve()

    pages = crawl()
    s = score(pages)
    print(json.dumps(s, indent=2))

    write_snapshot(
        repo / "data" / "audit" / f"{a.date}.json",
        {
            "date": a.date,
            "source": "audit",
            "provenance": (
                "live crawl of dxliving.com sitemap, each URL fetched twice and the better "
                "TTFB kept. Sub-scores are recomputed from measured ratios with the weights "
                "printed on the dashboard (crawl 25 / perf 25 / schema 20 / on-page 15 / "
                "content 15) — the 7 Aug sub-scores were assigned by hand, so compare the "
                "measured inputs rather than the composite across those two days."
            ),
            "window": {"vi": f"Lần quét ngày {a.date}", "en": f"Crawl of {a.date}"},
            "metrics": [
                row("site", "overall_score", s["overall"], unit="score", window="point",
                    note=f"raw {s['raw']}"),
                row("site", "pages_crawled", s["pages"], window="point"),
                row("site", "avg_load_time", s["avg_rt"], unit="seconds", window="point",
                    note=f"{s['fast']}/{s['ok']} pages under 1s; slowest {s['slowest']}s"),
                row("site", "crawlability", s["crawl"], unit="score", window="point"),
                row("site", "performance", s["perf"], unit="score", window="point"),
                row("site", "structured_data", s["schema"], unit="score", window="point",
                    note=f"{s['schema_pages']}/{s['ok']} pages carry JSON-LD"),
                row("site", "on_page", s["onpage"], unit="score", window="point"),
                row("site", "content", s["content"], unit="score", window="point",
                    note=f"{s['thin']} pages under 300 words"),
                row("site", "errors_4xx_5xx", s["errors"], window="point"),
                row("site", "articles", s["articles"], window="point",
                    note=f"average {s['avg_words_art']} words"),
            ],
        },
    )
    with open(repo / "data" / "audit" / f"{a.date}.pages.json", "w", encoding="utf-8") as fh:
        json.dump(pages, fh, ensure_ascii=False, indent=1)
    print(f"\nwrote data/audit/{a.date}.json (+ .pages.json)")


if __name__ == "__main__":
    main()
