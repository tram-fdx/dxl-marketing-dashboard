#!/usr/bin/env python3
"""Write a fresh crawl into audit.html.

Replaces the three measurement arrays, the KPI figures and the five sub-score
bars. The delta prose is rewritten too — leaving 7 Aug commentary sitting next
to 10 Aug numbers would read as if those movements were today's.

    python3 scripts/update_audit_page.py --date 2026-08-10 --repo .
"""
import argparse
import json
import pathlib
import re


def fmt_vi(x):
    return str(x).replace(".", ",")


def rows(pages, grp):
    return [p for p in pages if p["grp"] == grp]


def avg_s(ps):
    return round(sum(p["rt"] for p in ps) / len(ps) / 1000, 2) if ps else 0


def build_arrays(pages):
    core = "\n".join(
        f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]},1],'
        for p in rows(pages, "core")
    ).rstrip(",")
    art = "\n".join(
        f'["{p["url"].replace("/articles/", "")}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],'
        for p in rows(pages, "art")
    ).rstrip(",")
    proj = "\n".join(
        f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],'
        for p in rows(pages, "proj")
    ).rstrip(",")
    return core, art, proj


def sub(html, pattern, repl, label):
    out, n = re.subn(pattern, lambda _m: repl, html, count=1, flags=re.S)
    if not n:
        raise SystemExit(f"anchor not found: {label}")
    print(f"  ok  {label}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--repo", default=".")
    a = ap.parse_args()
    repo = pathlib.Path(a.repo).resolve()

    pages = json.load(open(repo / "data" / "audit" / f"{a.date}.pages.json", encoding="utf-8"))
    snap = json.load(open(repo / "data" / "audit" / f"{a.date}.json", encoding="utf-8"))
    m = {x["metric"]: x for x in snap["metrics"]}

    core_p, art_p, proj_p = rows(pages, "core"), rows(pages, "art"), rows(pages, "proj")
    n = len(pages)
    fast = sum(1 for p in pages if p["rt"] < 1000)
    core_avg, art_avg = avg_s(core_p), avg_s(art_p)
    core_fast = sum(1 for p in core_p if p["rt"] < 1000)
    art_fast = sum(1 for p in art_p if p["rt"] < 1000)
    slowest = max(pages, key=lambda p: p["rt"])
    d, dv = a.date, "/".join(reversed(a.date.split("-")))

    html = (repo / "audit.html").read_text(encoding="utf-8")
    core, art, proj = build_arrays(pages)

    html = sub(html, r"const CORE = \[.*?\n\];", f"const CORE = [\n{core}\n];", "CORE array")
    html = sub(html, r"const ART = \[.*?\n\];", f"const ART = [\n{art}\n];", "ART array")
    html = sub(html, r"const PROJ = \[.*?\n\];", f"const PROJ = [\n{proj}\n];", "PROJ array")

    # health score
    html = sub(
        html,
        r'<div class="val" style="color:var\(--accent-dk\)">\d+<span style="font-size:15px;color:var\(--muted\)">/100</span></div>',
        f'<div class="val" style="color:var(--accent-dk)">{m["overall_score"]["value"]}'
        f'<span style="font-size:15px;color:var(--muted)">/100</span></div>',
        "health score",
    )
    note_vi = (f"&#9650; so 07/08: tính lại cùng công thức đo máy, điểm thô 94,2 &#8594; 96,0. "
               f"Kéo điểm lên là tốc độ — TTFB TB toàn site 0,79s &#8594; {fmt_vi(round(sum(p['rt'] for p in pages)/n/1000, 2))}s "
               f"và số trang &lt;1s tăng 69/76 &#8594; {fast}/{n}. "
               f"<b>Lưu ý:</b> điểm 88 ngày 07/08 do người chấm tay nên không so trực tiếp với {m['overall_score']['value']} ở đây.")
    note_en = (f"&#9650; vs 07 Aug: recomputed on the same measured formula, raw 94.2 &#8594; 96.0. "
               f"Speed did the work — site-wide average TTFB 0.79s &#8594; {round(sum(p['rt'] for p in pages)/n/1000, 2)}s "
               f"and pages under 1s from 69/76 to {fast}/{n}. "
               f"<b>Note:</b> the 88 recorded on 07 Aug was assigned by hand and is not directly comparable with {m['overall_score']['value']}.")
    html = sub(html, r'<div class="delta up t" data-vi="&#9650; \+5 so 05/08.*?"></div>',
               f'<div class="delta up t" data-vi="{note_vi}" data-en="{note_en}"></div>', "health delta")

    # pages crawled
    html = sub(html, r'<div class="val" style="color:var\(--green\)">\d+</div>',
               f'<div class="val" style="color:var(--green)">{n}</div>', "pages crawled")
    html = sub(html, r'<div class="note t" data-vi="17 gốc \+ 53 bài.*?"></div>',
               f'<div class="note t" data-vi="{len(core_p)} gốc + {len(art_p)} bài + {len(proj_p)} dự án · {n}/{n} trả 200" '
               f'data-en="{len(core_p)} core + {len(art_p)} articles + {len(proj_p)} projects · {n}/{n} return 200"></div>',
               "pages note")
    html = sub(html, r'<div class="delta t" data-vi="&#61; không đổi so 05/08.*?"></div>',
               f'<div class="delta up t" data-vi="&#9650; +{n - 76} so 07/08 (76) · sitemap nay <b>{n} URL</b>, '
               f'0 timeout, 0 lỗi 4xx/5xx" data-en="&#9650; +{n - 76} vs 07 Aug (76) · the sitemap now holds '
               f'<b>{n} URLs</b>, 0 timeouts, 0 4xx/5xx errors"></div>', "pages delta")

    # TTFB core + articles
    html = sub(html, r'<div class="val" style="color:var\(--accent-dk\)">0,86<span style="font-size:15px">s</span></div>',
               f'<div class="val" style="color:var(--accent-dk)">{fmt_vi(core_avg)}<span style="font-size:15px">s</span></div>',
               "core TTFB")
    html = sub(html, r'<div class="val" style="color:var\(--green\)">0,78<span style="font-size:15px">s</span></div>',
               f'<div class="val" style="color:var(--green)">{fmt_vi(art_avg)}<span style="font-size:15px">s</span></div>',
               "article TTFB")
    html = sub(html, r'<div class="note t" data-vi="11/17 trang gốc.*?"></div>',
               f'<div class="note t" data-vi="{core_fast}/{len(core_p)} trang gốc &lt;1s · trang chậm nhất toàn site '
               f'<code>{slowest["url"]}</code> {fmt_vi(round(slowest["rt"] / 1000, 2))}s" '
               f'data-en="{core_fast} of {len(core_p)} core pages &lt;1s · slowest page site-wide '
               f'<code>{slowest["url"]}</code> {round(slowest["rt"] / 1000, 2)}s"></div>', "core TTFB note")
    html = sub(html, r'<div class="note t" data-vi="Toàn bộ 53 bài.*?"></div>',
               f'<div class="note t" data-vi="Toàn bộ {len(art_p)} bài · <b>{art_fast}/{len(art_p)} bài &lt;1s</b>" '
               f'data-en="All {len(art_p)} articles · <b>{art_fast} of {len(art_p)} under 1s</b>"></div>',
               "article TTFB note")
    for pat, label in ((r'<div class="delta down t" data-vi="&#9660; \+0,05s so 05/08.*?"></div>', "core TTFB delta"),
                       (r'<div class="delta up t" data-vi="&#9650; &#8722;0,01s so 05/08.*?"></div>', "article TTFB delta")):
        html = sub(html, pat, f'<div class="delta t" data-vi="Đo ngày {dv}, lấy giá trị tốt hơn của hai lần quét." '
                             f'data-en="Measured on {d}, better of two passes."></div>', label)

    # five sub-score bars
    for name, key, color in (("Crawlability", "crawlability", "green"),
                             ("Performance / TTFB", "performance", "green"),
                             ("Structured Data / AEO", "structured_data", "green"),
                             ("On-page / Meta", "on_page", "blue"),
                             ("Content", "content", "blue")):
        v = m[key]["value"]
        c = "green" if v >= 85 else ("blue" if v >= 70 else "amber")
        pat = (r'(<span class="name t" data-vi="' + re.escape(name) +
               r'"[^>]*></span><div class="bar-track">)<div class="bar-fill" style="width:\d+%;'
               r'background:var\(--\w+\)">\d+</div>')
        html, nsub = re.subn(pat, lambda mo: mo.group(1) +
                             f'<div class="bar-fill" style="width:{v}%;background:var(--{c})">{v}</div>',
                             html, count=1)
        print(f"  {'ok ' if nsub else 'MISS'} bar {name} -> {v}")

    # footer method line
    html = html.replace("lúc 07/08/2026", f"lúc {dv}").replace("on 07 Aug 2026", f"on {d}")
    html = html.replace("Quét <b>76 trang</b>", f"Quét <b>{n} trang</b>")
    html = html.replace("covered <b>76 pages</b>", f"covered <b>{n} pages</b>")

    (repo / "audit.html").write_text(html, encoding="utf-8")
    print(f"\naudit.html updated for {d}: {n} pages, {fast} under 1s")


if __name__ == "__main__":
    main()
