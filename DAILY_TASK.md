---
name: dxl-marketing-dashboard-daily
description: Mỗi sáng đọc số Social + SEO + Audit website, ghi snapshot JSON, dựng CSV cho Google Sheets, đóng băng ngày và push lên GitHub Pages
---

Cập nhật dashboard marketing hợp nhất của DX Living: đọc số liệu trực tiếp,
ghi thành snapshot theo ngày, dựng lại CSV cho Google Sheets, đóng băng bản
HTML của ngày, rồi push.

Repo: `tram-fdx/dxl-marketing-dashboard` (public), nhánh `main`.
Live: https://tram-fdx.github.io/dxl-marketing-dashboard/
Token: `/Users/thanhtramnt20/Claude/Projects/DXL/dashboard-site/deploy-token.txt`
(có BOM, phải strip; KHÔNG in ra, KHÔNG commit).
Sheet: https://docs.google.com/spreadsheets/d/1K4Y5QdkPqWxo1zciJZHn-b3M3WdrnqWdsNXmHgRE8ys/

Đây là repo ĐỘC LẬP. Tuyệt đối không đụng tới `dxl-social-dashboard-site`,
`dxliving-seo-report` hay `dxl-seo-audit` — kể cả để đọc số cũ.

Làm việc trong clone tại `/tmp/mktrepo`.

═══════════════════════════════════════════════
QUY TẮC — VI PHẠM LÀ DỪNG, KHÔNG PUSH
═══════════════════════════════════════════════

- KHÔNG BỊA SỐ. Kênh nào không đọc được thì **bỏ metric đó ra khỏi snapshot**
  và ghi lý do vào `provenance`. Không giữ số hôm qua rồi trình bày như số mới.
- Không đổi layout, CSS, hay cấu trúc của `social.html` / `seo.html` /
  `audit.html`. Chỉ thay giá trị số và chuỗi ngày.
- Không sửa tay file trong `archive/` — ngày đã đóng băng là đã đóng.
- Trước khi push, `index.html`, `social.html`, `seo.html`, `audit.html`,
  `history.html` đều phải còn khối `<!--DXLNAV:START-->`. Thiếu → DỪNG, báo cáo.

─────────────────────────────
BƯỚC 1 — Chuẩn bị

```
git clone <repo> /tmp/mktrepo
NEW_DATE = ngày chạy theo giờ Việt Nam (Asia/Ho_Chi_Minh), YYYY-MM-DD
```

claude-in-chrome → `list_connected_browsers` → `select_browser` deviceId máy
macOS (`isLocal=true`). Không có → dừng và ghi chú.

─────────────────────────────
BƯỚC 2 — Đọc số (CHỈ ĐỌC, không đăng bài, không nhắn tin)

**Social — 28 ngày**
- Facebook: `business.facebook.com/latest/insights/overview?asset_id=740407369159752`
  → views, viewers, visits, interactions, video_3s, link_clicks, net new followers.
  Tổng follower đọc ở `business.facebook.com/latest/`.
- Instagram: cùng trang insights, `asset_id=17841476632163784`
  → views, reach, interactions. Follower + số bài ở `instagram.com/dxliving.au/`.
- YouTube: `studio.youtube.com/channel/UCuxr30df_qmARRgETsruEyw/analytics/tab-overview/period-4_weeks`
  → views_28d, watch_time_hours. Subscribers + số video ở trang channel.
- LinkedIn admin: `/analytics/updates/` (impressions, reactions, comments, reposts),
  `/analytics/followers/` (total, new_30d), `/analytics/visitors/` (page_views, unique).
  Gặp authwall → bỏ metric LinkedIn, ghi rõ trong `provenance`.

**SEO — 28 ngày**
- Google Search Console: clicks, impressions, ctr, avg_position.
- GA4: sessions, engaged_sessions, conversions. GA4 đang có lỗi thu thập từ
  ~29/07 → nếu số vẫn bất thường thì ghi vào `note` của từng metric.
