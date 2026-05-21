from __future__ import annotations

from hoxit.filings import cninfo_reports

from conftest import JsonResponse


def test_cninfo_reports_uses_new_org_id_stock_format():
    calls = []

    def fake_post(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({
            "announcements": [
                {
                    "announcementTitle": "年度报告",
                    "announcementTypeName": "定期报告",
                    "announcementTime": "2026-04-30",
                    "announcementId": "123",
                }
            ]
        })

    rows = cninfo_reports("688017", "20260101", "20260516", http_post=fake_post)
    payload = calls[0]["data"]
    assert payload["stock"] == "688017,gssh0688017"
    assert payload["column"] == ""
    assert payload["seDate"] == "2026-01-01~2026-05-16"
    assert rows[0]["url"].endswith("annoId=123")
