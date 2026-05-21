from __future__ import annotations

from hoxit import filings, fundamentals, iwencai, reports, signals

from conftest import JsonResponse


def test_iwencai_route_table_loads_market_and_search_routes():
    routes = iwencai.load_routes()
    assert routes["market"].skill_id == "hithink-market-query"
    assert routes["report"].kind == "comprehensive_search"


def test_iwencai_query2data_builds_skill_headers():
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse({"datas": [{"a": 1}]})

    rows = iwencai.query_rows("market", "贵州茅台最新价", limit="3", http_post=fake_post)
    assert rows == [{"a": 1}]
    assert calls[0][0].endswith("/v1/query2data")
    assert calls[0][1]["headers"]["X-Claw-Skill-Id"] == "hithink-market-query"
    assert calls[0][1]["json"]["limit"] == "3"


def test_reports_iwencai_search_uses_comprehensive_search_payload_extra():
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse({"status_code": 0, "data": [{"title": "研报"}]})

    rows = reports.iwencai_search("贵州茅台 研报", channel="report", size=3, http_post=fake_post)
    assert rows == [{"title": "研报"}]
    assert calls[0][1]["json"]["size"] == 3
    assert calls[0][1]["headers"]["X-Claw-Skill-Id"] == "report-search"


def test_individual_info_falls_back_to_iwencai_basicinfo(monkeypatch):
    monkeypatch.setattr(fundamentals, "_requests_get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("eastmoney down")))
    monkeypatch.setattr(
        fundamentals.iwencai,
        "query_rows",
        lambda route, query, **kwargs: [
            {
                "股票代码": "600519.SH",
                "股票简称": "贵州茅台",
                "所属同花顺行业": ["食品饮料", "白酒", "白酒III"],
                "总股本[20260521]": 1252270215.0,
                "流通a股[20260521]": 1252270215.0,
                "上市日期[20260521]": "20010827",
                "最新价": "1311.0",
                "最新a股流通市值": 1234567890,
            }
        ],
    )

    result = fundamentals.individual_info("600519")
    assert result["code"] == "600519.SH"
    assert result["industry"] == "食品饮料 / 白酒 / 白酒III"
    assert result["list_date"] == "20010827"


def test_cninfo_reports_falls_back_to_iwencai_announcement(monkeypatch):
    monkeypatch.setattr(
        filings,
        "_requests_post",
        lambda *args, **kwargs: JsonResponse({"announcements": []}),
    )
    monkeypatch.setattr(
        filings.iwencai,
        "search_rows",
        lambda route, query, **kwargs: [
            {"title": "公告标题", "type": "公告", "publish_date": "2026-05-21 09:00:00", "url": "https://example.test"}
        ],
    )

    rows = filings.cninfo_reports("600519", "20260101", "20260521")
    assert rows == [{
        "title": "公告标题",
        "type": "公告",
        "date": "2026-05-21 09:00:00",
        "url": "https://example.test",
        "summary": "",
    }]


def test_daily_dragon_tiger_falls_back_to_iwencai_event(monkeypatch):
    monkeypatch.setattr(signals, "eastmoney_datacenter", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        signals.iwencai,
        "query_rows",
        lambda route, query, **kwargs: [
            {
                "股票代码": "001896.SZ",
                "股票简称": "豫能控股",
                "上榜原因": "日涨幅偏离值达7%的证券",
                "最新价": "16.37",
                "最新涨跌幅": 10.0,
                "净买入额[20260521]": 379056747.63,
                "买入额[20260521]": 379232134.63,
                "卖出额[20260521]": 175387.0,
                "换手率[20260521]": 8.1,
            }
        ],
    )

    result = signals.daily_dragon_tiger("2026-05-21")
    assert result["total_records"] == 1
    assert result["stocks"][0]["code"] == "001896.SZ"
    assert result["stocks"][0]["net_buy_wan"] == 37905.7
