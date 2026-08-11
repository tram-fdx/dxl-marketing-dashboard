#!/usr/bin/env python3
"""Snapshot of 11 Aug 2026 — social and SEO read live in Chrome.

The audit snapshot for this date is written by scripts/crawl_audit.py, not here.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import row, write_snapshot  # noqa: E402

DATE = "2026-08-11"
REPO = pathlib.Path(__file__).resolve().parent.parent

write_snapshot(
    REPO / "data" / "social" / f"{DATE}.json",
    {
        "date": DATE,
        "source": "social",
        "provenance": "read live in Chrome on 11 Aug 2026; Meta and YouTube report the 28 days to 9 Aug, LinkedIn the 30 days to 9 Aug",
        "window": {
            "vi": "28 ngày: 13/7 – 9/8/2026 (LinkedIn: 11/7 – 9/8)",
            "en": "28 days: 13 Jul – 9 Aug 2026 (LinkedIn: 11 Jul – 9 Aug)",
        },
        "metrics": [
            row("facebook", "followers", 115, window="point"),
            row("facebook", "views", 4827, change_pct=172.9),
            row("facebook", "viewers", 446, change_pct=50.7),
            row("facebook", "visits", 274, change_pct=407.4),
            row("facebook", "interactions", 170, change_pct=146.4),
            row("facebook", "video_3s", 112, change_pct=72.3),
            row("facebook", "watch_time_minutes", 51.3, unit="minutes", change_pct=168.9),
            row("facebook", "net_new_followers", 4, change_pct=100.0),
            row("facebook", "views_from_followers_pct", 47.3, unit="percent", change_pct=11.5),
            row("facebook", "conversations_started", 0, change_pct=0),

            row("instagram", "followers", 44, window="point"),
            row("instagram", "posts_total", 103, window="point"),
            row("instagram", "views", 907, change_pct=79.2),
            row("instagram", "reach", 196, change_pct=70.4),
            row("instagram", "reach_from_followers", 21, change_pct=90.9),
            row("instagram", "reach_from_non_followers", 176, change_pct=67.6),
            row("instagram", "interactions", 66, change_pct=842.9),
            row("instagram", "views_from_followers_pct", 53.1, unit="percent", change_pct=0.3),

            row("youtube", "views_28d", 28, change_pct=155.0),
            row("youtube", "watch_time_hours", 2.4, unit="hours", change_pct=999,
                note="YouTube reports >999%, the true figure is higher"),

            row("linkedin", "followers", 58, window="point"),
            row("linkedin", "new_followers_30d", 8, change_pct=300.0, window="30d"),
            row("linkedin", "impressions", 1678, change_pct=40.2, window="30d"),
            row("linkedin", "reactions", 64, change_pct=7.2, window="30d"),
            row("linkedin", "comments", 0, change_pct=0, window="30d"),
            row("linkedin", "reposts", 2, change_pct=0, window="30d"),
            row("linkedin", "page_views", 47, change_pct=123.8, window="30d"),
            row("linkedin", "unique_visitors", 22, change_pct=69.2, window="30d"),
        ],
        "insights": [
            {
                "level": "warn",
                "vi": "<b>Cả bốn kênh đứng yên so với hôm qua.</b> Cửa sổ 28 ngày trượt thêm một ngày nhưng FB views chỉ 4.777 → 4.827, IG và YouTube không đổi một con số nào. Không có bài mới nào được đăng từ 7/8.",
                "en": "<b>All four channels are flat against yesterday.</b> The 28-day window rolled forward a day, yet Facebook views moved only 4,777 → 4,827 and Instagram and YouTube did not shift at all. Nothing new has been published since 7 Aug.",
            },
            {
                "level": "warn",
                "vi": "<b>LinkedIn bắt đầu hạ nhiệt:</b> impressions 1.706 → 1.678 và mức tăng so kỳ trước tụt từ +44,7% xuống +40,2%. Bài ngày 3/8 đã hết đà — kênh mạnh nhất đang cần bài mới.",
                "en": "<b>LinkedIn is cooling:</b> impressions slipped 1,706 → 1,678 and the gain against the prior period eased from +44.7% to +40.2%. The 3 Aug post has spent its run — the strongest channel needs fresh material.",
            },
            {
                "level": "bad",
                "vi": "<b>Bốn ngày không đăng bài.</b> Đây là nguyên nhân chung của cả hai điểm trên. Meta trả số trễ 2 ngày nên khoảng lặng này sẽ còn hiện rõ hơn trong số liệu vài ngày tới.",
                "en": "<b>Four days without a post.</b> That single fact explains both points above. Meta reports on a two-day lag, so this quiet stretch will show up more sharply in the numbers over the next few days.",
            },
        ],
    },
)

write_snapshot(
    REPO / "data" / "seo" / f"{DATE}.json",
    {
        "date": DATE,
        "source": "seo",
        "provenance": "GSC and Ahrefs read live in Chrome on 11 Aug 2026; GA4 not re-read, collection has been faulty since ~29 Jul",
        "window": {
            "vi": "GSC: 28 ngày tới 8/8/2026 · Ahrefs: số tại thời điểm 11/8",
            "en": "GSC: 28 days to 8 Aug 2026 · Ahrefs: as at 11 Aug",
        },
        "metrics": [
            row("gsc", "clicks", 72, note="74 ngày 10/8 / was 74 on 10 Aug"),
            row("gsc", "impressions", 1370, note="GSC hiển thị 1.37K — đã làm tròn / GSC displays 1.37K, rounded"),
            row("gsc", "ctr", 5.3, unit="percent", note="5.5% ngày 10/8 / was 5.5% on 10 Aug"),
            row("gsc", "avg_position", 29.4, unit="position"),
            row("ahrefs", "referring_domains", 397, window="point", note="395 ngày 10/8 / was 395 on 10 Aug"),
            row("ahrefs", "backlinks", 404, window="point", note="401 ngày 10/8 / was 401 on 10 Aug"),
            row("ahrefs", "domain_rating", 0, unit="score", window="point"),
            row("ahrefs", "organic_keywords", 0, window="point"),
            row("ai", "chatgpt_responses", 10, window="point", note="3 trang được trích / 3 pages cited"),
            row("ai", "copilot_responses", 8, window="point", note="2 trang được trích / 2 pages cited"),
            row("ai", "ai_overview_responses", 0, window="point"),
            row("ai", "gemini_responses", 0, window="point"),
            row("ai", "perplexity_responses", 0, window="point"),
        ],
        "insights": [
            {
                "level": "good",
                "vi": "<b>Backlink vẫn chảy đều:</b> referring domains 395 → 397, backlinks 401 → 404. Ba ngày liên tiếp tăng, nhưng Domain Rating vẫn đứng 0 — link đến từ nguồn không có sức nặng.",
                "en": "<b>Backlinks keep arriving:</b> referring domains 395 → 397, backlinks 401 → 404. Three consecutive days of growth, yet Domain Rating holds at 0 — the links carry no weight.",
            },
            {
                "level": "warn",
                "vi": "<b>CTR giảm 5,5% → 5,3%</b> trong khi impressions tăng 1,34K → 1,37K và clicks giảm 74 → 72. Site đang xuất hiện nhiều hơn nhưng được bấm ít hơn — dấu hiệu title/meta chưa khớp truy vấn.",
                "en": "<b>CTR fell 5.5% → 5.3%</b> while impressions rose 1.34K → 1.37K and clicks dropped 74 → 72. The site is surfacing more but being clicked less — a sign the titles and meta descriptions do not match the queries.",
            },
            {
                "level": "info",
                "vi": "<b>AI citations giữ nguyên:</b> ChatGPT 10 câu trả lời / 3 trang, Copilot 8 / 2. Gemini, Perplexity và AI Overviews vẫn bằng 0 — chưa lan sang nền tảng nào khác.",
                "en": "<b>AI citations are unchanged:</b> ChatGPT 10 responses across 3 pages, Copilot 8 across 2. Gemini, Perplexity and AI Overviews remain at zero — nothing has spread to another platform yet.",
            },
            {
                "level": "warn",
                "vi": "<b>GA4 vẫn chưa đọc lại</b> — lỗi thu thập từ ~29/7 chưa được xác nhận đã sửa. Đây là việc cần xử lý trước khi báo cáo tháng.",
                "en": "<b>GA4 still has not been re-read</b> — the collection fault from ~29 Jul is unconfirmed as fixed. This needs resolving before the monthly report.",
            },
        ],
    },
)

print(f"wrote {DATE}: social + seo")
