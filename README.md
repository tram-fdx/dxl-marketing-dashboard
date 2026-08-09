# DX Living — Marketing Dashboard

Ba dashboard trong một site, song ngữ VI/EN, cập nhật tự động mỗi ngày.
Three dashboards on one site, bilingual VI/EN, updated automatically every day.

**Live:** https://tram-fdx.github.io/dxl-marketing-dashboard/

| Trang | Nội dung |
|---|---|
| `index.html` | Tổng quan — KPI đầu mục của cả ba mảng |
| `social.html` | Facebook · Instagram · YouTube · LinkedIn |
| `seo.html` | Google Search Console · GA4 · Ahrefs · AI visibility |
| `audit.html` | Sức khoẻ kỹ thuật dxliving.com |
| `history.html` | Lịch sử từng ngày |

Đây là repo **độc lập**. Nó không đọc, không ghi và không phụ thuộc vào
`dxl-social-dashboard-site`, `dxliving-seo-report` hay `dxl-seo-audit`.

## Dữ liệu đi từ đâu tới đâu

```
Chrome / API miễn phí
        ↓  (tác vụ tự động chạy mỗi sáng)
data/<mảng>/<ngày>.json     ← nguồn sự thật, một file một ngày một mảng
        ↓  scripts/build_csv.py
data/social.csv · seo.csv · audit.csv · all.csv
        ↓  IMPORTDATA
Google Sheets               ← mở ra là thấy số mới nhất
        ↓  scripts/freeze_day.py
archive/<ngày>/             ← bản HTML đóng băng, không bao giờ bị ghi đè
```

Mọi thứ chạy trên hạ tầng miễn phí: GitHub Pages (repo public), Google Sheets,
và Chrome trên máy. Không dùng API trả phí.

## Định dạng một snapshot

`data/<source>/<YYYY-MM-DD>.json`:

```json
{
  "date": "2026-08-07",
  "source": "seo",
  "provenance": "read live in Chrome",
  "window": {"vi": "28 ngày qua", "en": "Last 28 days"},
  "metrics": [
    {"channel": "gsc", "metric": "clicks", "value": 72,
     "unit": "count", "change_pct": 53.0, "window": "28d", "note": ""}
  ]
}
```

Cột CSV cố định: `date, source, channel, metric, value, unit, change_pct, window, note`.
**Không đổi thứ tự** — công thức trong Google Sheet tham chiếu theo vị trí cột.

## Chạy tay

```bash
python3 scripts/build_csv.py   --repo .          # dựng lại CSV từ mọi snapshot
python3 scripts/patch_pages.py --repo .          # trỏ date picker về index riêng từng mảng
python3 scripts/inject_nav.py  --repo .          # gắn lại thanh chuyển tab
python3 scripts/freeze_day.py  --repo . --date 2026-08-07 \
    --label-vi "..." --label-en "..." --dry-run  # xem trước rồi bỏ --dry-run
```

Thứ tự bắt buộc khi thêm một ngày mới: ghi snapshot JSON → `build_csv` →
`patch_pages` → `inject_nav` → `freeze_day`.

## Nguyên tắc

- Không bịa số. Kênh nào không đọc được thì bỏ metric đó ra khỏi snapshot và
  ghi lý do vào `provenance`, không suy đoán và không giữ số cũ như thể là số mới.
- Ngày đã đóng băng là đã đóng. `freeze_day.py` từ chối ghi đè trừ khi có `--force`.
- `data/<source>/<ngày>.json` là nguồn sự thật duy nhất. CSV và HTML đều dựng lại
  được từ đó, nên sửa snapshot là sửa được tất cả.
