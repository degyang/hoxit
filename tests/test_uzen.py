from __future__ import annotations

from hoxit.uzen import UzenDataProvider, collect_snapshot


def provider() -> UzenDataProvider:
    return UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试股份", "price": 10.0, "change_pct": 2.5}},
        bars=lambda code, category=4, offset=60, adjust="qfq": [{"date": "2026-06-12", "close": 10.0}],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1, "market_cap": 10000000000}},
        valuation=lambda code: {"forward_pe": 15.0, "peg": 1.2},
        fundamentals=lambda code: {"name": "测试股份", "industry": "软件开发"},
        finance=lambda code: {"roe": 12.3, "net_profit": 100000000},
        f10=lambda code: {"status": "unsupported", "sections": {}, "warnings": ["f10 unavailable"]},
        reports=lambda code: [{"title": "测试研报", "rating": "增持"}],
        news=lambda code: [{"title": "测试新闻"}],
        filings=lambda code, start_date, end_date: [{"title": "年度报告"}],
        hot=lambda date=None, exclude_st=False: [{"code": "600000", "reason": "热点"}],
        concept=lambda code: [{"name": "人工智能"}],
        fund_flow=lambda code, days=20: [{"date": "2026-06-12", "main_net_inflow": 1000}],
        dragon_tiger=lambda code, trade_date: [{"trade_date": trade_date, "net_buy": 2000}],
        lockup=lambda code, trade_date, forward_days=90: [],
        industry=lambda top_n=20: [{"industry": "软件开发", "change_pct": 1.1}],
        margin_trading=lambda code, page_size=30: [],
        block_trade=lambda code, page_size=20: [],
        holder_num=lambda code, page_size=10: [],
        dividend=lambda code, page_size=20: [],
    )


def test_collect_snapshot_assembles_core_sections():
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")

    assert snapshot["code"] == "600000"
    assert snapshot["market"] == "A"
    assert snapshot["mode"] == "analyze-stock"
    assert snapshot["sources"]["quote"]["code"] == "600000"
    assert snapshot["sources"]["bars"] == [{"date": "2026-06-12", "close": 10.0}]
    assert snapshot["sources"]["valuation"]["forward_pe"] == 15.0
    assert snapshot["sources"]["signals"]["concept"] == [{"name": "人工智能"}]
    assert snapshot["data_quality"]["complete"] is False
    assert "f10 unavailable" in snapshot["data_quality"]["warnings"]


def test_collect_snapshot_f10_unsupported_warning():
    """F10 unsupported status should add warnings to data_quality."""
    p = provider()
    snapshot = collect_snapshot("600000", provider=p, today="2026-06-14")
    assert any("f10" in w.lower() for w in snapshot["data_quality"]["warnings"])


def test_collect_snapshot_provider_exception_becomes_warning():
    """When a provider raises, the snapshot should still complete with a warning."""
    def bad_quote(codes):
        raise ConnectionError("network down")

    p = provider()
    # Replace quote provider with one that raises
    broken = UzenDataProvider(
        quote=bad_quote,
        bars=p.bars,
        metrics=p.metrics,
        valuation=p.valuation,
        fundamentals=p.fundamentals,
        finance=p.finance,
        f10=p.f10,
        reports=p.reports,
        news=p.news,
        filings=p.filings,
        hot=p.hot,
        concept=p.concept,
        fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger,
        lockup=p.lockup,
        industry=p.industry,
        margin_trading=p.margin_trading,
        block_trade=p.block_trade,
        holder_num=p.holder_num,
        dividend=p.dividend,
    )
    snapshot = collect_snapshot("600000", provider=broken, today="2026-06-14")
    assert snapshot["sources"]["quote"] == {}
    assert any("network down" in w for w in snapshot["data_quality"]["warnings"])
