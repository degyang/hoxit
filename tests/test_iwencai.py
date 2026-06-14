from __future__ import annotations

import tomllib
from pathlib import Path

from hoxit import filings, fundamentals, iwencai, reports, signals

from conftest import JsonResponse


def test_iwencai_route_table_loads_market_and_search_routes():
    routes = iwencai.load_routes()
    assert routes["market"].skill_id == "hithink-market-query"
    assert routes["report"].kind == "comprehensive_search"


def test_routes_json_is_declared_as_package_data():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    assert "routes.json" in pyproject["tool"]["setuptools"]["package-data"]["hoxit"]


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
    assert "claw_headers" in iwencai.query2data(route="market", query="贵州茅台最新价", limit="1", http_post=fake_post)


def test_iwencai_query2data_wraps_list_and_text_like_original_skills():
    def fake_list_post(url, **kwargs):
        return JsonResponse([{"a": 1}])

    list_response = iwencai.query2data(route="market", query="列表", http_post=fake_list_post)
    assert list_response["data"] == [{"a": 1}]
    assert list_response["claw_headers"]["X-Claw-Skill-Id"] == "hithink-market-query"

    class TextResponse:
        status_code = 200
        text = "plain text"

        def json(self):
            raise ValueError("not json")

    text_response = iwencai.query2data(route="market", query="文本", http_post=lambda url, **kwargs: TextResponse())
    assert text_response["text_response"] == "plain text"
    assert text_response["trace_id"]


