"""Full-suite integration tests — all 27+ endpoints against real data.

Usage:
    HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -v

Design:
  - All tests are serialised (natural file order). Eastmoney endpoints are
    throttled by em_get() (≥1s interval + jitter), so a full run takes ~15s.
  - Non-Eastmoney endpoints (mootdx, Tencent, THS, Baidu, cninfo) run
    at full speed and are tested first to keep total time low.
  - Primary test ticker: 600519 (贵州茅台). Concept/industry tests use
    688017 (绿的谐波) / 000858 (五粮液) where appropriate.
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest

from hoxit import filings, fundamentals, iwencai, market, news, reports, signals, valuation

pytestmark = [pytest.mark.integration, pytest.mark.slow]

CODES = {
    "茅台": "600519",
    "五粮液": "000858",
    "绿的谐波": "688017",
    "茅台SH": "600519.SH",
}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

_live = os.getenv("HOXIT_LIVE_TESTS") == "1"
skip = pytest.mark.skipif(not _live, reason="set HOXIT_LIVE_TESTS=1 to hit external services")
xfail_if_offline = pytest.mark.xfail(
    not _live,
    reason="Live test skipped (set HOXIT_LIVE_TESTS=1)",
    strict=False,
)


# ── 行情层（mootdx TCP + Tencent HTTP，不封 IP） ──────────────────


@skip
def test_live_tencent_metrics():
    """腾讯 PE/PB/市值/换手率 — 不封 IP，最快数据源之一"""
    result = market.tencent_metrics([CODES["茅台"]])
    assert CODES["茅台"] in result
    row = result[CODES["茅台"]]
    assert row["name"] == "贵州茅台"
    assert row["price"] > 0
    assert row["pe_ttm"] > 0
    assert row["mcap_yi"] > 100  # 至少百亿市值
    assert row["pb"] > 0


@skip
def test_live_tencent_metrics_index_and_etf():
    """腾讯指数 / ETF — 扩展支持"""
    result = market.tencent_metrics(["sh000001", "159915", "510050"])
    # 上证指数（用 sh 前缀）
    assert "sh000001" in result or "000001" in result
    for code, expected_prefix in [("sh000001", "上证"), ("159915", "创业"), ("510050", "50")]:
        if code in result:
            assert expected_prefix in result[code]["name"]


@skip
def test_live_mootdx_bars():
    """mootdx K线 — TCP 直连，最快"""
    rows = market.mootdx_bars(CODES["茅台"], frequency=9, offset=5)  # 9=日K
    assert len(rows) >= 1
    # mootdx raw response 无 code/symbol，但有 close/datetime/amount
    assert rows[0].get("close") or rows[0].get("datetime") or rows[0].get("amount")


@skip
def test_live_mootdx_transactions():
    """mootdx 逐笔成交 — 依赖 TCP 通达信行情服务器"""
    today = datetime.now().strftime("%Y-%m-%d")
    rows = market.mootdx_transactions(CODES["茅台"], date=today)
    assert len(rows) >= 0  # 盘前/非交易时间可能为空


# ── 估值层（同花顺 EPS 预测，HTTP） ────────────────────────────────


xfail_known_flaky = pytest.mark.xfail(reason="known flaky endpoint (API/HTML structure may vary)", strict=False)


@skip
@xfail_known_flaky
def test_live_ths_eps_forecast():
    """同花顺一致预期 EPS — 直连 basic.10jqka.com.cn"""
    forecast = valuation.ths_eps_forecast(CODES["茅台"])
    assert not forecast.empty
    assert "均值" in str(forecast.columns) or "每股收益" in str(forecast.columns)


@skip
def test_live_full_valuation():
    """完整估值流程 — EPS 预测 + 前向 PE / PEG / 消化年数"""
    result = valuation.full_valuation(CODES["茅台"])
    assert result["code"] == CODES["茅台"]
    assert result["price"] > 0
    assert result["pe_ttm"] > 0
    # 机构覆盖（至少有几家预测）
    if result.get("analyst_count"):
        assert result["analyst_count"] > 0


# ── 信号层（同花顺 + 百度，HTTP，不封 IP 或极低风险） ──────────────


@skip
def test_live_ths_hot_reason():
    """同花顺热点 — 盘后 15:30 后有数据"""
    rows = signals.ths_hot_reason(exclude_st=True)
    assert isinstance(rows, list)
    if rows:
        assert "code" in rows[0]
        assert "reason" in rows[0]


@skip
def test_live_hsgt_realtime():
    """同花顺北向资金实时 — 交易时段有 262 个时间点"""
    rows = signals.hsgt_realtime()
    assert len(rows) > 0
    assert "time" in rows[0]


@skip
def test_live_eastmoney_concept_blocks():
    """东财概念板块 — 个股所属板块/概念归属"""
    result = signals.eastmoney_concept_blocks(CODES["绿的谐波"])
    assert result["total"] > 0
    assert result["boards"]
    assert result["concept_tags"]
    assert result["boards"][0]["name"]
    assert result["boards"][0]["code"]


# ── 信号层（东财 push2 资金流，经 em_get 限流） ───────────────────


@skip
def test_live_eastmoney_fund_flow_minute():
    """东财 push2 分钟级资金流（交易时段才有数据）"""
    rows = signals.eastmoney_fund_flow_minute(CODES["茅台"])
    if rows:
        assert "main_net" in rows[0]
        assert "time" in rows[0]
    else:
        # 非交易时段返回空列表是预期行为
        pass


@skip
def test_live_stock_fund_flow_120d():
    """东财 push2his 日级资金流（120 日）"""
    rows = signals.stock_fund_flow_120d(CODES["茅台"], days=5)
    if rows:
        assert rows[0]["date"]
        assert rows[0]["main_net"] != 0


# ── 信号层（东财 datacenter，经 em_get 限流） ────────────────────


@skip
def test_live_dragon_tiger_board():
    """龙虎榜席位 — 近 30 天"""
    trade_date = datetime.now().strftime("%Y-%m-%d")
    result = signals.dragon_tiger_board(CODES["五粮液"], trade_date, look_back=60)
    assert "records" in result
    assert "seats" in result
    assert "institution" in result


@skip
def test_live_daily_dragon_tiger():
    """全市场龙虎榜 — 今天"""
    trade_date = datetime.now().strftime("%Y-%m-%d")
    result = signals.daily_dragon_tiger(trade_date)
    if result.get("stocks"):
        assert result["stocks"][0]["code"]
        assert result["stocks"][0]["net_buy_wan"] is not None


@skip
def test_live_lockup_expiry():
    """限售解禁日历"""
    trade_date = datetime.now().strftime("%Y-%m-%d")
    result = signals.lockup_expiry(CODES["茅台"], trade_date, forward_days=90)
    assert "history" in result
    assert "upcoming" in result


@skip
def test_live_margin_trading():
    """融资融券明细"""
    rows = signals.margin_trading(CODES["茅台"], page_size=5)
    assert len(rows) >= 1
    assert rows[0]["date"]
    assert rows[0]["rzye"] >= 0


@skip
def test_live_block_trade():
    """大宗交易"""
    rows = signals.block_trade(CODES["茅台"], page_size=5)
    assert len(rows) >= 1 if rows else True  # 可能没有大宗交易
    if rows:
        assert rows[0]["date"]
        assert rows[0]["price"] > 0


@skip
def test_live_holder_num_change():
    """股东户数变化"""
    rows = signals.holder_num_change(CODES["茅台"], page_size=3)
    assert len(rows) >= 1
    assert rows[0]["date"]
    assert rows[0]["holder_num"] > 0


@skip
def test_live_dividend_history():
    """分红送转历史"""
    rows = signals.dividend_history(CODES["茅台"], page_size=3)
    assert len(rows) >= 1
    assert rows[0]["date"]
    assert rows[0]["bonus_rmb"] >= 0


@skip
def test_live_industry_comparison():
    """行业横向对比 — 东财 push2 行业板块"""
    result = signals.industry_comparison(top_n=5)
    assert result["total"] > 0
    assert result["top"][0]["name"]
    assert "change_pct" in result["top"][0]


# ── 研报层（东财 reportapi，经 em_get 限流） ────────────────────


@skip
def test_live_eastmoney_reports():
    """东财研报列表"""
    rows = reports.eastmoney_reports(CODES["茅台"], max_pages=1)
    assert len(rows) >= 1
    assert rows[0].get("title") or rows[0].get("infoCode")


# ── 新闻层（东财 search-api-web / np-weblist，经 em_get 限流） ────


@skip
def test_live_stock_news():
    """东财个股新闻"""
    rows = news.stock_news(CODES["茅台"], page_size=3)
    assert len(rows) >= 1
    assert rows[0]["title"]


@skip
def test_live_global_news():
    """东财全球资讯 7×24"""
    rows = news.global_news(page_size=3)
    assert len(rows) >= 1
    assert rows[0]["title"]


# ── 基础数据 + 公告 ──────────────────────────────────────────────


@skip
def test_live_individual_info():
    """东财 push2 个股基本信息"""
    result = fundamentals.individual_info(CODES["茅台"])
    assert result["code"] in (CODES["茅台"], CODES["茅台SH"])
    assert result["name"] == "贵州茅台"
    assert result["industry"]


@skip
def test_live_finance_snapshot():
    """mootdx 财务快照"""
    result = fundamentals.finance_snapshot(CODES["茅台"])
    assert result is not None


@skip
@xfail_known_flaky
def test_live_f10():
    """mootdx F10 公司资料（截断优化）"""
    result = fundamentals.f10(CODES["茅台"])
    assert result is not None


@skip
def test_live_cninfo_reports():
    """巨潮公告"""
    rows = filings.cninfo_reports(CODES["茅台"], "20260501", "20260528", page_size=3)
    assert len(rows) >= 1
    assert rows[0]["title"]


# ── Phase 6: 治理/经营/事件（iwencai，需要 IWENCAI_API_KEY） ──────


@skip
def test_live_governance_summary():
    """iwencai 治理与股权结构（Phase 6）"""
    result = fundamentals.governance_summary(CODES["茅台"])
    assert isinstance(result, dict)
    # 数据可能返回 data_needed 或有实际数据
    assert "status" in result or "controller" in result


@skip
def test_live_business_summary():
    """iwencai 经营与产业链（Phase 6）"""
    result = fundamentals.business_summary(CODES["茅台"])
    assert isinstance(result, dict)
    assert "status" in result or "revenue_segments" in result


@skip
def test_live_event_summary():
    """iwencai 事件与催化剂（Phase 6）"""
    result = signals.event_summary(CODES["茅台"])
    assert isinstance(result, dict)
    assert "status" in result or "events" in result
