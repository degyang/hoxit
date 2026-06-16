from __future__ import annotations

from hoxit import signals

from conftest import JsonResponse


def test_eastmoney_concept_blocks_parses_boards():
    payload = {
        "data": {
            "diff": {
                "BK1234": {"f14": "食品饮料", "f12": "BK1234", "f3": 1.5, "f128": "茅台"},
                "BK5678": {"f14": "贵州板块", "f12": "BK5678", "f3": 0.8, "f128": "贵州茅台"},
            }
        }
    }
    result = signals.eastmoney_concept_blocks("600519", http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert result["total"] == 2
    assert result["boards"][0]["name"] == "食品饮料"
    assert result["concept_tags"] == ["食品饮料", "贵州板块"]
    assert result["boards"][1]["lead_stock"] == "贵州茅台"


def test_eastmoney_concept_blocks_returns_empty_on_failure():
    def failing_get(*args, **kwargs):
        raise RuntimeError("network error")
    result = signals.eastmoney_concept_blocks("688017", http_get=failing_get)
    assert result == {"total": 0, "boards": [], "concept_tags": []}


def test_baidu_concept_blocks_is_alias():
    """baidu_concept_blocks 应作为 eastmoney_concept_blocks 的别名继续可用"""
    assert signals.baidu_concept_blocks is signals.eastmoney_concept_blocks


def test_eastmoney_datacenter_builds_common_request():
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse({"result": {"data": [{"SECURITY_CODE": "688017"}]}})

    rows = signals.eastmoney_datacenter("RPT_TEST", filter_str='(SECURITY_CODE="688017")', http_get=fake_get)
    assert rows == [{"SECURITY_CODE": "688017"}]
    assert calls[0][1]["params"]["reportName"] == "RPT_TEST"
    assert calls[0][1]["headers"]["Referer"] == "https://data.eastmoney.com/"


def test_lockup_expiry_uses_single_datacenter_window_query():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["params"])
        if "FREE_DATE>=" in kwargs["params"]["filter"]:
            return JsonResponse({"result": {"data": [{"FREE_DATE": "2026-05-14 00:00:00", "LIMITED_STOCK_TYPE": "首发", "FREE_SHARES_NUM": 10, "FREE_RATIO": "1%"}]}})
        return JsonResponse({"result": {"data": [{"FREE_DATE": "2025-05-14 00:00:00", "LIMITED_STOCK_TYPE": "首发", "FREE_SHARES_NUM": 5, "FREE_RATIO": "0.5%"}]}})

    result = signals.lockup_expiry("688017", "2026-05-12", forward_days=2, http_get=fake_get)
    assert len(calls) == 2
    assert "(FREE_DATE>='2026-05-12')(FREE_DATE<='2026-05-14')" in calls[1]["filter"]
    assert result["history"][0]["date"] == "2025-05-14"
    assert result["upcoming"][0]["date"] == "2026-05-14"


def test_northbound_cache_overwrites_same_date(tmp_path):
    signals.save_northbound_snapshot("2026-05-12", 1, 2, tmp_path)
    signals.save_northbound_snapshot("2026-05-12", 3, 4, tmp_path)
    rows = signals.load_northbound_history(base_dir=tmp_path)
    assert rows == [{"date": "2026-05-12", "hgt": "3", "sgt": "4"}]