def test_reports_iwencai_search_uses_comprehensive_search_payload_extra():
    calls = []

    def fake_post(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse({"status_code": 0, "data": [{"title": "研报1"}, {"title": "研报2"}]})

    rows = reports.iwencai_search("贵州茅台 研报", channel="report", size=1, http_post=fake_post)
    assert rows == [{"title": "研报1"}]
    assert set(calls[0][1]["json"]) == {"channels", "app_id", "query"}
    assert calls[0][1]["headers"]["X-Claw-Skill-Id"] == "report-search"


def test_comprehensive_search_transparently_returns_http_error_body():
    class ErrorResponse:
        status_code = 401
        text = '{"error":{"code":"AUTH_FAILED","message":"bad key"}}'

        def json(self):
            return {"error": {"code": "AUTH_FAILED", "message": "bad key"}}

    response = iwencai.comprehensive_search(
        route="report",
        query="贵州茅台 研报",
        http_post=lambda url, **kwargs: ErrorResponse(),
    )
    assert response == {"error": {"code": "AUTH_FAILED", "message": "bad key"}}


def test_individual_info_falls_back_to_iwencai_basicinfo(monkeypatch):
    monkeypatch.setattr(fundamentals, "em_get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("eastmoney down")))
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


def test_individual_info_iwencai_fallback_handles_dynamic_date_columns(monkeypatch):
    monkeypatch.setattr(fundamentals, "em_get", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("eastmoney down")))
    monkeypatch.setattr(
        fundamentals.iwencai,
        "query_rows",
        lambda route, query, **kwargs: [
            {
                "股票代码": "600519.SH",
                "股票简称": "贵州茅台",
                "所属行业": "白酒",
                "总股本[20260601]": 1252270215.0,
                "流通A股[20260601]": 1252270215.0,
                "上市日期[20260601]": "20010827",
            }
        ],
    )

    result = fundamentals.individual_info("600519")
    assert result["total_shares"] == 1252270215.0
    assert result["float_shares"] == 1252270215.0
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


# ── summarize_query2data_response ──────────────────────────────


def test_summarize_adds_metadata_when_datas_present():
    """query2data 响应带 datas 时应追加 success/code_count/has_more 等摘要字段。"""
    response = {
        "datas": [{"a": 1}, {"b": 2}],
        "code_count": "5",
    }
    summarized = iwencai.summarize_query2data_response(response, query="测试", page="1", limit="2")
    assert summarized["success"] is True
    assert summarized["query"] == "测试"
    assert summarized["code_count"] == 5
    assert summarized["returned_count"] == 2
    assert summarized["page"] == "1"
    assert summarized["limit"] == "2"
    assert summarized["has_more"] is True
    assert "pagination_tip" in summarized
    assert summarized["datas"] == [{"a": 1}, {"b": 2}]


def test_summarize_detects_no_more_pages():
    """当所有记录已返回完时 has_more 应为 False 且无 pagination_tip。"""
    response = {"datas": [{"x": 1}], "code_count": "1"}
    summarized = iwencai.summarize_query2data_response(response, query="q", page="1", limit="10")
    assert summarized["has_more"] is False
    assert "pagination_tip" not in summarized


def test_summarize_adds_empty_tip_when_no_datas():
    """返回空数据时应提示 empty_data_tip。"""
    response = {"datas": [], "code_count": "0"}
    summarized = iwencai.summarize_query2data_response(response, query="q", page="1", limit="10")
    assert summarized["returned_count"] == 0
    assert "empty_data_tip" in summarized
    assert "未查询到匹配数据" in summarized["empty_data_tip"]


def test_summarize_passes_through_non_dict_or_missing_datas():
    """非 dict 或无 datas 的响应应原样返回。"""
    assert iwencai.summarize_query2data_response("raw string", query="q", page="1", limit="10") == "raw string"
    assert iwencai.summarize_query2data_response({"status": "ok"}, query="q", page="1", limit="10") == {"status": "ok"}


def test_summarize_handles_non_numeric_code_count():
    """code_count 非数字时应回退为 0 而非崩溃。"""
    response = {"datas": [{"a": 1}], "code_count": "N/A"}
    summarized = iwencai.summarize_query2data_response(response, query="q", page="1", limit="10")
    assert summarized["code_count"] == 0


# ── 完整 route 表（19 条） ─────────────────────────────────────


def test_all_19_routes_load_from_package_resource():
    """routes.json 应包含全部 19 条 route。"""
    routes = iwencai.load_routes()
    assert len(routes) == 19, f"期望 19 条 route，实际 {len(routes)}"

    query2data_keys = {k for k, r in routes.items() if r.kind == "query2data"}
    search_keys = {k for k, r in routes.items() if r.kind == "comprehensive_search"}

    assert len(query2data_keys) == 17
    assert search_keys == {"announcement", "report"}


def test_every_query2data_route_has_hithink_skill_id():
    """所有 query2data route 的 skill_id 应以 hithink- 开头。"""
    routes = iwencai.load_routes()
    for key, route in routes.items():
        if route.kind == "query2data":
            assert route.skill_id.startswith("hithink-"), f"{key}: {route.skill_id}"


def test_search_routes_have_channels_and_app_id():
    """公告/研报 route 必须有 channels 和 app_id。"""
    routes = iwencai.load_routes()
    for key in ("announcement", "report"):
        route = routes[key]
        assert route.channels, f"{key} 缺少 channels"
        assert route.app_id, f"{key} 缺少 app_id"


# ── Route 解析与校验 ──────────────────────────────────────────


def test_get_route_by_string_resolves_from_table():
    """通过字符串获取 route 应查表并返回 Route 对象。"""
    route = iwencai.get_route("market")
    assert isinstance(route, iwencai.Route)
    assert route.key == "market"
    assert route.skill_id == "hithink-market-query"


def test_get_route_passes_route_object_through():
    """传入 Route 对象时应直接返回。"""
    original = iwencai.Route(key="test", kind="query2data", skill_id="test-skill", version="1.0.0")
    assert iwencai.get_route(original) is original


def test_get_route_unknown_raises_iwencai_error():
    """未知 route 名称应抛出 IwencaiError。"""
    try:
        iwencai.get_route("nonexistent-route")
        assert False, "应该抛出异常"
    except iwencai.IwencaiError as exc:
        assert "unknown iwencai route" in str(exc)


def test_query2data_rejects_comprehensive_search_route():
    """对 comprehensive_search route 调用 query2data 应报错。"""
    try:
        iwencai.query2data(route="report", query="test", http_post=lambda **kw: None)
        assert False, "应该抛出异常"
    except iwencai.IwencaiError as exc:
        assert "不是 query2data route" in str(exc)


def test_comprehensive_search_rejects_query2data_route():
    """对 query2data route 调用 comprehensive_search 应报错。"""
    try:
        iwencai.comprehensive_search(route="market", query="test", http_post=lambda **kw: None)
        assert False, "应该抛出异常"
    except iwencai.IwencaiError as exc:
        assert "不是 comprehensive_search route" in str(exc)


# ── CLI: iwc 层解析 ───────────────────────────────────────────


def test_cli_iwc_routes_lists_all():
    """hoxit iwc routes 应能解析且无 --kind 过滤。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["iwc", "routes"])
    assert args.layer == "iwc"
    assert args.action == "routes"
    assert args.kind is None


def test_cli_iwc_routes_filter_by_kind():
    """hoxit iwc routes --kind query2data 应正确设置 kind 参数。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["iwc", "routes", "--kind", "query2data"])
    assert args.kind == "query2data"


def test_cli_iwc_query_parses_all_options():
    """hoxit iwc query 应解析 route/query/page/limit/api-key 等全部选项。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    args = parser.parse_args([
        "iwc", "query",
        "--route", "market",
        "--query", "贵州茅台 最新价",
        "--page", "2",
        "--limit", "20",
        "--api-key", "test-key",
        "--call-type", "retry",
        "--timeout", "60",
        "--raw",
    ])
    assert args.layer == "iwc"
    assert args.action == "query"
    assert args.route == "market"
    assert args.query == "贵州茅台 最新价"
    assert args.page == "2"
    assert args.limit == "20"
    assert args.api_key == "test-key"
    assert args.call_type == "retry"
    assert args.timeout == 60
    assert args.raw is True


def test_cli_iwc_query_short_flags():
    """hoxit iwc query -r -q 短参数应正确解析。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["iwc", "query", "-r", "finance", "-q", "ROE>20%"])
    assert args.route == "finance"
    assert args.query == "ROE>20%"
    assert args.page == "1"  # 默认
    assert args.limit == "10"  # 默认


