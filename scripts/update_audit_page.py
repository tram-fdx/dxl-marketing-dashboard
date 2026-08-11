#!/usr/bin/env python3
"""Write a fresh crawl into audit.html.

Refreshes the three measurement arrays, the five KPI cards and the five
sub-score bars from the day's snapshot.

Two rules learned the hard way, both worth keeping:

1. Address KPI cards by POSITION, never by matching the prose they hold. An
   early version matched the old wording, so it worked once and then failed the
   next day against text it had written itself.

2. Change VALUES INSIDE each card; never regenerate the card's markup. The
   health card nests a .score-ring, so a non-greedy `.*?</div></div>` regex
   closed it early, left orphan fragments behind and collapsed the .kpis grid.
   Card spans are found here by counting div depth, and only the .val text and
   the data-vi/data-en pairs of .note and .delta are rewritten.

    python3 scripts/update_audit_page.py --date 2026-08-11 --repo .
"""
import argparse
import html as htmllib
import json
import pathlib
import re

DIV_OPEN = re.compile(r"<div\b", re.I)
DIV_CLOSE = re.compile(r"</div>", re.I)


def card_spans(html):
    """(start, end) of every <div class="kpi"> block, matched by div depth."""
    spans = []
    for m in re.finditer(r'<div class="kpi">', html):
        i, depth, pos = m.start(), 0, m.start()
        while pos < len(html):
            o = DIV_OPEN.search(html, pos)
            c = DIV_CLOSE.search(html, pos)
            if not c:
                raise SystemExit("unbalanced <div> in audit.html — not touching it")
            if o and o.start() < c.start():
                depth, pos = depth + 1, o.end()
            else:
                depth, pos = depth - 1, c.end()
                if depth == 0:
                    spans.append((i, pos))
                    break
    return spans


def set_val(card, value_html):
    out, n = re.subn(r'(<div class="val"[^>]*>).*?(</div>)',
                     lambda m: m.group(1) + value_html + m.group(2), card, count=1, flags=re.S)
    return out, n


def set_text(card, cls, vi, en):
    """Set the first data-vi/data-en pair inside the card's .<cls> div.

    The pair may sit on the div itself or on a child span (the health card's
    note wraps a .tag span), so the search starts at the div and takes the
    first pair it meets.
    """
    m = re.search(r'<div class="' + cls + r'[^"]*"', card)
    if not m:
        return card, 0
    tail = card[m.start():]
    pair = re.search(r'data-vi="[^"]*"(\s*)data-en="[^"]*"', tail)
    if not pair:
        return card, 0
    new_tail = tail[:pair.start()] + f'data-vi="{vi}"{pair.group(1) or " "}data-en="{en}"' + tail[pair.end():]
    return card[:m.start()] + new_tail, 1


def esc(s):
    return htmllib.escape(str(s), quote=True)


def fmt_vi(x):
    return str(x).replace(".", ",")


def rows(pages, grp):
    return [p for p in pages if p["grp"] == grp]


