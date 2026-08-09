#!/usr/bin/env python3
"""Inject the shared DXL top nav into each dashboard page.

Idempotent: running it again replaces the existing nav block instead of stacking
a second one. Run after any dashboard page is regenerated.

    python3 scripts/inject_nav.py --repo .
"""
import argparse
import pathlib
import re

START = "<!--DXLNAV:START-->"
END = "<!--DXLNAV:END-->"

PAGES = {
    "index.html": "home",
    "social.html": "social",
    "seo.html": "seo",
    "audit.html": "audit",
    "history.html": "history",  # no tab of its own — nothing highlights
}

TABS = [
    ("home", "index.html", "Overview", "Tổng quan"),
    ("social", "social.html", "Social", "Social"),
    ("seo", "seo.html", "SEO", "SEO"),
    ("audit", "audit.html", "Website Audit", "Audit website"),
]

CSS = """
#dxlnav{position:fixed;top:0;left:0;right:0;height:48px;z-index:9999;
  background:#0b1533;display:flex;align-items:center;gap:14px;
  padding:0 16px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
  box-shadow:0 1px 0 rgba(255,255,255,.06),0 2px 12px rgba(11,21,51,.18)}
#dxlnav .nb{display:flex;align-items:center;gap:9px;flex:none;text-decoration:none}
#dxlnav .nb i{width:26px;height:26px;border-radius:8px;flex:none;
  background:linear-gradient(135deg,#5b6bf5,#22d3ee);display:flex;align-items:center;
  justify-content:center;color:#fff;font-weight:800;font-size:11px;font-style:normal}
#dxlnav .nb b{color:#fff;font-size:13px;font-weight:800;letter-spacing:.2px;white-space:nowrap}
#dxlnav .nt{display:flex;align-items:center;gap:6px;overflow-x:auto;scrollbar-width:none}
#dxlnav .nt::-webkit-scrollbar{display:none}
#dxlnav a.t{color:#9aa6c6;font-size:12.5px;font-weight:700;text-decoration:none;
  padding:7px 13px;border-radius:9px;white-space:nowrap;transition:.15s}
#dxlnav a.t:hover{color:#fff;background:rgba(255,255,255,.08)}
#dxlnav a.t.on{color:#0b1533;background:#fff}
#dxlnav .nr{margin-left:auto;display:flex;align-items:center;gap:10px;flex:none}
#dxlnav .nd{color:#6d7ba3;font-size:11px;font-weight:700;white-space:nowrap}
@media(max-width:820px){#dxlnav .nb b{display:none}#dxlnav .nd{display:none}}
body{padding-top:48px !important}
/* social.html keeps a sticky left rail — drop it below the bar */
.app>.rail{top:48px !important;height:calc(100vh - 48px) !important}
"""


def block(active: str) -> str:
    tabs = "".join(
        '<a class="t{on}" href="{href}">{en}</a>'.format(
            on=" on" if key == active else "", href=href, en=en
        )
        for key, href, en, _vi in TABS
    )
    return (
        f"{START}\n"
        f"<style>{CSS}</style>\n"
        f'<div id="dxlnav">'
        f'<a class="nb" href="index.html"><i>DX</i><b>DX Living — Marketing</b></a>'
        f'<div class="nt">{tabs}</div>'
        f'<div class="nr"><span class="nd" id="dxlnavDate"></span></div>'
        f"</div>\n"
        f'<script>fetch("data/index.json").then(r=>r.json()).then(j=>{{'
        f'var e=document.getElementById("dxlnavDate");'
        f'if(e&&j.latest)e.textContent="Data: "+j.latest;}}).catch(function(){{}});<\\/script>\n'
        f"{END}"
    ).replace("<\\/script>", "</script>")


def inject(path: pathlib.Path, active: str) -> str:
    html = path.read_text(encoding="utf-8")
    new = block(active)
    if START in html:
        html = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _m: new, html, flags=re.S)
        action = "replaced"
    else:
        m = re.search(r"<body[^>]*>", html)
        if not m:
            raise SystemExit(f"{path.name}: no <body> tag found")
        html = html[: m.end()] + "\n" + new + html[m.end() :]
        action = "inserted"
    path.write_text(html, encoding="utf-8")
    return action


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    root = pathlib.Path(args.repo)
    for name, active in PAGES.items():
        p = root / name
        if not p.exists():
            print(f"  skip {name} (missing)")
            continue
        print(f"  {inject(p, active):8s} nav -> {name}")


if __name__ == "__main__":
    main()