def test_cli_iwc_query_rejects_non_positive_page_and_limit():
    """hoxit iwc query 的 page/limit 应保持迁移前的正整数约束。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    for option in ("--page", "--limit"):
        try:
            parser.parse_args(["iwc", "query", "-r", "finance", "-q", "ROE", option, "0"])
            assert False, f"{option} 应拒绝 0"
        except SystemExit:
            pass


def test_cli_iwc_search_parses_options():
    """hoxit iwc search 应解析 search 专属选项。"""
    from hoxit.cli import build_parser

    parser = build_parser()
    args = parser.parse_args([
        "iwc", "search",
        "--route", "announcement",
        "--query", "分红公告",
        "--api-key", "sk-xxx",
    ])
    assert args.layer == "iwc"
    assert args.action == "search"
    assert args.route == "announcement"
    assert args.query == "分红公告"


# ── CLI: iwc dispatch (dry-run with mock http_post) ────────────


def test_cli_iwc_routes_dispatch_returns_all_without_kind():
    """iwc routes dispatch 应返回全部 19 条 route（不传 kind）。"""
    from hoxit.cli import build_parser, run

    parser = build_parser()
    args = parser.parse_args(["iwc", "routes"])
    result = run(args)
    assert isinstance(result, list)
    assert len(result) == 19
    for entry in result:
        assert "route" in entry
        assert "kind" in entry
        assert "skill_id" in entry
        assert "description" in entry


def test_cli_iwc_routes_dispatch_filters_by_kind():
    """iwc routes --kind query2data 应只返回 17 条。"""
    from hoxit.cli import build_parser, run

    parser = build_parser()
    args = parser.parse_args(["iwc", "routes", "--kind", "query2data"])
    result = run(args)
    assert len(result) == 17
    assert all(r["kind"] == "query2data" for r in result)


def test_cli_iwc_query_dispatch_with_summary(monkeypatch, capsys):
    """iwc query dispatch 应调用 summarize 包装（非 raw 模式）。"""
    from hoxit.cli import build_parser, run

    calls = {}

    def fake_query2data(*, route, query, page, limit, api_key, call_type, timeout, **kwargs):
        calls["route"] = route
        calls["query"] = query
        return {"datas": [{"code": "600519"}], "code_count": "1"}

    monkeypatch.setattr("hoxit.iwencai.query2data", fake_query2data)
    monkeypatch.setattr("hoxit.iwencai.get_api_key", lambda *a, **kw: "test-key")

    parser = build_parser()
    args = parser.parse_args(["iwc", "query", "-r", "market", "-q", "茅台"])
    result = run(args)
    assert result["success"] is True
    assert result["returned_count"] == 1
    assert result["datas"] == [{"code": "600519"}]
    assert calls["query"] == "茅台"


def test_cli_iwc_query_dispatch_raw_mode(monkeypatch):
    """iwc query --raw 应返回 gateway 原始响应（不添加摘要元数据）。"""
    from hoxit.cli import build_parser, run

    raw_response = {"datas": [{"x": 1}], "code_count": "100", "chunks_info": {}}

    monkeypatch.setattr("hoxit.iwencai.query2data", lambda **kw: raw_response)
    monkeypatch.setattr("hoxit.iwencai.get_api_key", lambda *a, **kw: "test-key")

    parser = build_parser()
    args = parser.parse_args(["iwc", "query", "-r", "market", "-q", "test", "--raw"])
    result = run(args)
    assert result is raw_response


def test_cli_iwc_query_rejects_search_route():
    """iwc query 使用 report route 应报错退出。"""
    from hoxit.cli import build_parser, run

    parser = build_parser()
    args = parser.parse_args(["iwc", "query", "-r", "report", "-q", "test"])
    try:
        run(args)
        assert False, "应该抛出 SystemExit"
    except SystemExit as exc:
        assert "不是 query2data" in str(exc)


def test_cli_iwc_search_rejects_query_route():
    """iwc search 使用 market route 应报错退出。"""
    from hoxit.cli import build_parser, run

    parser = build_parser()
    args = parser.parse_args(["iwc", "search", "-r", "market", "-q", "test"])
    try:
        run(args)
        assert False, "应该抛出 SystemExit"
    except SystemExit as exc:
        assert "不是 comprehensive_search" in str(exc)
