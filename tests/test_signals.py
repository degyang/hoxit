from __future__ import annotations

from hoxit import signals

from conftest import JsonResponse


def test_baidu_concept_blocks_accepts_string_result_code():
    payload = {
        "ResultCode": "0",
        "Result": [
            {"type": "行业", "list": [{"name": "机器人", "increase": "1%"}]},
            {"type": "概念", "list": [{"name": "人形机器人", "increase": "2%"}]},
            {"type": "地域", "list": [{"name": "上海", "increase": "0%"}]},
        ],
    }
    result = signals.baidu_concept_blocks("688017", http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert result["industry"][0]["name"] == "机器人"
    assert result["concept_tags"] == ["人形机器人"]
    assert result["region"][0]["name"] == "上海"


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


def test_industry_comparison_uses_eastmoney_push2():
    payload = {"data": {"diff": [{"f14": "机器人", "f3": 2.5, "f12": "BK1234", "f104": 10, "f105": 2, "f140": "样本股", "f136": 5.1}]}}
    rows = signals.industry_comparison(1, http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert rows["top"][0]["name"] == "机器人"
    assert rows["top"][0]["leader"] == "样本股"


def test_compatibility_aliases_exist():
    assert signals.get_concept_blocks is signals.baidu_concept_blocks
    assert signals.get_dragon_tiger_board is signals.dragon_tiger_board
    assert signals.get_lockup_expiry is signals.lockup_expiry
