from __future__ import annotations

from hoxit import signals

from conftest import FakeDataFrame, JsonResponse


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


def test_lockup_expiry_checks_forward_window():
    class FakeAk:
        def __init__(self):
            self.detail_dates = []

        def stock_restricted_release_queue_em(self, symbol):
            return FakeDataFrame()

        def stock_restricted_release_detail_em(self, date):
            self.detail_dates.append(date)
            if date == "20260514":
                return FakeDataFrame([{"股票代码": "688017", "解禁日期": "2026-05-14", "限售股类型": "首发", "解禁数量": 10, "占流通股比例": "1%"}])
            return FakeDataFrame(columns=["股票代码"])

    fake = FakeAk()
    result = signals.lockup_expiry("688017", "2026-05-12", forward_days=2, ak_module=fake)
    assert fake.detail_dates == ["20260512", "20260513", "20260514"]
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


def test_compatibility_aliases_exist():
    assert signals.get_concept_blocks is signals.baidu_concept_blocks
    assert signals.get_dragon_tiger_board is signals.dragon_tiger_board
    assert signals.get_lockup_expiry is signals.lockup_expiry
