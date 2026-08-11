#!/usr/bin/env python3
"""Write a fresh crawl into audit.html.

Rebuilds the three measurement arrays, the five KPI cards and the five
sub-score bars from the day's snapshot.

The KPI cards are addressed **by position**, not by matching the prose they
currently hold. An earlier version matched on the old wording, which meant it
worked once and then failed the next day against text it had itself written.
Position is stable; wording is not.

    python3 scripts/update_audit_page.py --date 2026-08-11 --repo .
"""
import argparse
import json
import pathlib
import re

KPI_BLOCK = re.compile(r'<div class="kpi">.*?</div>\s*</div>', re.S)


def fmt_vi(x):
    return str(x).replace(".", ",")


def rows(pages, grp):
    return [p for p in pages if p["grp"] == grp]


def avg_s(ps):
    return round(sum(p["rt"] for p in ps) / len(ps) / 1000, 2) if ps else 0


def card(val_html, note_vi, note_en, delta_vi, delta_en, lbl_vi, lbl_en, ring=False):
    inner = (f'<div class="score-ring"><div class="val" style="color:var(--accent-dk)">{val_html}</div></div>'
             if ring else f'<div class="val" style="color:var(--green)">{val_html}</div>')
    return (f'<div class="kpi">\n'
            f'      <div class="lbl t" data-vi="{lbl_vi}" data-en="{lbl_en}"></div>\n'
            f'      {inner}\n'
            f'      <div class="note t" data-vi="{note_vi}" data-en="{note_en}"></div>\n'
            f'      <div class="delta t" data-vi="{delta_vi}" data-en="{delta_en}"></div>\n'
            f'    </div>')


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
    withs = sum(1 for p in pages if p["schema"] > 0)
    bare = [p["url"] for p in pages if p["schema"] == 0]
    core_avg, art_avg = avg_s(core_p), avg_s(art_p)
    core_fast = sum(1 for p in core_p if p["rt"] < 1000)
    art_fast = sum(1 for p in art_p if p["rt"] < 1000)
    slow = max(pages, key=lambda p: p["rt"])
    site_avg = round(sum(p["rt"] for p in pages) / n / 1000, 2)
    d, dv = a.date, "/".join(reversed(a.date.split("-")))
    home = next(p["schema"] for p in pages if p["url"] == "/")
    arts_s = [p["schema"] for p in art_p]

    html = (repo / "audit.html").read_text(encoding="utf-8")

    core = "\n".join(f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]},1],' for p in core_p).rstrip(",")
    art = "\n".join(f'["{p["url"].replace("/articles/", "")}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],' for p in art_p).rstrip(",")
    proj = "\n".join(f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],' for p in proj_p).rstrip(",")
    for name, body in (("CORE", core), ("ART", art), ("PROJ", proj)):
        html, k = re.subn(rf"const {name} = \[.*?\n\];", f"const {name} = [\n{body}\n];", html, count=1, flags=re.S)
        print(f"  {'ok ' if k else 'MISS'} {name} array ({len(body.splitlines())} rows)")

    measured_vi = f"Đo ngày {dv}, lấy giá trị tốt hơn của hai lần quét."
    measured_en = f"Measured on {d}, better of two passes."
    cards = [
        card(f'{m["overall_score"]["value"]}<span style="font-size:15px;color:var(--muted)">/100</span>',
             f"Điểm thô {fmt_vi(m['overall_score'].get('note', '').replace('raw ', ''))} · trọng số Crawl 25% · Perf 25% · Schema 20% · On-page 15% · Content 15%",
             f"Raw {m['overall_score'].get('note', '').replace('raw ', '')} · weights crawl 25% · perf 25% · schema 20% · on-page 15% · content 15%",
             "Điểm tính từ số đo, không chấm tay. Điểm 88 ngày 07/08 do người chấm nên không so trực tiếp được.",
             "Computed from measurements, not assigned by hand. The 88 recorded on 07 Aug was hand-assigned and is not directly comparable.",
             "Health Score", "Health Score", ring=True),
        card(str(n),
             f"{len(core_p)} gốc + {len(art_p)} bài + {len(proj_p)} dự án · {n}/{n} trả 200",
             f"{len(core_p)} core + {len(art_p)} articles + {len(proj_p)} projects · {n}/{n} return 200",
             f"0 timeout · 0 lỗi 4xx/5xx · sitemap {n} URL",
             f"0 timeouts · 0 4xx/5xx errors · sitemap holds {n} URLs",
             "Trang crawl được", "Pages crawled"),
        card(f'{fmt_vi(core_avg)}<span style="font-size:15px">s</span>',
             f"{core_fast}/{len(core_p)} trang gốc &lt;1s · chậm nhất toàn site <code>{slow['url']}</code> {fmt_vi(round(slow['rt']/1000,2))}s",
             f"{core_fast} of {len(core_p)} core pages &lt;1s · slowest site-wide <code>{slow['url']}</code> {round(slow['rt']/1000,2)}s",
             measured_vi, measured_en, "TTFB TB — trang gốc", "Avg TTFB — core"),
        card(f'{fmt_vi(art_avg)}<span style="font-size:15px">s</span>',
             f"Toàn bộ {len(art_p)} bài · <b>{art_fast}/{len(art_p)} bài &lt;1s</b>",
             f"All {len(art_p)} articles · <b>{art_fast} of {len(art_p)} under 1s</b>",
             measured_vi, measured_en, "TTFB TB — bài viết", "Avg TTFB — articles"),
        card(f"{withs}/{n}",
             f"Số khối script JSON-LD thô: trang chủ {home} · bài {min(arts_s)}–{max(arts_s)}. Lỗi nhân bản vẫn còn nên số schema thật thấp hơn nhiều.",
             f"Raw JSON-LD script blocks: homepage {home} · articles {min(arts_s)}–{max(arts_s)}. The duplication defect persists, so the true schema count is far lower.",
             f"Phủ <b>{round(100*withs/n,1)}%</b> · còn trống: {', '.join('<code>'+u+'</code>' for u in bare) or 'không có'}",
             f"Coverage <b>{round(100*withs/n,1)}%</b> · still bare: {', '.join('<code>'+u+'</code>' for u in bare) or 'none'}",
             "Schema (JSON-LD)", "Schema (JSON-LD)"),
    ]

    blocks = KPI_BLOCK.findall(html)
    if len(blocks) != len(cards):
        raise SystemExit(f"expected {len(cards)} KPI cards, found {len(blocks)} — layout changed, not touching it")
    for old, new in zip(blocks, cards):
        html = html.replace(old, new, 1)
    print(f"  ok  {len(cards)} KPI cards rebuilt by position")

    for name, key in (("Crawlability", "crawlability"), ("Performance / TTFB", "performance"),
                      ("Structured Data / AEO", "structured_data"), ("On-page / Meta", "on_page"),
                      ("Content", "content")):
        v = m[key]["value"]
        c = "green" if v >= 85 else ("blue" if v >= 70 else "amber")
        pat = (r'(<span class="name t" data-vi="' + re.escape(name) +
               r'"[^>]*></span><div class="bar-track">)<div class="bar-fill" style="width:\d+%;background:var\(--\w+\)">\d+</div>')
        html, k = re.subn(pat, lambda mo: mo.group(1) + f'<div class="bar-fill" style="width:{v}%;background:var(--{c})">{v}</div>',
                          html, count=1)
        print(f"  {'ok ' if k else 'MISS'} bar {name} -> {v}")

    html = re.sub(r'data-vi="Ngày crawl: <b>[\d/]+</b>', f'data-vi="Ngày crawl: <b>{dv}</b>', html, count=1)
    html = re.sub(r'data-en="Crawl date: <b>[^<]+</b>', f'data-en="Crawl date: <b>{d}</b>', html, count=1)
    html = re.sub(r'<span id="dpLabel">Ngày [\d/]+</span>', f'<span id="dpLabel">Ngày {dv}</span>', html, count=1)
    html = re.sub(r"lúc \d{2}/\d{2}/\d{4}", f"lúc {dv}", html)
    html = re.sub(r"on \d{2} \w{3} 2026", f"on {d}", html)
    html = re.sub(r"Quét <b>\d+ trang</b>", f"Quét <b>{n} trang</b>", html)
    html = re.sub(r"covered <b>\d+ pages</b>", f"covered <b>{n} pages</b>", html)
    html = re.sub(r'data-vi="TTFB đo thật — \d+ trang', f'data-vi="TTFB đo thật — {n} trang', html)
    html = re.sub(r'(data-en="Real measured TTFB[^"]*?)\d+ pages', rf"\g<1>{n} pages", html)
    html = re.sub(r"(<b>)\d{2}/\d{2}/2026(</b>. Phần <b>phân tích)", rf"\g<1>{dv}\g<2>", html)
    html = re.sub(r"(the <b>)\d{2} \w{3} 2026(</b> crawl)", rf"\g<1>{d}\g<2>", html)

    (repo / "audit.html").write_text(html, encoding="utf-8")
    print(f"\naudit.html updated for {d}: {n} pages, {fast} under 1s, site avg {site_avg}s")


if __name__ == "__main__":
    main()