def test_ths_hot_reason_can_exclude_st_stocks():
    payload = {
        "errocode": 0,
        "data": [
            {"code": "000001", "name": "平安银行"},
            {"code": "000002", "name": "ST测试"},
            {"code": "000003", "name": "*ST样本"},
        ],
    }
    rows = signals.ths_hot_reason("2026-05-12", exclude_st=True, http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert [row["code"] for row in rows] == ["000001"]


def test_push2his_fund_flow_parses_rows_and_headers():
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse({"data": {"klines": ["2026-05-12,100,-20,30,40,50,0"]}})

    rows = signals.stock_fund_flow_120d("600519", days=1, http_get=fake_get)
    assert calls[0][0].startswith("https://push2his.eastmoney.com")
    assert calls[0][1]["headers"]["Origin"] == "https://quote.eastmoney.com"
    assert calls[0][1]["params"]["secid"] == "1.600519"
    assert rows == [{"date": "2026-05-12", "main_net": 100.0, "small_net": -20.0, "mid_net": 30.0, "large_net": 40.0, "super_net": 50.0}]


def test_dragon_tiger_board_includes_seats_and_institution():
    def fake_get(url, **kwargs):
        report = kwargs["params"]["reportName"]
        if report == "RPT_DAILYBILLBOARD_DETAILSNEW":
            return JsonResponse({"result": {"data": [{"TRADE_DATE": "2026-05-12 00:00:00", "EXPLANATION": "测试原因", "BILLBOARD_NET_AMT": 12340000, "TURNOVERRATE": 8.9}]}})
        if report == "RPT_BILLBOARD_DAILYDETAILSBUY":
            return JsonResponse({"result": {"data": [{"OPERATEDEPT_NAME": "机构专用", "OPERATEDEPT_CODE": "0", "BUY": 2000000, "SELL": 100000, "NET": 1900000}]}})
        return JsonResponse({"result": {"data": [{"OPERATEDEPT_NAME": "卖出席位", "OPERATEDEPT_CODE": "1", "BUY": 100000, "SELL": 500000, "NET": -400000}]}})

    result = signals.dragon_tiger_board("688017", "2026-05-12", http_get=fake_get)
    assert result["records"][0]["net_buy"] == 1234.0
    assert result["seats"]["buy"][0]["name"] == "机构专用"
    assert result["institution"] == {"buy_amt": 200.0, "sell_amt": 0.0, "net_amt": 200.0}


def test_industry_comparison_fallback_to_eastmoney(monkeypatch):
    """当 iwencai 查询失败时，应回退到 eastmoney push2 API。"""
    # Mock iwencai.query_rows to return empty (triggers fallthrough)
    import hoxit.iwencai as iw_mod

    def _empty(*args, **kwargs):
        return []
    monkeypatch.setattr(iw_mod, "query_rows", _empty)

    payload = {"data": {"diff": [{"f14": "机器人", "f3": 2.5, "f12": "BK1234", "f104": 10, "f105": 2, "f140": "样本股", "f136": 5.1}]}}
    rows = signals.industry_comparison(1, http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert rows["top"][0]["name"] == "机器人"
    assert rows["top"][0]["leader"] == "样本股"


def test_compatibility_aliases_exist():
    assert signals.get_concept_blocks is signals.eastmoney_concept_blocks
    assert signals.get_dragon_tiger_board is signals.dragon_tiger_board
    assert signals.get_lockup_expiry is signals.lockup_expiry


# ── event_summary ───────────────────────────────────────────────


def test_event_summary_returns_computed_on_valid_data():
    """事件摘要应正确解析 iwencai event route 返回的数据。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [
                {
                    "股票代码": "600519.SH",
                    "事件标题": "贵州茅台发布2026年一季报，净利润同比增长15%",
                    "事件日期": "2026-04-20",
                    "事件类型": "业绩公告",
                    "催化剂": "业绩超预期",
                },
                {
                    "股票代码": "600519.SH",
                    "事件标题": "贵州茅台控股股东增持计划公告",
                    "事件日期": "2026-05-10",
                    "事件类型": "股东增持",
                    "催化剂": "大股东增持",
                },
            ]
        })

    result = signals.event_summary("600519", http_post=fake_post)
    assert result["status"] == "computed"
    assert result["code"] == "600519.SH"
    assert len(result["events"]) == 2
    assert result["events"][0]["title"] == "贵州茅台发布2026年一季报，净利润同比增长15%"
    assert result["events"][0]["sentiment"] == "positive"  # "增长" is positive keyword
    assert result["events"][1]["sentiment"] == "positive"  # "增持" is positive keyword
    assert result["positive_count"] == 2
    assert result["negative_count"] == 0
    assert len(result["catalysts"]) > 0
    assert result["warnings"] == []


def test_event_summary_returns_data_needed_on_empty_rows():
    """事件摘要在 iwencai 返回空数据时应返回 data_needed 状态。"""
    def fake_post(url, **kwargs):
        return JsonResponse({"datas": []})

    result = signals.event_summary("600519", http_post=fake_post)
    assert result["status"] == "data_needed"
    assert result["events"] == []
    assert result["catalysts"] == []
    assert result["positive_count"] == 0
    assert result["negative_count"] == 0
    assert len(result["warnings"]) > 0


def test_event_summary_handles_network_error():
    """事件摘要在网络异常时应返回 data_needed 而非抛出异常。"""
    def failing_post(url, **kwargs):
        raise RuntimeError("network error")

    result = signals.event_summary("600519", http_post=failing_post)
    assert result["status"] == "data_needed"
    assert result["code"] == "600519"


def test_event_summary_classifies_negative_sentiment():
    """事件摘要应能识别负面情绪事件。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [
                {
                    "股票代码": "000001.SZ",
                    "事件标题": "平安银行收到监管处罚通知",
                    "事件日期": "2026-05-01",
                    "事件类型": "监管处罚",
                },
                {
                    "股票代码": "000001.SZ",
                    "事件标题": "平安银行股东减持计划公告",
                    "事件日期": "2026-05-05",
                    "事件类型": "股东减持",
                },
                {
                    "股票代码": "000001.SZ",
                    "事件标题": "平安银行召开股东大会",
                    "事件日期": "2026-05-10",
                    "事件类型": "公司治理",
                },
            ]
        })

    result = signals.event_summary("000001", http_post=fake_post)
    assert result["status"] == "computed"
    assert result["positive_count"] == 0
    assert result["negative_count"] == 2  # "处罚" and "减持" are negative
    assert result["events"][0]["sentiment"] == "negative"
    assert result["events"][1]["sentiment"] == "negative"
    assert result["events"][2]["sentiment"] == "neutral"


def test_event_summary_normalizes_code():
    """事件摘要应正确处理带后缀的股票代码。"""
    calls = []

    def fake_post(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({"datas": []})

    signals.event_summary("600519.SH", http_post=fake_post)
    assert "600519" in calls[0]["json"]["query"]


def test_event_summary_limits_events_to_10():
    """事件摘要应最多返回 10 条事件记录。"""
    def fake_post(url, **kwargs):
        datas = [
            {"股票代码": "600519.SH", "事件标题": f"事件{i}", "事件日期": "2026-05-01"}
            for i in range(15)
        ]
        return JsonResponse({"datas": datas})

    result = signals.event_summary("600519", http_post=fake_post)
    assert len(result["events"]) == 10


def test_event_summary_handles_mixed_catalyst_formats():
    """事件摘要应能处理列表和字符串格式的催化剂字段。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [
                {
                    "股票代码": "600519.SH",
                    "事件标题": "事件1",
                    "催化剂": ["催化剂A", "催化剂B"],
                },
                {
                    "股票代码": "600519.SH",
                    "事件标题": "事件2",
                    "催化剂": "催化剂C",
                },
            ]
        })

    result = signals.event_summary("600519", http_post=fake_post)
    assert result["status"] == "computed"
    assert "催化剂A" in result["catalysts"]
    assert "催化剂B" in result["catalysts"]
    assert "催化剂C" in result["catalysts"]
