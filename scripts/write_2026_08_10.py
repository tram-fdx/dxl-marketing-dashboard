#!/usr/bin/env python3
"""Snapshot of 10 Aug 2026, read live in Chrome.

Audit is deliberately absent: re-crawling 76 pages was not run today, so no
audit snapshot is written rather than a copy of the 7 Aug numbers wearing
today's date. The overview falls back to the last audit day it does have.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dxl_data import row, write_snapshot  # noqa: E402

DATE = "2026-08-10"
REPO = pathlib.Path(__file__).resolve().parent.parent

write_snapshot(
    REPO / "data" / "social" / f"{DATE}.json",
    {
        "date": DATE,
        "source": "social",
        "provenance": "read live in Chrome on 10 Aug 2026; Meta and YouTube report the 28 days to 8 Aug, LinkedIn the 30 days to 8 Aug",
        "window": {
            "vi": "28 ngày: 12/7 – 8/8/2026 (LinkedIn: 10/7 – 8/8)",
            "en": "28 days: 12 Jul – 8 Aug 2026 (LinkedIn: 10 Jul – 8 Aug)",
        },
        "metrics": [
            row("facebook", "followers", 115, window="point"),
            row("facebook", "views", 4777, change_pct=169.7),
            row("facebook", "viewers", 441, change_pct=50.0),
            row("facebook", "visits", 271, change_pct=411.3),
            row("facebook", "interactions", 168, change_pct=140.0),
            row("facebook", "video_3s", 113, change_pct=76.6),
            row("facebook", "watch_time_minutes", 51.6, unit="minutes", change_pct=173.7),
            row("facebook", "net_new_followers", 4, change_pct=100.0),
            row("facebook", "views_from_followers_pct", 47.7, unit="percent", change_pct=10.9),
            row("facebook", "conversations_started", 0, change_pct=0),

            row("instagram", "followers", 44, window="point"),
            row("instagram", "posts_total", 103, window="point"),
            row("instagram", "views", 909, change_pct=80.7),
            row("instagram", "reach", 196, change_pct=71.9),
            row("instagram", "reach_from_followers", 21, change_pct=110.0),
            row("instagram", "reach_from_non_followers", 176, change_pct=67.6),
            row("instagram", "interactions", 66, change_pct=842.9),
            row("instagram", "views_from_followers_pct", 53.1, unit="percent", change_pct=0.6),

            row("youtube", "views_28d", 28, change_pct=155.0),
            row("youtube", "watch_time_hours", 2.4, unit="hours", change_pct=999,
                note="YouTube reports >999%, the true figure is higher"),

            row("linkedin", "followers", 58, window="point"),
            row("linkedin", "new_followers_30d", 8, change_pct=300.0, window="30d"),
            row("linkedin", "impressions", 1706, change_pct=44.7, window="30d"),
            row("linkedin", "reactions", 65, change_pct=7.1, window="30d"),
            row("linkedin", "comments", 0, change_pct=0, window="30d"),
            row("linkedin", "reposts", 2, change_pct=0, window="30d"),
            row("linkedin", "page_views", 47, change_pct=123.8, window="30d"),
            row("linkedin", "unique_visitors", 22, change_pct=69.2, window="30d"),
        ],
        "insights": [
            {
                "level": "good",
                "vi": "<b>Facebook</b> tăng mạnh nhất: 4.777 lượt xem (+169,7%) và 271 lượt truy cập trang (+411,3%). Phần lớn đến từ bài ngày 3/8 — một bài đạt 668 reach, gấp 3–6 lần các bài còn lại.",
                "en": "<b>Facebook</b> moved most: 4,777 views (+169.7%) and 271 page visits (+411.3%). Most of it traces to the 3 Aug post — 668 reach on its own, three to six times any other post.",
            },
            {
                "level": "good",
                "vi": "<b>LinkedIn</b> hiệu quả nhất trên mỗi follower: 1.706 hiển thị và 8 follower mới (+300%) chỉ với 58 người theo dõi. Đây là kênh B2B đáng đầu tư tiếp.",
                "en": "<b>LinkedIn</b> works hardest per follower: 1,706 impressions and 8 new followers (+300%) off a base of 58. This is the B2B channel worth pressing.",
            },
            {
                "level": "warn",
                "vi": "<b>Instagram</b> tương tác +842,9% nhưng chỉ từ 7 lên 66 — nền quá nhỏ nên con số phần trăm không nói lên nhiều. Reach 196 vẫn thấp, 90% đến từ người chưa theo dõi.",
                "en": "<b>Instagram</b> interactions are up 842.9% — but from 7 to 66, so the percentage flatters a tiny base. Reach of 196 is still low, and 90% of it comes from non-followers.",
            },
        ],
    },
)

write_snapshot(
    REPO / "data" / "seo" / f"{DATE}.json",
    {
        "date": DATE,
        "source": "seo",
        "provenance": "GSC and Ahrefs read live in Chrome on 10 Aug 2026; GA4 not re-read today because collection has been faulty since ~29 Jul",
        "window": {
            "vi": "GSC: 28 ngày tới 7/8/2026 · Ahrefs: số tại thời điểm 10/8",
            "en": "GSC: 28 days to 7 Aug 2026 · Ahrefs: as at 10 Aug",
        },
        "metrics": [
            row("gsc", "clicks", 74),
            row("gsc", "impressions", 1340, note="GSC hiển thị 1.34K — đã làm tròn / GSC displays 1.34K, rounded"),
            row("gsc", "ctr", 5.5, unit="percent"),
            row("gsc", "avg_position", 29.2, unit="position", note="tốt hơn 29.6 ngày 7/8 / better than 29.6 on 7 Aug"),
            row("ahrefs", "referring_domains", 395, window="point", note="366 ngày 7/8 / was 366 on 7 Aug"),
            row("ahrefs", "backlinks", 401, window="point", note="372 ngày 7/8 / was 372 on 7 Aug"),
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
                "vi": "<b>Lần đầu đo được hiện diện trên AI.</b> Ahrefs ghi nhận ChatGPT trích DX Living trong 10 câu trả lời (3 trang) và Copilot 8 câu (2 trang). Báo cáo 7/8 còn ghi '0 prompt được track'.",
                "en": "<b>AI visibility is measurable for the first time.</b> Ahrefs records DX Living cited in 10 ChatGPT responses across 3 pages, and 8 Copilot responses across 2. The 7 Aug report still read '0 prompts tracked'.",
            },
            {
                "level": "good",
                "vi": "<b>Backlink tăng nhanh:</b> referring domains 366 → 395 và backlinks 372 → 401 chỉ trong 3 ngày. Nhưng Domain Rating vẫn 0 — link mới chưa đủ chất lượng để đẩy DR.",
                "en": "<b>Backlinks are accumulating fast:</b> referring domains 366 → 395 and backlinks 372 → 401 in three days. Domain Rating is still 0, so the new links are not yet strong enough to move it.",
            },
            {
                "level": "bad",
                "vi": "<b>0 từ khoá organic và 0 organic traffic theo Ahrefs</b>, trong khi GSC vẫn ghi nhận 74 clicks. Chênh lệch này nghĩa là site đang xuất hiện ở vị trí trung bình 29.2 — quá sâu để Ahrefs tính là có thứ hạng.",
                "en": "<b>Ahrefs shows 0 organic keywords and 0 organic traffic</b> while GSC still records 74 clicks. The gap says the site is surfacing at an average position of 29.2 — too deep for Ahrefs to count it as ranking.",
            },
            {
                "level": "warn",
                "vi": "<b>GA4 chưa đọc lại hôm nay</b> vì lỗi thu thập từ ~29/7 vẫn chưa được xác nhận đã sửa. Số session trên dashboard vẫn là của ngày 7/8.",
                "en": "<b>GA4 was not re-read today</b> — the collection fault from ~29 Jul has not been confirmed fixed. The session figures on the dashboard are still those of 7 Aug.",
            },
        ],
    },
)

print(f"wrote {DATE}: social + seo (audit deliberately skipped)")
