from __future__ import annotations

from hoxit.reports import dedup_articles, eastmoney_reports

from conftest import JsonResponse


def test_eastmoney_reports_paginates_until_total_page():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["params"]["pageNo"])
        return JsonResponse({"data": [{"title": f"r{len(calls)}"}], "TotalPage": 2})

    rows = eastmoney_reports("688017", max_pages=5, http_get=fake_get, sleep=lambda _: None)
    assert len(rows) == 2
    assert calls == ["1", "2"]


def test_dedup_articles_keeps_highest_score_and_sorts_by_date():
    rows = dedup_articles([
        {"uid": "a", "score": 1, "publish_date": "2026-01-01"},
        {"uid": "a", "score": 2, "publish_date": "2026-01-01"},
        {"uid": "b", "score": 1, "publish_date": "2026-02-01"},
    ])
    assert [row["uid"] for row in rows] == ["b", "a"]
    assert rows[1]["score"] == 2