- Ahrefs (UI qua Chrome, gói hiện tại không có API): referring_domains, backlinks,
  domain_rating.

**Audit website**
- Quét `dxliving.com` như dashboard audit vẫn làm: overall_score, pages_crawled,
  avg_load_time, crawlability, structured_data, performance, errors_4xx_5xx.

─────────────────────────────
BƯỚC 3 — Ghi snapshot

Ba file, đúng shape trong `README.md`:

```
/tmp/mktrepo/data/social/<NEW_DATE>.json
/tmp/mktrepo/data/seo/<NEW_DATE>.json
/tmp/mktrepo/data/audit/<NEW_DATE>.json
```

Mỗi metric là một dòng phẳng: `channel, metric, value, unit, change_pct, window, note`.
Validate cả ba bằng `python3 -m json.tool`.

**Bắt buộc có `insights`** — 2–4 nhận định mỗi mảng, song ngữ, hiện trên trang Overview:

```json
"insights": [
  {"level": "good", "vi": "<b>Facebook</b> …", "en": "<b>Facebook</b> …"}
]
```

`level` là `good` / `warn` / `bad` / `info`. Viết nhận định nói **điều gì đang xảy ra
và vì sao**, không lặp lại con số đã có ở trên. Cảnh báo khi phần trăm đánh lừa
(vd. +842% nhưng nền chỉ từ 7 lên 66). Không có `insights` thì trang tự suy ra
mức biến động lớn nhất — dùng được nhưng nhạt, đừng để rơi vào đó.

─────────────────────────────
BƯỚC 4 — Cập nhật số hiển thị trên 3 trang HTML

Thay giá trị trong `social.html`, `seo.html`, `audit.html` cho khớp snapshot vừa ghi,
kèm chuỗi ngày/kỳ báo cáo. Kiểm tra: số `<span class="vi">` phải bằng số
`<span class="en">` trong mỗi file.

─────────────────────────────
BƯỚC 5 — Dựng lại và đóng băng

```bash
cd /tmp/mktrepo
python3 scripts/build_csv.py   --repo .
python3 scripts/patch_pages.py --repo . --date <NEW_DATE>   # BẮT BUỘC có --date:
#   nó dập PK_TODAY vào audit.html. Quên thì bộ chọn ngày tưởng trang là bản cũ,
#   chip ngày cũ bấm không ăn và chip ngày mới nhảy sang bản archive y hệt.
python3 scripts/inject_nav.py  --repo .
python3 scripts/freeze_day.py  --repo . --date <NEW_DATE> \
    --label-vi "<tóm tắt 1 dòng>" --label-en "<one-line summary>" --dry-run
```

Đọc output dry-run rồi chạy lại bỏ `--dry-run`.

─────────────────────────────
BƯỚC 6 — Kiểm tra trước khi push

- `data/index.json` có `<NEW_DATE>` và `latest = <NEW_DATE>`.
- `data/index-social.json`, `-seo`, `-audit` đều có ngày mới (trừ mảng không đọc được).
- Mọi đường dẫn trong manifest đều tồn tại thật.
- Năm file HTML còn khối `DXLNAV`.

─────────────────────────────
BƯỚC 7 — Push

```bash
git add -A && git commit -m "data: <NEW_DATE>" && git push
```

─────────────────────────────
BƯỚC 8 — Xác nhận live & báo cáo

Đợi ~75–90 giây cho Pages build, mở
`https://tram-fdx.github.io/dxl-marketing-dashboard/?v=<random>`.
Phải thấy: thanh tab đen ở trên cùng, "Data: <NEW_DATE>" ở góc phải,
và số mới trên trang Overview. Bấm thử một ngày cũ trong `history.html`
để chắc nó mở đúng bản archive.

Báo cáo ngắn: số mới từng mảng, thay đổi đáng chú ý so với hôm trước,
1–2 gợi ý hành động, mảng nào không đọc được và vì sao, trạng thái deploy + link.

Google Sheet tự cập nhật theo CSV, không cần làm gì thêm.