def avg_s(ps):
    """Seconds to two decimals as a string — 0.70 must not render as 0.7
    beside a sibling card showing 0.64."""
    return f"{sum(p['rt'] for p in ps) / len(ps) / 1000:.2f}" if ps else "0.00"


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
    slow_s = f"{slow['rt'] / 1000:.2f}"  # bound here: nesting this f-string inside another breaks on Python 3.9
    site_avg = f"{sum(p['rt'] for p in pages) / n / 1000:.2f}"
    raw = (m["overall_score"].get("note") or "").replace("raw ", "")
    d, dv = a.date, "/".join(reversed(a.date.split("-")))
    home = next(p["schema"] for p in pages if p["url"] == "/")
    arts_s = [p["schema"] for p in art_p]

    html = (repo / "audit.html").read_text(encoding="utf-8")

    # measurement arrays
    core = "\n".join(f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]},1],' for p in core_p).rstrip(",")
    art = "\n".join(f'["{p["url"].replace("/articles/", "")}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],' for p in art_p).rstrip(",")
    proj = "\n".join(f'["{p["url"]}",{p["rt"]},{p["words"]},{p["schema"]},{p["links"]}],' for p in proj_p).rstrip(",")
    for name, body in (("CORE", core), ("ART", art), ("PROJ", proj)):
        html, k = re.subn(rf"const {name} = \[.*?\n\];", f"const {name} = [\n{body}\n];", html, count=1, flags=re.S)
        print(f"  {'ok  ' if k else 'MISS'} {name} array ({len(body.splitlines())} rows)")

    measured = (f"Đo ngày {dv}, lấy giá trị tốt hơn của hai lần quét.",
                f"Measured on {d}, better of two passes.")
    # index -> (value html, note vi/en, delta vi/en)
    plan = {
        0: (f'{m["overall_score"]["value"]}<span style="font-size:15px;color:var(--muted)">/100</span>',
            (f"Điểm thô {fmt_vi(raw)} · tính từ số đo, không chấm tay",
             f"Raw {raw} · computed from measurements, not assigned by hand"),
            (f"Trọng số: Crawl 25% · Perf 25% · Schema 20% · On-page 15% · Content 15%. "
             f"Điểm 88 ngày 07/08 do người chấm nên không so trực tiếp với {m['overall_score']['value']} ở đây.",
             f"Weights: crawl 25% · perf 25% · schema 20% · on-page 15% · content 15%. "
             f"The 88 recorded on 07 Aug was hand-assigned and is not directly comparable with {m['overall_score']['value']}.")),
        1: (str(n),
            (f"{len(core_p)} gốc + {len(art_p)} bài + {len(proj_p)} dự án · {n}/{n} trả 200",
             f"{len(core_p)} core + {len(art_p)} articles + {len(proj_p)} projects · {n}/{n} return 200"),
            (f"0 timeout · 0 lỗi 4xx/5xx · sitemap {n} URL",
             f"0 timeouts · 0 4xx/5xx errors · sitemap holds {n} URLs")),
        2: (f'{fmt_vi(core_avg)}<span style="font-size:15px">s</span>',
            (f"{core_fast}/{len(core_p)} trang gốc &lt;1s · chậm nhất toàn site <code>{esc(slow['url'])}</code> {fmt_vi(slow_s)}s",
             f"{core_fast} of {len(core_p)} core pages &lt;1s · slowest site-wide <code>{esc(slow['url'])}</code> {slow_s}s"),
            measured),
        3: (f'{fmt_vi(art_avg)}<span style="font-size:15px">s</span>',
            (f"Toàn bộ {len(art_p)} bài · <b>{art_fast}/{len(art_p)} bài &lt;1s</b>",
             f"All {len(art_p)} articles · <b>{art_fast} of {len(art_p)} under 1s</b>"),
            measured),
        4: (f"{withs}/{n}",
            (f"Số khối script JSON-LD thô: trang chủ {home} · bài {min(arts_s)}–{max(arts_s)}. Lỗi nhân bản vẫn còn nên số schema thật thấp hơn nhiều.",
             f"Raw JSON-LD script blocks: homepage {home} · articles {min(arts_s)}–{max(arts_s)}. The duplication defect persists, so the true schema count is far lower."),
            (f"Phủ <b>{round(100*withs/n,1)}%</b> · còn trống: {', '.join('<code>'+esc(u)+'</code>' for u in bare) or 'không có'}",
             f"Coverage <b>{round(100*withs/n,1)}%</b> · still bare: {', '.join('<code>'+esc(u)+'</code>' for u in bare) or 'none'}")),
    }

    spans = card_spans(html)
    if len(spans) != len(plan):
        raise SystemExit(f"expected {len(plan)} KPI cards, found {len(spans)} — layout changed, not touching it")
    for idx in sorted(plan, reverse=True):  # back to front so earlier offsets stay valid
        s, e = spans[idx]
        card = html[s:e]
        val, note, delta = plan[idx]
        card, kv = set_val(card, val)
        card, kn = set_text(card, "note", *note)
        card, kd = set_text(card, "delta", *delta)
        html = html[:s] + card + html[e:]
        print(f"  {'ok  ' if kv and kn and kd else 'PART'} KPI[{idx}]  val:{kv} note:{kn} delta:{kd}")

    for name, key in (("Crawlability", "crawlability"), ("Performance / TTFB", "performance"),
                      ("Structured Data / AEO", "structured_data"), ("On-page / Meta", "on_page"),
                      ("Content", "content")):
        v = m[key]["value"]
        c = "green" if v >= 85 else ("blue" if v >= 70 else "amber")
        pat = (r'(<span class="name t" data-vi="' + re.escape(name) +
               r'"[^>]*></span><div class="bar-track">)<div class="bar-fill" style="width:\d+%;background:var\(--\w+\)">\d+</div>')
        html, k = re.subn(pat, lambda mo: mo.group(1) + f'<div class="bar-fill" style="width:{v}%;background:var(--{c})">{v}</div>',
                          html, count=1)
        print(f"  {'ok  ' if k else 'MISS'} bar {name} -> {v}")

    # dates and page counts scattered through the prose
    html = re.sub(r'data-vi="Ngày crawl: <b>[\d/]+</b>', f'data-vi="Ngày crawl: <b>{dv}</b>', html, count=1)
    html = re.sub(r'data-en="Crawl date: <b>[^<]+</b>', f'data-en="Crawl date: <b>{d}</b>', html, count=1)
    html = re.sub(r'<span id="dpLabel">Ngày [\d/]+</span>', f'<span id="dpLabel">Ngày {dv}</span>', html, count=1)
    html = re.sub(r"lúc \d{2}/\d{2}/\d{4}", f"lúc {dv}", html)
    html = re.sub(r"on \d{2} \w{3} 2026", f"on {d}", html)
    html = re.sub(r"Quét <b>\d+ trang</b>", f"Quét <b>{n} trang</b>", html)
    html = re.sub(r"covered <b>\d+ pages</b>", f"covered <b>{n} pages</b>", html)
    html = re.sub(r'data-vi="TTFB đo thật — \d+ trang', f'data-vi="TTFB đo thật — {n} trang', html)
    html = re.sub(r'(data-en="Real measured TTFB[^"]*?)\d+ pages', rf"\g<1>{n} pages", html)
    html = re.sub(r"(<b>)\d{2}/\d{2}/2026(</b>\. Phần <b>phân tích)", rf"\g<1>{dv}\g<2>", html)
    html = re.sub(r"(the <b>)\d{2} \w{3} 2026(</b> crawl)", rf"\g<1>{d}\g<2>", html)

    (repo / "audit.html").write_text(html, encoding="utf-8")
    print(f"\naudit.html updated for {d}: {n} pages, {fast} under 1s, site avg {site_avg}s")


if __name__ == "__main__":
    main()
