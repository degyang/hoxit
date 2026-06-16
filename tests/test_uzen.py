from __future__ import annotations

import json
from typing import Any, Callable

from hoxit.uzen import (
    UzenDataProvider,
    _normalize_concept,
    _normalize_dragon_tiger,
    _normalize_finance,
    analyze_snapshot,
    collect_snapshot,
    render_markdown,
    run_analysis,
)


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
        governance=lambda code: {"actual_controller": "测试集团", "pledge_ratio": 10.0, "status": "computed"},
        business=lambda code: {"revenue_segments": [{"name": "主营", "ratio": 0.8}], "customer_concentration": 15.0, "status": "computed"},
        event=lambda code: {"events": [{"title": "业绩增长", "sentiment": "positive"}], "positive_count": 1, "negative_count": 0, "status": "computed"},
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


def test_collect_snapshot_finance_dataframe_quality_full():
    """Finance providers may return a DataFrame; normalise to dict."""
    class FakeDataFrame:
        """Simulates a pandas DataFrame with .to_dict()."""
        def __bool__(self):
            raise ValueError("The truth value of a DataFrame is ambiguous")

        def to_dict(self):
            return {"roe": 15.0, "net_profit": 1000}

    p = provider()
    dataframe_provider = UzenDataProvider(
        quote=p.quote,
        bars=p.bars,
        metrics=p.metrics,
        valuation=p.valuation,
        fundamentals=p.fundamentals,
        finance=lambda code: FakeDataFrame(),
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
        governance=p.governance,
        business=p.business,
        event=p.event,
    )

    snapshot = collect_snapshot("600000", provider=dataframe_provider, today="2026-06-14")

    # After normalization, finance is a plain dict (from .to_dict())
    assert isinstance(snapshot["sources"]["finance"], dict)
    assert snapshot["sources"]["finance"]["roe"] == 15.0
    assert snapshot["data_quality"]["sources"]["finance"]["quality"] == "full"


def test_analyze_snapshot_adds_summary_panel_and_risk():
    snapshot = collect_snapshot("600000", mode="scan-trap", provider=provider(), today="2026-06-14")
    analyzed = analyze_snapshot(snapshot)

    assert analyzed["analysis"]["summary"]["name"] == "测试股份"
    assert analyzed["analysis"]["summary"]["price"] == 10.0

    panel = analyzed["analysis"]["panel"]
    assert panel["verdict"] in {"bullish", "neutral", "bearish"}
    assert isinstance(panel["score"], int)
    assert isinstance(panel["reasons"], list)
    assert panel["reasons"]
    assert isinstance(panel["signals"], list)
    assert len(panel["signals"]) == 5
    assert isinstance(panel["vote_distribution"], dict)

    market_risk = analyzed["analysis"]["market_risk"]
    assert market_risk["level"] in {"low", "medium", "high"}
    assert market_risk["basis"] == "market_data"
    assert isinstance(market_risk["flags"], list)

    trap_risk = analyzed["analysis"]["trap_risk"]
    assert trap_risk["status"] == "unsupported"
    assert trap_risk["basis"] == "social_evidence"
    assert isinstance(trap_risk["evidence"], list)
    assert isinstance(trap_risk["warnings"], list)


def test_analyze_snapshot_derives_change_pct_from_last_close():
    """mootdx quote may omit change_pct but include price and last_close."""
    p = provider()
    quote_provider = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试股份", "price": 32.1, "last_close": 32.7}},
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
        governance=p.governance,
        business=p.business,
        event=p.event,
    )

    snapshot = analyze_snapshot(collect_snapshot("600000", provider=quote_provider, today="2026-06-14"))

    assert snapshot["analysis"]["summary"]["change_pct"] == -1.83


def test_render_markdown_has_stable_sections():
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert markdown.startswith("# UZEN A股分析：600000")
    assert "本报告仅用于信息整理" in markdown

    expected_sections = [
        "## 核心结论",
        "## 数据完整性",
        "## 行情与估值",
        "## 基本面与财务",
        "## 研报、新闻与公告",
        "## 资金、龙虎榜与题材",
        "## 行业与同业",
        "## 投资者面板",
        "## 市场数据风险检查",
        "## 社交/操纵风险检查",
        "## DCF 估值",
        "## 同业比较（Comps）",
        "## 后续跟踪项",
    ]
    positions = [markdown.index(section) for section in expected_sections]
    assert positions == sorted(positions)


def test_run_analysis_writes_json_and_markdown(tmp_path):
    result = run_analysis("600000", mode="quick-scan", provider=provider(), output_dir=tmp_path, today="2026-06-14")

    assert result["json_path"].endswith("600000-quick-scan.json")
    assert result["markdown_path"].endswith("600000-quick-scan.md")
    payload = json.loads((tmp_path / "600000-quick-scan.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "600000-quick-scan.md").read_text(encoding="utf-8")
    assert payload["mode"] == "quick-scan"
    assert "# UZEN A股分析：600000" in markdown


def test_quick_scan_mode_profile_is_lite(tmp_path):
    result = run_analysis("600000", mode="quick-scan", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    snapshot = result["snapshot"]

    assert snapshot["analysis"]["mode_profile"]["depth"] == "lite"
    assert "quick-scan" in result["markdown_path"]


def test_panel_only_and_lhb_modes_are_labeled(tmp_path):
    panel = run_analysis("600000", mode="panel-only", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    lhb = run_analysis("600000", mode="lhb-analyzer", provider=provider(), output_dir=tmp_path, today="2026-06-14", trade_date="2026-06-14")

    assert panel["snapshot"]["analysis"]["mode_profile"]["primary_section"] == "panel"
    assert lhb["snapshot"]["analysis"]["mode_profile"]["primary_section"] == "dragon_tiger"


def test_unknown_mode_falls_back_to_standard():
    snapshot = collect_snapshot("600000", mode="unknown-mode", provider=provider(), today="2026-06-14")
    analyzed = analyze_snapshot(snapshot)
    assert analyzed["analysis"]["mode_profile"]["depth"] == "standard"
    assert analyzed["analysis"]["mode_profile"]["primary_section"] == "full_report"


# ---------------------------------------------------------------------------
# Call-recording provider for mode execution profile tests
# ---------------------------------------------------------------------------

def _recording_provider() -> tuple[UzenDataProvider, list[str]]:
    """Return a provider that records every call as a key string."""
    calls: list[str] = []

    def _recording_wrapper(key: str, func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            calls.append(key)
            return func(*args, **kwargs)
        return wrapper

    base = provider()
    recorded = UzenDataProvider(
        quote=_recording_wrapper("quote", base.quote),
        bars=_recording_wrapper("bars", base.bars),
        metrics=_recording_wrapper("metrics", base.metrics),
        valuation=_recording_wrapper("valuation", base.valuation),
        fundamentals=_recording_wrapper("fundamentals", base.fundamentals),
        finance=_recording_wrapper("finance", base.finance),
        f10=_recording_wrapper("f10", base.f10),
        reports=_recording_wrapper("reports", base.reports),
        news=_recording_wrapper("news", base.news),
        filings=_recording_wrapper("filings", base.filings),
        hot=_recording_wrapper("hot", base.hot),
        concept=_recording_wrapper("concept", base.concept),
        fund_flow=_recording_wrapper("fund_flow", base.fund_flow),
        dragon_tiger=_recording_wrapper("dragon_tiger", base.dragon_tiger),
        lockup=_recording_wrapper("lockup", base.lockup),
        industry=_recording_wrapper("industry", base.industry),
        margin_trading=_recording_wrapper("margin_trading", base.margin_trading),
        block_trade=_recording_wrapper("block_trade", base.block_trade),
        holder_num=_recording_wrapper("holder_num", base.holder_num),
        dividend=_recording_wrapper("dividend", base.dividend),
        governance=_recording_wrapper("governance", base.governance),
        business=_recording_wrapper("business", base.business),
        event=_recording_wrapper("event", base.event),
    )
    return recorded, calls


def test_quick_scan_skips_heavy_providers():
    """quick-scan must not call reports, news, filings, hot, lockup, industry, etc."""
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="quick-scan", provider=prov, today="2026-06-14")
    expected = {"quote", "metrics", "valuation", "fundamentals", "concept", "fund_flow"}
    assert set(calls) == expected


def test_analyze_stock_calls_full_coverage():
    """analyze-stock must call every provider."""
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="analyze-stock", provider=prov, today="2026-06-14")
    all_keys = {
        "quote", "bars", "metrics", "valuation", "fundamentals", "finance", "f10",
        "reports", "news", "filings",
        "hot", "concept", "fund_flow", "dragon_tiger", "lockup", "industry",
        "margin_trading", "block_trade", "holder_num", "dividend",
        "governance", "business", "event",
    }
    assert set(calls) == all_keys


def test_panel_only_calls_expected_subset():
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="panel-only", provider=prov, today="2026-06-14")
    expected = {"quote", "metrics", "valuation", "fundamentals", "finance"}
    assert set(calls) == expected


def test_scan_trap_calls_expected_subset():
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="scan-trap", provider=prov, today="2026-06-14")
    expected = {"quote", "bars", "concept", "fund_flow", "margin_trading", "block_trade", "holder_num", "dragon_tiger"}
    assert set(calls) == expected


def test_lhb_analyzer_calls_expected_subset():
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="lhb-analyzer", provider=prov, today="2026-06-14", trade_date="2026-06-14")
    expected = {"quote", "concept", "fund_flow", "dragon_tiger", "block_trade", "margin_trading", "lockup"}
    assert set(calls) == expected


def test_dcf_calls_expected_subset():
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="dcf", provider=prov, today="2026-06-14")
    expected = {"quote", "metrics", "valuation", "fundamentals", "finance"}
    assert set(calls) == expected


def test_comps_calls_expected_subset():
    prov, calls = _recording_provider()
    collect_snapshot("600000", mode="comps", provider=prov, today="2026-06-14")
    expected = {"quote", "metrics", "fundamentals", "industry"}
    assert set(calls) == expected


def test_skipped_sources_use_neutral_defaults():
    """Skipped sources must still appear in the snapshot with neutral defaults."""
    prov, _ = _recording_provider()
    snapshot = collect_snapshot("600000", mode="quick-scan", provider=prov, today="2026-06-14")
    sources = snapshot["sources"]
    signals = sources["signals"]

    # quick-scan skips these; they must be present with neutral defaults
    assert sources["bars"] == []
    assert sources["reports"] == []
    assert sources["news"] == []
    assert sources["filings"] == []
    assert sources["f10"] == {}
    assert sources["finance"] == {}
    assert sources["governance"] == {}
    assert sources["business"] == {}
    assert sources["event"] == {}
    assert signals["hot"] == []
    assert signals["dragon_tiger"] == []
    assert signals["lockup"] == []
    assert signals["industry"] == []
    assert signals["margin_trading"] == []
    assert signals["block_trade"] == []
    assert signals["holder_num"] == []
    assert signals["dividend"] == []


# ---------------------------------------------------------------------------
# Source quality record tests
# ---------------------------------------------------------------------------

def test_full_source_quality():
    """Sources with data should have quality 'full'."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]

    assert sq["quote"]["quality"] == "full"
    assert sq["quote"]["label"] == "quote"
    assert sq["quote"]["source"] == "provider.quote"
    assert sq["quote"]["required"] is True
    assert sq["quote"]["warnings"] == []

    assert sq["valuation"]["quality"] == "full"
    assert sq["fundamentals"]["quality"] == "full"
    assert sq["concept"]["quality"] == "full"
    assert sq["fund_flow"]["quality"] == "full"


def test_provider_exception_quality_is_error():
    """When a provider raises, the quality record should be 'error'."""
    def bad_quote(codes):
        raise ConnectionError("network down")

    p = provider()
    broken = UzenDataProvider(
        quote=bad_quote,
        bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
    )
    snapshot = collect_snapshot("600000", provider=broken, today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]

    assert sq["quote"]["quality"] == "error"
    assert "network down" in sq["quote"]["warnings"]
    # The top-level warnings should also contain the error
    assert any("network down" in w for w in snapshot["data_quality"]["warnings"])


def test_skipped_source_quality():
    """Mode-skipped sources should have quality 'skipped'."""
    snapshot = collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]

    # quick-scan skips these
    assert sq["bars"]["quality"] == "skipped"
    assert sq["reports"]["quality"] == "skipped"
    assert sq["news"]["quality"] == "skipped"
    assert sq["filings"]["quality"] == "skipped"
    assert sq["f10"]["quality"] == "skipped"
    assert sq["finance"]["quality"] == "skipped"
    assert sq["hot"]["quality"] == "skipped"
    assert sq["dragon_tiger"]["quality"] == "skipped"
    assert sq["lockup"]["quality"] == "skipped"
    assert sq["industry"]["quality"] == "skipped"
    assert sq["margin_trading"]["quality"] == "skipped"
    assert sq["block_trade"]["quality"] == "skipped"
    assert sq["holder_num"]["quality"] == "skipped"
    assert sq["dividend"]["quality"] == "skipped"
    assert sq["governance"]["quality"] == "skipped"
    assert sq["business"]["quality"] == "skipped"
    assert sq["event"]["quality"] == "skipped"

    # quick-scan uses these
    assert sq["quote"]["quality"] == "full"
    assert sq["metrics"]["quality"] == "full"
    assert sq["valuation"]["quality"] == "full"
    assert sq["fundamentals"]["quality"] == "full"
    assert sq["concept"]["quality"] == "full"
    assert sq["fund_flow"]["quality"] == "full"


# ---------------------------------------------------------------------------
# New A-share data sources tests (PR-DATA-002)
# ---------------------------------------------------------------------------


def test_governance_source_in_snapshot():
    """governance source should appear in analyze-stock snapshot."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    governance = snapshot["sources"]["governance"]
    assert governance["status"] == "computed"
    assert governance["actual_controller"] == "测试集团"
    assert governance["pledge_ratio"] == 10.0


def test_business_source_in_snapshot():
    """business source should appear in analyze-stock snapshot."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    business = snapshot["sources"]["business"]
    assert business["status"] == "computed"
    assert len(business["revenue_segments"]) == 1
    assert business["customer_concentration"] == 15.0


def test_event_source_in_snapshot():
    """event source should appear in analyze-stock snapshot."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    event = snapshot["sources"]["event"]
    assert event["status"] == "computed"
    assert len(event["events"]) == 1
    assert event["positive_count"] == 1
    assert event["negative_count"] == 0


def test_governance_business_event_quality_full():
    """governance, business, event should have quality 'full' when data present."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]
    assert sq["governance"]["quality"] == "full"
    assert sq["business"]["quality"] == "full"
    assert sq["event"]["quality"] == "full"


def test_governance_business_event_skipped_in_quick_scan():
    """governance, business, event should be skipped in quick-scan mode."""
    snapshot = collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]
    assert sq["governance"]["quality"] == "skipped"
    assert sq["business"]["quality"] == "skipped"
    assert sq["event"]["quality"] == "skipped"
    # Neutral defaults
    assert snapshot["sources"]["governance"] == {}
    assert snapshot["sources"]["business"] == {}
    assert snapshot["sources"]["event"] == {}


def test_governance_business_event_error_quality():
    """governance, business, event should have quality 'error' when provider raises."""
    def bad_governance(code):
        raise ConnectionError("governance error")

    def bad_business(code):
        raise ConnectionError("business error")

    def bad_event(code):
        raise ConnectionError("event error")

    p = provider()
    broken = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=bad_governance, business=bad_business, event=bad_event,
    )
    snapshot = collect_snapshot("600000", provider=broken, today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]
    assert sq["governance"]["quality"] == "error"
    assert sq["business"]["quality"] == "error"
    assert sq["event"]["quality"] == "error"
    assert any("governance error" in w for w in sq["governance"]["warnings"])
    assert any("business error" in w for w in sq["business"]["warnings"])
    assert any("event error" in w for w in sq["event"]["warnings"])


def test_governance_business_event_missing_quality():
    """governance, business, event should have quality 'missing' when empty."""
    def empty_governance(code):
        return {}

    def empty_business(code):
        return {}

    def empty_event(code):
        return {}

    p = provider()
    empty_provider = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=empty_governance, business=empty_business, event=empty_event,
    )
    snapshot = collect_snapshot("600000", provider=empty_provider, today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]
    assert sq["governance"]["quality"] == "missing"
    assert sq["business"]["quality"] == "missing"
    assert sq["event"]["quality"] == "missing"


def test_governance_business_event_data_needed_quality():
    """PR-DATA-001-style data_needed dicts should be quality 'missing', not 'full'.

    PR-DATA-001 interfaces return non-empty dicts like:
      {"status": "data_needed", "warnings": ["治理数据不足"]}
    These must not be recorded as quality: "full".
    """
    def data_needed_governance(code):
        return {
            "code": code,
            "actual_controller": "",
            "pledge_ratio": None,
            "shareholder_changes": [],
            "executive_holding": None,
            "status": "data_needed",
            "warnings": ["治理数据不足"],
        }

    def data_needed_business(code):
        return {
            "code": code,
            "revenue_segments": [],
            "customer_concentration": None,
            "supplier_concentration": None,
            "top_customers": [],
            "status": "data_needed",
            "warnings": ["经营数据不足"],
        }

    def data_needed_event(code):
        return {
            "code": code,
            "events": [],
            "catalysts": [],
            "positive_count": 0,
            "negative_count": 0,
            "status": "data_needed",
            "warnings": ["事件数据不足"],
        }

    p = provider()
    data_needed_provider = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=data_needed_governance, business=data_needed_business, event=data_needed_event,
    )
    snapshot = collect_snapshot("600000", provider=data_needed_provider, today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]

    # Quality must not be "full" for data_needed payloads
    assert sq["governance"]["quality"] == "missing"
    assert sq["business"]["quality"] == "missing"
    assert sq["event"]["quality"] == "missing"

    # Source dicts must be preserved in snapshot
    assert snapshot["sources"]["governance"]["status"] == "data_needed"
    assert snapshot["sources"]["business"]["status"] == "data_needed"
    assert snapshot["sources"]["event"]["status"] == "data_needed"

    # Payload warnings must be propagated into quality records
    assert "治理数据不足" in sq["governance"]["warnings"]
    assert "经营数据不足" in sq["business"]["warnings"]
    assert "事件数据不足" in sq["event"]["warnings"]


def test_f10_unsupported_quality_is_partial():
    """F10 unsupported status should produce quality 'partial'."""
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")
    sq = snapshot["data_quality"]["sources"]

    assert sq["f10"]["quality"] == "partial"
    assert sq["f10"]["optional_missing"] == ["f10 sections unavailable"]
    assert any("f10" in w.lower() for w in sq["f10"]["warnings"])


def test_skipped_sources_do_not_affect_complete():
    """Skipped sources alone must not make top-level complete false."""
    snapshot = collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14")

    # quick-scan has many skipped sources but no errors
    # complete should be True because skipped sources don't count
    assert snapshot["data_quality"]["complete"] is True


# ---------------------------------------------------------------------------
# Markdown report contract tests
# ---------------------------------------------------------------------------

def test_markdown_no_raw_dict_repr():
    """Markdown must not contain raw Python dict/list representations."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    # These patterns indicate raw dict/list dumps
    assert "行情：{" not in markdown
    assert "估值：{" not in markdown
    assert "基本面：{" not in markdown
    assert "财务：{" not in markdown
    assert "概念：[{" not in markdown


def test_markdown_quote_section_compact():
    """Quote section should show name, price, change_pct, not raw dict."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "名称：测试股份" in markdown
    assert "最新价：10.00元" in markdown
    assert "涨跌幅：" in markdown


def test_markdown_valuation_section_compact():
    """Valuation section should show PE, PEG, PB, market cap."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "前瞻 PE：" in markdown
    assert "PEG：" in markdown
    assert "PE TTM：" in markdown
    assert "PB：" in markdown
    assert "总市值：" in markdown


def test_markdown_fundamentals_section_compact():
    """Fundamentals section should show industry, ROE, net profit."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "行业：软件开发" in markdown
    assert "ROE：" in markdown
    assert "净利润：" in markdown


def test_markdown_reports_section_compact():
    """Reports section should show count and top titles."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "研报（1 条）：" in markdown
    assert "测试研报" in markdown


def test_markdown_concepts_section_compact():
    """Concepts section should show names, not raw list."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "概念：人工智能" in markdown
    # Should not have raw list representation
    assert "概念：[{" not in markdown


def test_markdown_concepts_accepts_provider_mapping():
    """Live concept providers may return a mapping with concept_tags or boards."""
    p = provider()
    mapping_provider = UzenDataProvider(
        quote=p.quote,
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
        concept=lambda code: {
            "total": 2,
            "concept_tags": ["银行", "破净股"],
            "boards": [{"name": "银行"}, {"name": "破净股"}],
        },
        fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger,
        lockup=p.lockup,
        industry=p.industry,
        margin_trading=p.margin_trading,
        block_trade=p.block_trade,
        holder_num=p.holder_num,
        dividend=p.dividend,
        governance=p.governance,
        business=p.business,
        event=p.event,
    )
    snapshot = collect_snapshot("600000", provider=mapping_provider, today="2026-06-14")

    # After normalization, concept is a list of {name: …} dicts
    concepts = snapshot["sources"]["signals"]["concept"]
    assert isinstance(concepts, list)
    assert len(concepts) == 2
    assert concepts[0]["name"] == "银行"

    analyzed = analyze_snapshot(snapshot)
    markdown = render_markdown(analyzed)

    assert "概念：银行、破净股" in markdown
    assert "concept_tags" not in markdown


def test_markdown_missing_data_renders_chinese():
    """Missing values should render as '缺失' or Chinese text, not {} or []."""
    # Create a provider with minimal data
    minimal = UzenDataProvider(
        quote=lambda codes: {},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {},
        valuation=lambda code: {},
        fundamentals=lambda code: {},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=minimal, today="2026-06-14"))
    markdown = render_markdown(snapshot)

    # Missing values should be rendered as Chinese text
    assert "名称：未知" in markdown
    assert "最新价：缺失" in markdown
    assert "前瞻 PE：缺失" in markdown
    assert "行业：未知行业" in markdown
    assert "暂无数据" in markdown
    assert "暂无概念数据" in markdown


def test_markdown_disclaimer_present():
    """Disclaimer must always be present."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "本报告仅用于信息整理，不构成投资建议" in markdown


# ---------------------------------------------------------------------------
# DCF analysis tests
# ---------------------------------------------------------------------------

def test_dcf_computed_with_sufficient_data():
    """DCF should compute intrinsic value when data is sufficient."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0, "total_shares": 1000000000}},
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0, "net_profit": 500000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    dcf = snapshot["analysis"]["dcf"]

    assert dcf["status"] == "computed"
    assert dcf["intrinsic_value_per_share"] is not None
    assert dcf["intrinsic_value_per_share"] > 0
    assert dcf["market_price"] == 20.0
    assert dcf["margin_of_safety"] is not None
    assert isinstance(dcf["sensitivity"], list)
    assert len(dcf["sensitivity"]) == 9  # 3 discount rates x 3 terminal growths
    assert dcf["inputs"]["net_profit"] == 500000000
    assert dcf["inputs"]["share_count"] == 1000000000


def test_dcf_data_needed_when_missing_inputs():
    """DCF should return data_needed when net_profit or share_count is missing."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0}},  # no total_shares
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0},  # no net_profit
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    dcf = snapshot["analysis"]["dcf"]

    assert dcf["status"] == "data_needed"
    assert dcf["intrinsic_value_per_share"] is None
    assert dcf["margin_of_safety"] is None
    assert dcf["sensitivity"] == []
    assert any("净利润" in w for w in dcf["warnings"])
    assert any("总股本" in w for w in dcf["warnings"])


def test_markdown_dcf_section_computed():
    """Markdown should include DCF section with computed values."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0, "total_shares": 1000000000}},
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0, "net_profit": 500000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## DCF 估值" in markdown
    assert "状态：已计算" in markdown
    assert "内在价值（Intrinsic Value）" in markdown
    assert "安全边际（Margin of Safety）" in markdown
    assert "折现率（Discount Rate）" in markdown
    assert "敏感性分析（Sensitivity）" in markdown


def test_markdown_dcf_section_data_needed():
    """Markdown should show data_needed status when DCF inputs are missing."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## DCF 估值" in markdown
    assert "状态：数据不足（data_needed）" in markdown


def test_dcf_input_quality_computed():
    """DCF input_quality should list available, missing, and proxy_used."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0, "total_shares": 1000000000}},
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0, "net_profit": 500000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    iq = snapshot["analysis"]["dcf"]["input_quality"]

    assert "market_price" in iq["available"]
    assert "net_profit" in iq["available"]
    assert "share_count" in iq["available"]
    assert iq["missing"] == []
    assert "net_profit_as_cash_flow" in iq["proxy_used"]
    assert iq["required"] == ["net_profit", "share_count"]


def test_dcf_input_quality_missing():
    """DCF input_quality should list missing inputs."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0}},  # no total_shares
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0},  # no net_profit
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    iq = snapshot["analysis"]["dcf"]["input_quality"]

    assert "market_price" in iq["available"]
    assert "net_profit" in iq["missing"]
    assert "share_count" in iq["missing"]
    assert "net_profit_as_cash_flow" not in iq["proxy_used"]


def test_markdown_dcf_input_quality():
    """Markdown should show DCF input quality lines."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0, "total_shares": 1000000000}},
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0, "net_profit": 500000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "输入可用：" in markdown
    assert "代理指标：" in markdown


# ---------------------------------------------------------------------------
# Comps analysis tests
# ---------------------------------------------------------------------------

def test_comps_computed_with_peer_data():
    """Comps should compute median PE/PB when peer data is available."""
    def industry_with_peers(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "pe_ttm": 20.0, "pb": 2.5},
            {"name": "同行B", "code": "000002", "pe_ttm": 25.0, "pb": 3.0},
            {"name": "同行C", "code": "000003", "pe_ttm": 30.0, "pb": 3.5},
            {"name": "同行D", "code": "000004", "pe_ttm": 15.0, "pb": 1.8},
            {"name": "同行E", "code": "000005", "pe_ttm": 22.0, "pb": 2.2},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_with_peers,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    comps = snapshot["analysis"]["comps"]

    assert comps["status"] == "computed"
    assert comps["subject"]["pe_ttm"] == 18.0
    assert comps["subject"]["pb"] == 2.1
    assert comps["subject"]["industry"] == "软件开发"
    assert comps["median_pe"] == 22.0  # median of [15, 20, 22, 25, 30]
    assert comps["median_pb"] == 2.5   # median of [1.8, 2.2, 2.5, 3.0, 3.5]
    assert comps["position"] == "below_median"  # 18 < 22 * 0.9 = 19.8
    assert len(comps["rows"]) == 5


def test_comps_data_needed_when_no_peers():
    """Comps should return data_needed when no peer multiples are available."""
    def industry_empty(top_n=20):
        return []

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_empty,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    comps = snapshot["analysis"]["comps"]

    assert comps["status"] == "data_needed"
    assert comps["median_pe"] is None
    assert comps["median_pb"] is None
    assert comps["position"] == "unknown"
    assert any("PE/PB" in w for w in comps["warnings"])


def test_comps_data_needed_when_peers_have_no_multiples():
    """Comps should return data_needed when peers exist but have no PE/PB."""
    def industry_no_multiples(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "change_pct": 1.5},
            {"name": "同行B", "code": "000002", "change_pct": 2.0},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_no_multiples,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    comps = snapshot["analysis"]["comps"]

    assert comps["status"] == "data_needed"
    assert comps["median_pe"] is None
    assert comps["median_pb"] is None
    assert len(comps["rows"]) == 2


def test_markdown_comps_section_computed():
    """Markdown should include comps section with computed values."""
    def industry_with_peers(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "pe_ttm": 20.0, "pb": 2.5},
            {"name": "同行B", "code": "000002", "pe_ttm": 25.0, "pb": 3.0},
            {"name": "同行C", "code": "000003", "pe_ttm": 30.0, "pb": 3.5},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_with_peers,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## 同业比较（Comps）" in markdown
    assert "状态：已计算" in markdown
    assert "样本数：3 家同业" in markdown
    assert "行业中位 PE" in markdown
    assert "行业中位 PB" in markdown
    assert "估值位置" in markdown


def test_markdown_comps_section_data_needed():
    """Markdown should show data_needed status when comps data is missing."""
    def industry_empty(top_n=20):
        return []

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_empty,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## 同业比较（Comps）" in markdown
    assert "状态：数据不足（data_needed）" in markdown


def test_comps_input_quality_computed():
    """Comps input_quality should list peer rows and sample counts."""
    def industry_with_peers(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "pe_ttm": 20.0, "pb": 2.5},
            {"name": "同行B", "code": "000002", "pe_ttm": 25.0, "pb": 3.0},
            {"name": "同行C", "code": "000003", "pe_ttm": 30.0, "pb": 3.5},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_with_peers,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    iq = snapshot["analysis"]["comps"]["input_quality"]

    assert iq["peer_rows"] == 3
    assert iq["pe_samples"] == 3
    assert iq["pb_samples"] == 3
    assert iq["missing"] == []


def test_comps_input_quality_missing_samples():
    """Comps input_quality should list missing PE/PB samples."""
    def industry_no_multiples(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "change_pct": 1.5},
            {"name": "同行B", "code": "000002", "change_pct": 2.0},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_no_multiples,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    iq = snapshot["analysis"]["comps"]["input_quality"]

    assert iq["peer_rows"] == 2
    assert iq["pe_samples"] == 0
    assert iq["pb_samples"] == 0
    assert "peer_pe" in iq["missing"]
    assert "peer_pb" in iq["missing"]


def test_markdown_comps_input_quality():
    """Markdown should show Comps input quality lines."""
    def industry_with_peers(top_n=20):
        return [
            {"name": "同行A", "code": "000001", "pe_ttm": 20.0, "pb": 2.5},
            {"name": "同行B", "code": "000002", "pe_ttm": 25.0, "pb": 3.0},
        ]

    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试", "industry": "软件开发"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=industry_with_peers,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="comps", provider=p, today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="comps")

    assert "PE 样本数：" in markdown
    assert "PB 样本数：" in markdown


# ---------------------------------------------------------------------------
# Risk model split tests
# ---------------------------------------------------------------------------

def test_market_risk_uses_market_data_basis():
    """market_risk should have basis='market_data' and level/flags."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="scan-trap", provider=provider(), today="2026-06-14"))
    market_risk = snapshot["analysis"]["market_risk"]

    assert market_risk["basis"] == "market_data"
    assert market_risk["level"] in {"low", "medium", "high"}
    assert isinstance(market_risk["flags"], list)


def test_market_risk_flags_from_signals():
    """market_risk flags should reflect signal availability."""
    def provider_with_signals():
        return UzenDataProvider(
            quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
            bars=lambda code, **kw: [],
            metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0}},
            valuation=lambda code: {},
            fundamentals=lambda code: {"name": "测试"},
            finance=lambda code: {},
            f10=lambda code: {},
            reports=lambda code: [],
            news=lambda code: [],
            filings=lambda code, s, e: [],
            hot=lambda **kw: [],
            concept=lambda code: [],
            fund_flow=lambda code, **kw: [{"date": "2026-06-12", "main_net_inflow": 1000}],
            dragon_tiger=lambda code, d: [],
            lockup=lambda code, d, **kw: [],
            industry=lambda **kw: [],
            margin_trading=lambda code, **kw: [{"date": "2026-06-12"}],
            block_trade=lambda code, **kw: [{"date": "2026-06-12"}],
            holder_num=lambda code, **kw: [{"date": "2026-06-10"}, {"date": "2026-06-12"}],
            dividend=lambda code, **kw: [],
        )

    snapshot = analyze_snapshot(collect_snapshot("600000", mode="scan-trap", provider=provider_with_signals(), today="2026-06-14"))
    market_risk = snapshot["analysis"]["market_risk"]

    assert market_risk["level"] == "high"  # 3 flags: block_trade, margin_trading, holder_num
    assert len(market_risk["flags"]) == 3
    assert "存在大宗交易记录" in market_risk["flags"]
    assert "存在融资融券变化记录" in market_risk["flags"]
    assert "股东户数存在可跟踪变化" in market_risk["flags"]


def test_trap_risk_unsupported():
    """trap_risk should be unsupported with social_evidence basis."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    trap_risk = snapshot["analysis"]["trap_risk"]

    assert trap_risk["status"] == "unsupported"
    assert trap_risk["basis"] == "social_evidence"
    assert trap_risk["evidence"] == []
    assert len(trap_risk["warnings"]) > 0
    assert any("尚未实现" in w for w in trap_risk["warnings"])


def test_markdown_market_risk_section():
    """Markdown should include market data risk section."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## 市场数据风险检查" in markdown
    assert "数据来源：市场数据（非社交证据）" in markdown
    assert "风险等级：" in markdown


def test_markdown_trap_risk_section():
    """Markdown should include social/trap risk section with unsupported status."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## 社交/操纵风险检查" in markdown
    assert "状态：尚未支持" in markdown
    assert "社交证据采集尚未实现" in markdown


def test_markdown_risk_wording_no_social_implication():
    """Market risk section should not imply social/manipulation evidence."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    # Market risk section should not contain social/manipulation language
    market_risk_start = markdown.index("## 市场数据风险检查")
    trap_risk_start = markdown.index("## 社交/操纵风险检查")
    market_risk_section = markdown[market_risk_start:trap_risk_start]

    assert "杀猪盘" not in market_risk_section
    assert "操纵" not in market_risk_section
    # "非社交证据" is acceptable as it clarifies market data basis
    assert "非社交证据" in market_risk_section


# ---------------------------------------------------------------------------
# Investor panel signal tests
# ---------------------------------------------------------------------------

def test_panel_signals_schema():
    """Panel signals should have all required fields."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    assert "signals" in panel
    assert len(panel["signals"]) == 5

    required_fields = {"investor_id", "name", "group", "signal", "score", "confidence", "reasoning"}
    for sig in panel["signals"]:
        assert required_fields.issubset(sig.keys())
        assert sig["signal"] in {"pass", "fail", "neutral", "data_needed"}
        assert isinstance(sig["score"], int)
        assert isinstance(sig["confidence"], float)
        assert isinstance(sig["reasoning"], list)


def test_panel_vote_distribution():
    """Panel vote_distribution should count signals correctly."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    vote_dist = panel["vote_distribution"]
    assert isinstance(vote_dist, dict)
    assert "pass" in vote_dist
    assert "fail" in vote_dist
    assert "neutral" in vote_dist
    assert "data_needed" in vote_dist

    # Total votes should equal number of signals
    total_votes = sum(vote_dist.values())
    assert total_votes == len(panel["signals"])


def test_panel_investor_ids():
    """Panel should include all 5 baseline investor archetypes."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    investor_ids = {sig["investor_id"] for sig in panel["signals"]}
    expected_ids = {"value", "quality", "growth", "momentum", "hot_money"}
    assert investor_ids == expected_ids


def test_panel_data_needed_when_missing_data():
    """Panel signals should show data_needed when data is missing."""
    minimal = UzenDataProvider(
        quote=lambda codes: {},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {},
        valuation=lambda code: {},
        fundamentals=lambda code: {},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=minimal, today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    # All signals should be data_needed
    for sig in panel["signals"]:
        assert sig["signal"] == "data_needed"
        assert sig["confidence"] == 0.0

    # Vote distribution should show all data_needed
    assert panel["vote_distribution"]["data_needed"] == 5


def test_panel_value_investor_low_pe():
    """Value investor should pass with low PE."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 12.0, "pb": 1.2}},
        valuation=lambda code: {"forward_pe": 10.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    value_sig = next(sig for sig in panel["signals"] if sig["investor_id"] == "value")
    assert value_sig["signal"] == "pass"
    assert value_sig["score"] >= 60
    assert any("估值偏低" in r for r in value_sig["reasoning"])


def test_panel_quality_investor_high_roe():
    """Quality investor should pass with high ROE."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 20.0}},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 20.0, "net_profit": 100000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]

    quality_sig = next(sig for sig in panel["signals"] if sig["investor_id"] == "quality")
    assert quality_sig["signal"] == "pass"
    assert quality_sig["score"] >= 60
    assert any("盈利能力强" in r for r in quality_sig["reasoning"])


def test_markdown_panel_section():
    """Markdown should include panel section with signal distribution."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## 投资者面板" in markdown
    assert "综合结论：" in markdown
    assert "综合分数：" in markdown
    assert "投票分布：" in markdown
    assert "投资者信号：" in markdown


# ---------------------------------------------------------------------------
# Mode-specific Markdown section visibility tests
# ---------------------------------------------------------------------------

def _get_sections(markdown: str) -> set[str]:
    """Extract section headers from markdown."""
    sections = set()
    for line in markdown.split("\n"):
        if line.startswith("## "):
            sections.add(line[3:].strip())
    return sections


def test_analyze_stock_markdown_has_all_sections():
    """analyze-stock mode should render all sections."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="analyze-stock")
    sections = _get_sections(markdown)

    expected = {
        "核心结论", "数据完整性", "行情与估值", "基本面与财务",
        "研报、新闻与公告", "资金、龙虎榜与题材", "行业与同业",
        "投资者面板", "市场数据风险检查", "社交/操纵风险检查",
        "DCF 估值", "同业比较（Comps）", "后续跟踪项",
    }
    assert expected.issubset(sections)


def test_dcf_markdown_omits_unrelated_sections():
    """dcf mode should include DCF but omit Comps and risk sections."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="dcf")
    sections = _get_sections(markdown)

    # Should include
    assert "DCF 估值" in sections
    assert "行情与估值" in sections
    assert "基本面与财务" in sections

    # Should omit
    assert "同业比较（Comps）" not in sections
    assert "市场数据风险检查" not in sections
    assert "社交/操纵风险检查" not in sections
    assert "投资者面板" not in sections
    assert "研报、新闻与公告" not in sections
    assert "资金、龙虎榜与题材" not in sections
    assert "行业与同业" not in sections


def test_comps_markdown_omits_unrelated_sections():
    """comps mode should include Comps but omit DCF and risk sections."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="comps")
    sections = _get_sections(markdown)

    # Should include
    assert "同业比较（Comps）" in sections
    assert "行业与同业" in sections
    assert "行情与估值" in sections
    assert "基本面与财务" in sections

    # Should omit
    assert "DCF 估值" not in sections
    assert "市场数据风险检查" not in sections
    assert "社交/操纵风险检查" not in sections
    assert "投资者面板" not in sections
    assert "研报、新闻与公告" not in sections
    assert "资金、龙虎榜与题材" not in sections


def test_panel_only_markdown_omits_unrelated_sections():
    """panel-only mode should include panel but omit DCF/Comps/risk sections."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="panel-only")
    sections = _get_sections(markdown)

    # Should include
    assert "投资者面板" in sections
    assert "行情与估值" in sections
    assert "基本面与财务" in sections

    # Should omit
    assert "DCF 估值" not in sections
    assert "同业比较（Comps）" not in sections
    assert "市场数据风险检查" not in sections
    assert "社交/操纵风险检查" not in sections
    assert "研报、新闻与公告" not in sections
    assert "资金、龙虎榜与题材" not in sections
    assert "行业与同业" not in sections


def test_scan_trap_markdown_omits_unrelated_sections():
    """scan-trap mode should include risk sections but omit DCF/Comps/panel."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="scan-trap")
    sections = _get_sections(markdown)

    # Should include
    assert "市场数据风险检查" in sections
    assert "社交/操纵风险检查" in sections
    assert "行情与估值" in sections
    assert "基本面与财务" in sections

    # Should omit
    assert "DCF 估值" not in sections
    assert "同业比较（Comps）" not in sections
    assert "投资者面板" not in sections
    assert "研报、新闻与公告" not in sections
    assert "资金、龙虎榜与题材" not in sections
    assert "行业与同业" not in sections


def test_all_modes_include_disclaimer():
    """All modes should include the investment disclaimer."""
    modes = ["analyze-stock", "dcf", "comps", "panel-only", "scan-trap"]
    for mode in modes:
        snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
        markdown = render_markdown(snapshot, mode=mode)
        assert "本报告仅用于信息整理，不构成投资建议" in markdown, f"Disclamer missing in {mode} mode"


def test_unknown_mode_renders_all_sections():
    """Unknown mode should fall back to full analyze-stock behavior."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="unknown-mode")
    sections = _get_sections(markdown)

    # Should include all sections like analyze-stock
    expected = {
        "核心结论", "数据完整性", "行情与估值", "基本面与财务",
        "研报、新闻与公告", "资金、龙虎榜与题材", "行业与同业",
        "投资者面板", "市场数据风险检查", "社交/操纵风险检查",
        "DCF 估值", "同业比较（Comps）", "后续跟踪项",
    }
    assert expected.issubset(sections)


# ---------------------------------------------------------------------------
# Agent analysis envelope tests
# ---------------------------------------------------------------------------

def test_agent_analysis_default_is_not_provided():
    """Default agent_analysis should have status='not_provided'."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["status"] == "not_provided"
    assert agent["basis"] == "agent_qualitative_input"
    assert agent["thesis"] == ""
    assert agent["assumptions"] == []
    assert agent["conflicts"] == []
    assert agent["followups"] == []
    assert agent["warnings"] == []


def test_agent_analysis_provided_envelope():
    """Provided agent_analysis should have status='provided' with content."""
    envelope = {
        "thesis": "看多，基本面改善",
        "assumptions": ["行业复苏", "管理层稳定"],
        "conflicts": ["估值偏高"],
        "followups": ["关注 Q2 财报"],
        "warnings": ["注意风险"],
    }
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["status"] == "provided"
    assert agent["thesis"] == "看多，基本面改善"
    assert agent["assumptions"] == ["行业复苏", "管理层稳定"]
    assert agent["conflicts"] == ["估值偏高"]
    assert agent["followups"] == ["关注 Q2 财报"]
    assert agent["warnings"] == ["注意风险"]


def test_agent_analysis_partial_envelope():
    """Partial agent_analysis should fill missing fields with defaults."""
    envelope = {"thesis": "中性观点"}
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["status"] == "provided"
    assert agent["thesis"] == "中性观点"
    assert agent["assumptions"] == []
    assert agent["conflicts"] == []
    assert agent["followups"] == []
    assert agent["warnings"] == []


def test_agent_analysis_in_json_artifact(tmp_path):
    """JSON artifact should include agent_analysis."""
    envelope = {"thesis": "测试论点"}
    result = run_analysis(
        "600000",
        mode="quick-scan",
        provider=provider(),
        output_dir=tmp_path,
        today="2026-06-14",
        agent_analysis=envelope,
    )
    payload = json.loads((tmp_path / "600000-quick-scan.json").read_text(encoding="utf-8"))

    assert "agent_analysis" in payload["analysis"]
    assert payload["analysis"]["agent_analysis"]["status"] == "provided"
    assert payload["analysis"]["agent_analysis"]["thesis"] == "测试论点"


def test_agent_analysis_markdown_when_provided():
    """Markdown should include agent analysis section when provided."""
    envelope = {
        "thesis": "看多",
        "assumptions": ["假设1"],
        "conflicts": ["矛盾1"],
        "followups": ["跟踪1"],
    }
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    markdown = render_markdown(snapshot)

    assert "## Agent 定性分析" in markdown
    assert "核心论点：看多" in markdown
    assert "假设条件：" in markdown
    assert "假设1" in markdown
    assert "矛盾/风险：" in markdown
    assert "矛盾1" in markdown
    assert "后续验证项：" in markdown
    assert "跟踪1" in markdown


def test_agent_analysis_markdown_when_not_provided():
    """Markdown should NOT include agent analysis section when not provided."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert "## Agent 定性分析" not in markdown


def test_agent_analysis_invalid_type_raises():
    """Non-dict agent_analysis should raise ValueError."""
    from hoxit.uzen import _validate_agent_analysis
    import pytest

    with pytest.raises(ValueError, match="must be a JSON object"):
        _validate_agent_analysis("not a dict")

    with pytest.raises(ValueError, match="must be a JSON object"):
        _validate_agent_analysis([1, 2, 3])


def test_agent_analysis_invalid_field_types_raises():
    """Invalid field types should raise ValueError."""
    from hoxit.uzen import _validate_agent_analysis
    import pytest

    with pytest.raises(ValueError, match="thesis must be a string"):
        _validate_agent_analysis({"thesis": 123})

    with pytest.raises(ValueError, match="assumptions must be a list"):
        _validate_agent_analysis({"assumptions": "not a list"})

    with pytest.raises(ValueError, match="assumptions must be a list"):
        _validate_agent_analysis({"assumptions": [1, 2, 3]})


# ---------------------------------------------------------------------------
# LHB (龙虎榜) summary tests
# ---------------------------------------------------------------------------

def test_lhb_summary_computed_with_data():
    """LHB summary should compute when dragon_tiger data exists."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider(), today="2026-06-14", trade_date="2026-06-14"))
    lhb = snapshot["analysis"]["lhb"]

    assert lhb["status"] == "computed"
    assert lhb["rows"] == 1
    assert lhb["has_dragon_tiger"] is True
    assert lhb["net_buy"] == 2000.0
    assert "龙虎榜净买入为正" in lhb["signals"]
    assert "龙虎榜共 1 条记录" in lhb["signals"]
    assert lhb["warnings"] == []


def test_lhb_summary_data_needed_when_no_rows():
    """LHB summary should return data_needed when no dragon_tiger rows."""
    def provider_no_lhb():
        return UzenDataProvider(
            quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
            bars=lambda code, **kw: [],
            metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0}},
            valuation=lambda code: {},
            fundamentals=lambda code: {"name": "测试"},
            finance=lambda code: {},
            f10=lambda code: {},
            reports=lambda code: [],
            news=lambda code: [],
            filings=lambda code, s, e: [],
            hot=lambda **kw: [],
            concept=lambda code: [],
            fund_flow=lambda code, **kw: [],
            dragon_tiger=lambda code, d: [],  # Empty LHB
            lockup=lambda code, d, **kw: [],
            industry=lambda **kw: [],
        )

    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider_no_lhb(), today="2026-06-14", trade_date="2026-06-14"))
    lhb = snapshot["analysis"]["lhb"]

    assert lhb["status"] == "data_needed"
    assert lhb["rows"] == 0
    assert lhb["has_dragon_tiger"] is False
    assert lhb["net_buy"] is None
    assert lhb["signals"] == []
    assert any("缺失" in w for w in lhb["warnings"])


def test_lhb_summary_net_sell_signal():
    """LHB summary should detect net sell signal."""
    def provider_net_sell():
        return UzenDataProvider(
            quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
            bars=lambda code, **kw: [],
            metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0}},
            valuation=lambda code: {},
            fundamentals=lambda code: {"name": "测试"},
            finance=lambda code: {},
            f10=lambda code: {},
            reports=lambda code: [],
            news=lambda code: [],
            filings=lambda code, s, e: [],
            hot=lambda **kw: [],
            concept=lambda code: [],
            fund_flow=lambda code, **kw: [],
            dragon_tiger=lambda code, d: [{"trade_date": d, "net_buy": -5000}],
            lockup=lambda code, d, **kw: [],
            industry=lambda **kw: [],
        )

    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider_net_sell(), today="2026-06-14", trade_date="2026-06-14"))
    lhb = snapshot["analysis"]["lhb"]

    assert lhb["status"] == "computed"
    assert lhb["net_buy"] == -5000.0
    assert "龙虎榜净卖出" in lhb["signals"]


def test_lhb_in_json_artifact(tmp_path):
    """JSON artifact should include lhb analysis."""
    result = run_analysis("600000", mode="lhb-analyzer", provider=provider(), output_dir=tmp_path, today="2026-06-14", trade_date="2026-06-14")
    payload = json.loads((tmp_path / "600000-lhb-analyzer.json").read_text(encoding="utf-8"))

    assert "lhb" in payload["analysis"]
    assert payload["analysis"]["lhb"]["status"] == "computed"
    assert payload["analysis"]["lhb"]["rows"] == 1


def test_markdown_lhb_section_computed():
    """Markdown should include LHB section with computed values."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider(), today="2026-06-14", trade_date="2026-06-14"))
    markdown = render_markdown(snapshot, mode="lhb-analyzer")

    assert "## 龙虎榜分析" in markdown
    assert "状态：已计算" in markdown
    assert "记录数：1" in markdown
    assert "净买入合计：" in markdown
    assert "龙虎榜净买入为正" in markdown


def test_markdown_lhb_section_data_needed():
    """Markdown should show data_needed when LHB data is missing."""
    def provider_no_lhb():
        return UzenDataProvider(
            quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
            bars=lambda code, **kw: [],
            metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0}},
            valuation=lambda code: {},
            fundamentals=lambda code: {"name": "测试"},
            finance=lambda code: {},
            f10=lambda code: {},
            reports=lambda code: [],
            news=lambda code: [],
            filings=lambda code, s, e: [],
            hot=lambda **kw: [],
            concept=lambda code: [],
            fund_flow=lambda code, **kw: [],
            dragon_tiger=lambda code, d: [],
            lockup=lambda code, d, **kw: [],
            industry=lambda **kw: [],
        )

    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider_no_lhb(), today="2026-06-14", trade_date="2026-06-14"))
    markdown = render_markdown(snapshot, mode="lhb-analyzer")

    assert "## 龙虎榜分析" in markdown
    assert "状态：数据不足（data_needed）" in markdown


def test_lhb_section_included_in_lhb_analyzer_mode():
    """lhb-analyzer mode should include the LHB section."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot, mode="lhb-analyzer")
    sections = _get_sections(markdown)

    assert "龙虎榜分析" in sections


def test_lhb_section_excluded_in_other_modes():
    """Non-lhb-analyzer modes should exclude the LHB section."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))

    for mode in ["analyze-stock", "quick-scan", "dcf", "comps", "panel-only", "scan-trap"]:
        markdown = render_markdown(snapshot, mode=mode)
        sections = _get_sections(markdown)
        assert "龙虎榜分析" not in sections, f"LHB section should not appear in {mode} mode"


# ---------------------------------------------------------------------------
# Dimension layer tests
# ---------------------------------------------------------------------------

def test_dimensions_schema():
    """Dimensions should have all required keys with correct types."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    dimensions = snapshot["analysis"]["dimensions"]

    required_keys = {
        "basic", "market", "valuation", "fundamentals", "capital_flow", "panel", "risk", "lhb", "dcf", "comps",
        # Phase 6 coverage dimensions
        "governance", "business", "events", "policy", "sentiment", "lhb_detail",
        # Deferred UZI dimensions
        "materials", "futures", "moat", "contest",
    }
    assert required_keys.issubset(dimensions.keys())

    for key in required_keys:
        dim = dimensions[key]
        assert "status" in dim, f"{key} missing status"
        assert "quality" in dim, f"{key} missing quality"
        assert "inputs" in dim, f"{key} missing inputs"
        assert "outputs" in dim, f"{key} missing outputs"
        assert "warnings" in dim, f"{key} missing warnings"

        assert dim["status"] in {"computed", "partial", "data_needed", "unsupported"}
        assert dim["quality"] in {"full", "partial", "missing", "skipped", "error"}
        assert isinstance(dim["inputs"], list)
        assert isinstance(dim["outputs"], list)
        assert isinstance(dim["warnings"], list)


def test_dimensions_basic_computed():
    """Basic dimension should be computed when quote and fundamentals are available."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    basic = snapshot["analysis"]["dimensions"]["basic"]

    assert basic["status"] == "computed"
    assert basic["quality"] == "full"
    assert "quote" in basic["inputs"]
    assert "fundamentals" in basic["inputs"]
    assert "summary" in basic["outputs"]


def test_dimensions_market_computed():
    """Market dimension should be computed when quote, bars, metrics are available."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    market = snapshot["analysis"]["dimensions"]["market"]

    assert market["status"] == "computed"
    assert market["quality"] == "full"
    assert "quote" in market["inputs"]
    assert "bars" in market["inputs"]
    assert "metrics" in market["inputs"]


def test_dimensions_panel_computed():
    """Panel dimension should be computed when panel analysis is available."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    panel = snapshot["analysis"]["dimensions"]["panel"]

    assert panel["status"] == "computed"
    assert panel["quality"] == "full"
    assert "panel" in panel["outputs"]


def test_dimensions_risk_computed():
    """Risk dimension should be partial when trap_risk is unsupported."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    risk = snapshot["analysis"]["dimensions"]["risk"]

    assert risk["status"] == "partial"
    assert risk["quality"] == "partial"
    assert "market_risk" in risk["outputs"]
    assert "trap_risk" in risk["outputs"]


def test_dimensions_risk_partial_when_trap_risk_unsupported():
    """Risk dimension should be partial with warning when trap_risk is unsupported."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    risk = snapshot["analysis"]["dimensions"]["risk"]
    trap_risk = snapshot["analysis"]["trap_risk"]

    assert trap_risk["status"] == "unsupported"
    assert risk["status"] == "partial"
    assert risk["quality"] == "partial"
    assert len(risk["warnings"]) > 0
    assert any("尚未实现" in w for w in risk["warnings"])


def test_dimensions_skipped_sources_in_quick_scan():
    """Quick-scan mode should produce skipped quality for heavy sources."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    dims = snapshot["analysis"]["dimensions"]

    # capital_flow includes dragon_tiger which is skipped in quick-scan
    assert dims["capital_flow"]["quality"] in ("skipped", "partial", "missing")
    # lhb depends on dragon_tiger which is skipped
    assert dims["lhb"]["quality"] in ("skipped", "missing")


def test_dimensions_lhb_data_needed():
    """LHB dimension should be data_needed when no dragon_tiger data."""
    def provider_no_lhb():
        return UzenDataProvider(
            quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
            bars=lambda code, **kw: [],
            metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0}},
            valuation=lambda code: {},
            fundamentals=lambda code: {"name": "测试"},
            finance=lambda code: {},
            f10=lambda code: {},
            reports=lambda code: [],
            news=lambda code: [],
            filings=lambda code, s, e: [],
            hot=lambda **kw: [],
            concept=lambda code: [],
            fund_flow=lambda code, **kw: [],
            dragon_tiger=lambda code, d: [],
            lockup=lambda code, d, **kw: [],
            industry=lambda **kw: [],
        )

    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider_no_lhb(), today="2026-06-14", trade_date="2026-06-14"))
    lhb = snapshot["analysis"]["dimensions"]["lhb"]

    assert lhb["status"] == "data_needed"
    assert lhb["quality"] == "missing"


def test_dimensions_lhb_computed():
    """LHB dimension should be computed when dragon_tiger data exists."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="lhb-analyzer", provider=provider(), today="2026-06-14", trade_date="2026-06-14"))
    lhb = snapshot["analysis"]["dimensions"]["lhb"]

    assert lhb["status"] == "computed"
    assert lhb["quality"] == "full"


def test_dimensions_dcf_data_needed():
    """DCF dimension should be data_needed when inputs are missing."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0}},  # no total_shares
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0},  # no net_profit
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    dcf = snapshot["analysis"]["dimensions"]["dcf"]

    assert dcf["status"] == "data_needed"
    assert dcf["quality"] == "missing"


def test_dimensions_computed_with_sufficient_data():
    """DCF dimension should be computed when all inputs are available."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 20.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 15.0, "total_shares": 1000000000}},
        valuation=lambda code: {"forward_pe": 12.0},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {"roe": 15.0, "net_profit": 500000000},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    dcf = snapshot["analysis"]["dimensions"]["dcf"]

    assert dcf["status"] == "computed"
    assert dcf["quality"] == "full"


def test_dimensions_in_json_artifact(tmp_path):
    """JSON artifact should include dimensions."""
    result = run_analysis("600000", mode="quick-scan", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    payload = json.loads((tmp_path / "600000-quick-scan.json").read_text(encoding="utf-8"))

    assert "dimensions" in payload["analysis"]
    dimensions = payload["analysis"]["dimensions"]
    assert "basic" in dimensions
    assert "market" in dimensions
    assert "valuation" in dimensions


def test_dimensions_existing_analysis_unchanged():
    """Dimensions should not affect existing analysis keys."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))

    # Verify existing keys still exist
    assert "summary" in snapshot["analysis"]
    assert "valuation" in snapshot["analysis"]
    assert "panel" in snapshot["analysis"]
    assert "market_risk" in snapshot["analysis"]
    assert "trap_risk" in snapshot["analysis"]
    assert "dcf" in snapshot["analysis"]
    assert "comps" in snapshot["analysis"]
    assert "lhb" in snapshot["analysis"]
    assert "mode_profile" in snapshot["analysis"]
    assert "agent_analysis" in snapshot["analysis"]
    assert "followups" in snapshot["analysis"]

    # Verify dimensions is additional
    assert "dimensions" in snapshot["analysis"]


# ---------------------------------------------------------------------------
# Phase 6 coverage dimension tests
# ---------------------------------------------------------------------------


def test_dimensions_governance_computed():
    """Governance dimension should be computed when governance source is full."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    gov = snapshot["analysis"]["dimensions"]["governance"]

    assert gov["status"] == "computed"
    assert gov["quality"] == "full"
    assert gov["inputs"] == ["governance"]
    assert gov["outputs"] == ["governance"]
    assert gov["warnings"] == []


def test_dimensions_business_computed():
    """Business dimension should be computed when business source is full."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    biz = snapshot["analysis"]["dimensions"]["business"]

    assert biz["status"] == "computed"
    assert biz["quality"] == "full"
    assert biz["inputs"] == ["business"]
    assert biz["outputs"] == ["business"]
    assert biz["warnings"] == []


def test_dimensions_events_computed():
    """Events dimension should be computed when event source is full."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    events = snapshot["analysis"]["dimensions"]["events"]

    assert events["status"] == "computed"
    assert events["quality"] == "full"
    assert events["inputs"] == ["event"]
    assert events["outputs"] == ["event"]
    assert events["warnings"] == []


def test_dimensions_policy_unsupported():
    """Policy dimension should be unsupported with warning."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    policy = snapshot["analysis"]["dimensions"]["policy"]

    assert policy["status"] == "unsupported"
    assert policy["quality"] == "missing"
    assert policy["inputs"] == []
    assert policy["outputs"] == []
    assert len(policy["warnings"]) > 0
    assert any("政策" in w for w in policy["warnings"])


def test_dimensions_sentiment_unsupported():
    """Sentiment dimension should be unsupported with warning."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    sentiment = snapshot["analysis"]["dimensions"]["sentiment"]

    assert sentiment["status"] == "unsupported"
    assert sentiment["quality"] == "missing"
    assert sentiment["inputs"] == []
    assert sentiment["outputs"] == []
    assert len(sentiment["warnings"]) > 0
    assert any("社交" in w for w in sentiment["warnings"])


def test_dimensions_lhb_detail_computed():
    """LHB detail dimension should be computed when dragon_tiger source is full."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    lhb_detail = snapshot["analysis"]["dimensions"]["lhb_detail"]

    assert lhb_detail["status"] == "computed"
    assert lhb_detail["quality"] == "full"
    assert lhb_detail["inputs"] == ["dragon_tiger"]
    assert lhb_detail["outputs"] == ["dragon_tiger"]
    assert lhb_detail["warnings"] == []


def test_dimensions_deferred_uzi_unsupported():
    """Deferred UZI dimensions should be unsupported with explicit warnings."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    dims = snapshot["analysis"]["dimensions"]

    deferred = ["materials", "futures", "moat", "contest"]
    for key in deferred:
        dim = dims[key]
        assert dim["status"] == "unsupported", f"{key} should be unsupported"
        assert dim["quality"] == "missing", f"{key} should be missing quality"
        assert dim["inputs"] == [], f"{key} should have no inputs"
        assert dim["outputs"] == [], f"{key} should have no outputs"
        assert len(dim["warnings"]) > 0, f"{key} should have warnings"


def test_dimensions_governance_skipped_in_quick_scan():
    """Governance dimension should be skipped in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    gov = snapshot["analysis"]["dimensions"]["governance"]

    assert gov["quality"] in ("skipped", "missing")


def test_dimensions_business_skipped_in_quick_scan():
    """Business dimension should be skipped in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    biz = snapshot["analysis"]["dimensions"]["business"]

    assert biz["quality"] in ("skipped", "missing")


def test_dimensions_events_skipped_in_quick_scan():
    """Events dimension should be skipped in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    events = snapshot["analysis"]["dimensions"]["events"]

    assert events["quality"] in ("skipped", "missing")


def test_dimensions_lhb_detail_skipped_in_quick_scan():
    """LHB detail dimension should be skipped in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    lhb_detail = snapshot["analysis"]["dimensions"]["lhb_detail"]

    assert lhb_detail["quality"] in ("skipped", "missing")


def test_dimensions_governance_data_needed():
    """Governance dimension should reflect data_needed status from source."""
    def data_needed_governance(code):
        return {"status": "data_needed", "warnings": ["治理数据不足"]}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=data_needed_governance, business=p.business, event=p.event,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    gov = snapshot["analysis"]["dimensions"]["governance"]

    assert gov["status"] == "partial"
    assert gov["quality"] == "missing"


def test_dimensions_all_phase6_in_json_artifact(tmp_path):
    """JSON artifact should include all Phase 6 dimensions."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    payload = json.loads((tmp_path / "600000-analyze-stock.json").read_text(encoding="utf-8"))
    dims = payload["analysis"]["dimensions"]

    phase6_keys = ["governance", "business", "events", "policy", "sentiment", "lhb_detail",
                   "materials", "futures", "moat", "contest"]
    for key in phase6_keys:
        assert key in dims, f"{key} missing from JSON artifact"


# ── Synthesis layer ──────────────────────────────────────────────────────────


def test_synthesis_schema():
    """Synthesis should have all required fields."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert synth["basis"] == "deterministic_hoxit_analysis"
    assert synth["stance"] in ("bullish", "neutral", "bearish", "data_needed")
    assert synth["confidence"] in ("high", "medium", "low")
    assert isinstance(synth["drivers"], list)
    assert isinstance(synth["risks"], list)
    assert isinstance(synth["conflicts"], list)
    assert isinstance(synth["followups"], list)


def test_synthesis_bullish_when_panel_bullish():
    """Synthesis stance should follow panel verdict."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    panel = snapshot["analysis"]["panel"]
    synth = snapshot["analysis"]["synthesis"]

    # Default provider yields panel verdict — stance should match or be neutral
    if panel["verdict"] == "bullish":
        assert synth["stance"] == "bullish"
    elif panel["verdict"] == "bearish":
        assert synth["stance"] == "bearish"
    else:
        assert synth["stance"] == "neutral"


def test_synthesis_data_needed_when_panel_data_needed():
    """Synthesis should be data_needed when all panel signals are data_needed."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试"}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {},
        valuation=lambda code: {},
        fundamentals=lambda code: {},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert synth["stance"] == "data_needed"
    assert synth["confidence"] == "low"


def test_synthesis_low_confidence_when_data_quality_incomplete():
    """Synthesis confidence should be low when data quality has gaps."""
    # Use minimal provider that produces missing data quality
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {},
        valuation=lambda code: {},
        fundamentals=lambda code: {"name": "测试"},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert synth["confidence"] == "low"


def test_synthesis_includes_risk_flags():
    """Synthesis risks should include each market risk flag."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    market_risk = snapshot["analysis"]["market_risk"]
    synth = snapshot["analysis"]["synthesis"]

    # Each market risk flag should appear in synthesis risks
    flags = market_risk.get("flags", [])
    for flag in flags:
        assert flag in synth["risks"]


def test_synthesis_includes_risk_dimension_warnings():
    """Synthesis risks should include risk dimension warnings (e.g. trap_risk unsupported)."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    risk_dim = snapshot["analysis"]["dimensions"]["risk"]
    synth = snapshot["analysis"]["synthesis"]

    # Risk dimension warnings should appear in synthesis risks
    for warning in risk_dim.get("warnings", []):
        assert warning in synth["risks"]


def test_synthesis_in_json_artifact(tmp_path):
    """JSON artifact should include synthesis."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    payload = json.loads((tmp_path / "600000-analyze-stock.json").read_text(encoding="utf-8"))

    assert "synthesis" in payload["analysis"]
    synth = payload["analysis"]["synthesis"]
    assert synth["basis"] == "deterministic_hoxit_analysis"
    assert "stance" in synth
    assert "confidence" in synth


def test_synthesis_markdown_section():
    """Markdown should include 综合研判 section."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 综合研判" in md
    assert "立场：" in md
    assert "置信度：" in md


def test_synthesis_markdown_data_needed():
    """Markdown synthesis should show data_needed when panel has no data."""
    p = UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试"}},
        bars=lambda code, **kw: [],
        metrics=lambda codes: {},
        valuation=lambda code: {},
        fundamentals=lambda code: {},
        finance=lambda code: {},
        f10=lambda code: {},
        reports=lambda code: [],
        news=lambda code: [],
        filings=lambda code, s, e: [],
        hot=lambda **kw: [],
        concept=lambda code: [],
        fund_flow=lambda code, **kw: [],
        dragon_tiger=lambda code, d: [],
        lockup=lambda code, d, **kw: [],
        industry=lambda **kw: [],
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=p, today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 综合研判" in md
    assert "数据不足" in md


def test_synthesis_markdown_no_raw_dict():
    """Markdown synthesis should not contain raw dict repr."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    # Find the synthesis section
    synth_start = md.find("## 综合研判")
    synth_end = md.find("##", synth_start + 1)
    synth_section = md[synth_start:synth_end] if synth_end > 0 else md[synth_start:]

    assert "{" not in synth_section
    assert "}" not in synth_section


# ── Report self-review ──────────────────────────────────────────────────────


def test_report_review_schema():
    """Report review should have status, checks, and warnings."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    assert review["status"] in ("passed", "warnings")
    assert isinstance(review["checks"], list)
    assert isinstance(review["warnings"], list)
    for check in review["checks"]:
        assert "name" in check
        assert "status" in check
        assert "warnings" in check


def test_report_review_required_sections():
    """Report review should check required analysis sections exist."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review2", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    section_check = next(c for c in review["checks"] if c["name"] == "required_analysis_sections")
    assert section_check["status"] == "passed"
    assert section_check["warnings"] == []


def test_report_review_disclaimer_check():
    """Report review should verify disclaimer is present in Markdown."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review3", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    disclaimer_check = next(c for c in review["checks"] if c["name"] == "disclaimer_present")
    assert disclaimer_check["status"] == "passed"


def test_report_review_no_raw_dict_check():
    """Report review should verify no raw dict repr in Markdown."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review4", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    raw_dict_check = next(c for c in review["checks"] if c["name"] == "no_raw_dict_repr")
    assert raw_dict_check["status"] == "passed"


def test_report_review_mode_section_alignment():
    """Report review should verify mode sections appear in Markdown."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review5", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    alignment_check = next(c for c in review["checks"] if c["name"] == "mode_section_alignment")
    assert alignment_check["status"] == "passed"


def test_report_review_unsupported_feature_wording():
    """Report review should verify unsupported features have correct wording."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir="/tmp/uzen-test-review6", today="2026-06-14")
    review = result["snapshot"]["analysis"]["report_review"]

    unsupported_check = next(c for c in review["checks"] if c["name"] == "unsupported_feature_wording")
    assert unsupported_check["status"] == "passed"


def test_report_review_in_json_artifact(tmp_path):
    """JSON artifact should include report_review."""
    result = run_analysis("600000", mode="analyze-stock", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    payload = json.loads((tmp_path / "600000-analyze-stock.json").read_text(encoding="utf-8"))

    assert "report_review" in payload["analysis"]
    review = payload["analysis"]["report_review"]
    assert review["status"] in ("passed", "warnings")
    assert len(review["checks"]) > 0


def test_report_review_non_blocking():
    """Report review status should never be 'failed'."""
    # Test with various modes to ensure non-blocking
    for mode in ("analyze-stock", "quick-scan", "dcf", "panel-only"):
        result = run_analysis("600000", mode=mode, provider=provider(), output_dir=f"/tmp/uzen-test-nb-{mode}", today="2026-06-14")
        review = result["snapshot"]["analysis"]["report_review"]
        assert review["status"] in ("passed", "warnings"), f"Mode {mode} produced unexpected status: {review['status']}"


# ── Deep review envelope ────────────────────────────────────────────────────


def test_agent_analysis_deep_review_defaults():
    """Default envelope should include deep review fields."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["data_gap_acknowledged"] == {}
    assert agent["dimension_commentary"] == {}
    assert agent["panel_insights"] == ""


def test_agent_analysis_deep_review_backward_compat():
    """Phase 4 envelope without deep review fields should remain valid."""
    envelope = {
        "thesis": "看多",
        "assumptions": ["行业复苏"],
        "conflicts": [],
        "followups": ["关注 Q2"],
        "warnings": [],
    }
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["status"] == "provided"
    assert agent["thesis"] == "看多"
    # New fields get defaults
    assert agent["data_gap_acknowledged"] == {}
    assert agent["dimension_commentary"] == {}
    assert agent["panel_insights"] == ""


def test_agent_analysis_deep_review_provided():
    """Deep review fields should be accepted and stored."""
    envelope = {
        "thesis": "看多",
        "data_gap_acknowledged": {"lhb": "龙虎榜数据缺失"},
        "dimension_commentary": {"risk": "风险维度不完整"},
        "panel_insights": "投资者面板显示多空分歧",
    }
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    agent = snapshot["analysis"]["agent_analysis"]

    assert agent["data_gap_acknowledged"] == {"lhb": "龙虎榜数据缺失"}
    assert agent["dimension_commentary"] == {"risk": "风险维度不完整"}
    assert agent["panel_insights"] == "投资者面板显示多空分歧"


def test_agent_analysis_deep_review_invalid_data_gap():
    """Invalid data_gap_acknowledged type should raise ValueError."""
    import pytest
    envelope = {"data_gap_acknowledged": "not a dict"}
    with pytest.raises(ValueError, match="data_gap_acknowledged must be a dict"):
        analyze_snapshot(
            collect_snapshot("600000", provider=provider(), today="2026-06-14"),
            agent_analysis=envelope,
        )


def test_agent_analysis_deep_review_invalid_dimension_commentary():
    """Invalid dimension_commentary type should raise ValueError."""
    import pytest
    envelope = {"dimension_commentary": {"risk": 123}}
    with pytest.raises(ValueError, match="dimension_commentary must be a dict"):
        analyze_snapshot(
            collect_snapshot("600000", provider=provider(), today="2026-06-14"),
            agent_analysis=envelope,
        )


def test_agent_analysis_deep_review_invalid_panel_insights():
    """Invalid panel_insights type should raise ValueError."""
    import pytest
    envelope = {"panel_insights": 123}
    with pytest.raises(ValueError, match="panel_insights must be a string"):
        analyze_snapshot(
            collect_snapshot("600000", provider=provider(), today="2026-06-14"),
            agent_analysis=envelope,
        )


def test_agent_analysis_deep_review_markdown():
    """Markdown should render deep review fields when provided."""
    envelope = {
        "thesis": "看多",
        "data_gap_acknowledged": {"lhb": "龙虎榜数据缺失"},
        "dimension_commentary": {"risk": "风险维度不完整"},
        "panel_insights": "投资者面板显示多空分歧",
    }
    snapshot = analyze_snapshot(
        collect_snapshot("600000", provider=provider(), today="2026-06-14"),
        agent_analysis=envelope,
    )
    md = render_markdown(snapshot)

    assert "面板洞察：投资者面板显示多空分歧" in md
    assert "数据缺口确认" in md
    assert "lhb：龙虎榜数据缺失" in md
    assert "维度评注" in md
    assert "risk：风险维度不完整" in md


def test_agent_analysis_deep_review_json_artifact(tmp_path):
    """JSON artifact should include deep review fields."""
    envelope = {
        "thesis": "测试",
        "data_gap_acknowledged": {"dcf": "DCF 数据不足"},
        "panel_insights": "面板洞察内容",
    }
    result = run_analysis(
        "600000",
        mode="analyze-stock",
        provider=provider(),
        output_dir=tmp_path,
        today="2026-06-14",
        agent_analysis=envelope,
    )
    payload = json.loads((tmp_path / "600000-analyze-stock.json").read_text(encoding="utf-8"))
    agent = payload["analysis"]["agent_analysis"]

    assert agent["data_gap_acknowledged"] == {"dcf": "DCF 数据不足"}
    assert agent["panel_insights"] == "面板洞察内容"


# ---------------------------------------------------------------------------
# Phase 6: Synthesis and Markdown tests
# ---------------------------------------------------------------------------


def test_synthesis_governance_driver():
    """Synthesis should include governance driver when controller is present."""
    def gov_with_controller(code):
        return {"status": "computed", "actual_controller": "测试集团", "pledge_ratio": 10.0}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=gov_with_controller, business=p.business, event=p.event,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert any("实控人" in d for d in synth["drivers"])


def test_synthesis_governance_high_pledge_risk():
    """Synthesis should include risk when pledge ratio is high."""
    def gov_high_pledge(code):
        return {"status": "computed", "actual_controller": "测试", "pledge_ratio": 60.0}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=gov_high_pledge, business=p.business, event=p.event,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert any("质押" in r for r in synth["risks"])


def test_synthesis_business_driver():
    """Synthesis should include business driver when segments present."""
    def biz_with_segments(code):
        return {"status": "computed", "revenue_segments": [{"name": "白酒", "ratio": 0.8}]}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=p.governance, business=biz_with_segments, event=p.event,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert any("主营" in d for d in synth["drivers"])


def test_synthesis_event_positive_driver():
    """Synthesis should include positive event driver."""
    def event_positive(code):
        return {"status": "computed", "events": [], "positive_count": 3, "negative_count": 0}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=p.governance, business=p.business, event=event_positive,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert any("正面事件" in d for d in synth["drivers"])


def test_synthesis_event_negative_risk():
    """Synthesis should include negative event risk."""
    def event_negative(code):
        return {"status": "computed", "events": [], "positive_count": 0, "negative_count": 5}

    p = provider()
    custom = UzenDataProvider(
        quote=p.quote, bars=p.bars, metrics=p.metrics, valuation=p.valuation,
        fundamentals=p.fundamentals, finance=p.finance, f10=p.f10,
        reports=p.reports, news=p.news, filings=p.filings,
        hot=p.hot, concept=p.concept, fund_flow=p.fund_flow,
        dragon_tiger=p.dragon_tiger, lockup=p.lockup, industry=p.industry,
        margin_trading=p.margin_trading, block_trade=p.block_trade,
        holder_num=p.holder_num, dividend=p.dividend,
        governance=p.governance, business=p.business, event=event_negative,
    )
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=custom, today="2026-06-14"))
    synth = snapshot["analysis"]["synthesis"]

    assert any("负面事件" in r for r in synth["risks"])


def test_markdown_governance_section():
    """Markdown should render governance section with controller info."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 治理与股权结构" in md
    assert "实控人" in md


def test_markdown_business_section():
    """Markdown should render business section with segments."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 经营与产业链" in md
    assert "主营构成" in md


def test_markdown_events_section():
    """Markdown should render events section with counts."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 事件与催化剂" in md
    assert "近期事件" in md


def test_markdown_lhb_detail_section():
    """Markdown should render LHB detail section."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "## 龙虎榜详情" in md
    assert "龙虎榜记录数" in md


def test_markdown_lhb_detail_accepts_provider_mapping():
    """Live LHB providers may return a mapping with records."""
    p = provider()
    mapping_provider = UzenDataProvider(
        quote=p.quote,
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
        dragon_tiger=lambda code, trade_date: {
            "records": [{"trade_date": trade_date, "reason": "日涨幅偏离值达7%"}],
            "seats": {"buy": [], "sell": []},
        },
        lockup=p.lockup,
        industry=p.industry,
        margin_trading=p.margin_trading,
        block_trade=p.block_trade,
        holder_num=p.holder_num,
        dividend=p.dividend,
        governance=p.governance,
        business=p.business,
        event=p.event,
    )
    snapshot = collect_snapshot("600000", provider=mapping_provider, today="2026-06-14")

    # After normalization, dragon_tiger is a list (records extracted)
    dt = snapshot["sources"]["signals"]["dragon_tiger"]
    assert isinstance(dt, list)
    assert len(dt) == 1
    assert dt[0]["reason"] == "日涨幅偏离值达7%"

    analyzed = analyze_snapshot(snapshot)
    md = render_markdown(analyzed)

    assert "龙虎榜记录数：1" in md
    assert "最新上榜原因：日涨幅偏离值达7%" in md


def test_markdown_governance_no_raw_dict():
    """Governance section should not contain raw dict repr."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    gov_start = md.find("## 治理与股权结构")
    gov_end = md.find("##", gov_start + 1)
    gov_section = md[gov_start:gov_end] if gov_end > 0 else md[gov_start:]

    assert "{" not in gov_section
    assert "}" not in gov_section


def test_markdown_business_no_raw_dict():
    """Business section should not contain raw dict repr."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    biz_start = md.find("## 经营与产业链")
    biz_end = md.find("##", biz_start + 1)
    biz_section = md[biz_start:biz_end] if biz_end > 0 else md[biz_start:]

    assert "{" not in biz_section
    assert "}" not in biz_section


def test_markdown_events_no_raw_dict():
    """Events section should not contain raw dict repr."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    evt_start = md.find("## 事件与催化剂")
    evt_end = md.find("##", evt_start + 1)
    evt_section = md[evt_start:evt_end] if evt_end > 0 else md[evt_start:]

    assert "{" not in evt_section
    assert "}" not in evt_section


def test_markdown_governance_skipped_in_quick_scan():
    """Governance section should not appear in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot, mode="quick-scan")

    assert "## 治理与股权结构" not in md


def test_markdown_business_skipped_in_quick_scan():
    """Business section should not appear in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot, mode="quick-scan")

    assert "## 经营与产业链" not in md


def test_markdown_events_skipped_in_quick_scan():
    """Events section should not appear in quick-scan mode."""
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="quick-scan", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot, mode="quick-scan")

    assert "## 事件与催化剂" not in md


def test_markdown_trap_risk_unsupported_wording():
    """Trap risk section should explicitly state unsupported."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    md = render_markdown(snapshot)

    assert "尚未支持" in md or "尚未实现" in md


# ── PR-LIVE-001: Provider normalization helpers ─────────────────────────


def _make_provider(**overrides: Any) -> UzenDataProvider:
    """Build a UzenDataProvider with selective overrides."""
    p = provider()
    fields = {
        "quote": p.quote, "bars": p.bars, "metrics": p.metrics,
        "valuation": p.valuation, "fundamentals": p.fundamentals,
        "finance": p.finance, "f10": p.f10, "reports": p.reports,
        "news": p.news, "filings": p.filings, "hot": p.hot,
        "concept": p.concept, "fund_flow": p.fund_flow,
        "dragon_tiger": p.dragon_tiger, "lockup": p.lockup,
        "industry": p.industry, "margin_trading": p.margin_trading,
        "block_trade": p.block_trade, "holder_num": p.holder_num,
        "dividend": p.dividend, "governance": p.governance,
        "business": p.business, "event": p.event,
    }
    fields.update(overrides)
    return UzenDataProvider(**fields)


# --- _normalize_finance unit tests ---


def test_normalize_finance_passthrough_dict():
    """A plain dict passes through unchanged."""
    data = {"roe": 15.0, "net_profit": 1000}
    assert _normalize_finance(data) is data


def test_normalize_finance_none_returns_empty():
    """None normalises to empty dict."""
    assert _normalize_finance(None) == {}


def test_normalize_finance_to_dict_method():
    """Objects with .to_dict() (pandas DataFrame) are converted."""
    class FakeDataFrame:
        def to_dict(self):
            return {"roe": 20.0, "net_profit": 5000}

    result = _normalize_finance(FakeDataFrame())
    assert isinstance(result, dict)
    assert result["roe"] == 20.0
    assert result["net_profit"] == 5000


def test_normalize_finance_dunder_dict():
    """Objects without .to_dict() fall back to __dict__."""
    class SimpleObj:
        def __init__(self):
            self.roe = 12.0
            self.net_profit = 3000

    result = _normalize_finance(SimpleObj())
    assert isinstance(result, dict)
    assert result["roe"] == 12.0


def test_normalize_finance_dataframe_in_collect_snapshot():
    """DataFrame-like finance does not break collect_snapshot or downstream."""
    class FakeDataFrame:
        def __bool__(self):
            raise ValueError("ambiguous")

        def to_dict(self):
            return {"roe": 18.0, "net_profit": 8000}

    snapshot = collect_snapshot("600000", provider=_make_provider(
        finance=lambda code: FakeDataFrame(),
    ), today="2026-06-14")

    finance = snapshot["sources"]["finance"]
    assert isinstance(finance, dict)
    assert finance["roe"] == 18.0
    assert snapshot["data_quality"]["sources"]["finance"]["quality"] == "full"

    # Downstream analysis should work without errors
    analyzed = analyze_snapshot(snapshot)
    assert analyzed["analysis"]["summary"]["name"] == "测试股份"


# --- _normalize_concept unit tests ---


def test_normalize_concept_passthrough_list():
    """A canonical list passes through unchanged."""
    data = [{"name": "银行"}, {"name": "破净股"}]
    assert _normalize_concept(data) is data


def test_normalize_concept_empty_returns_empty():
    """Empty/None inputs return empty list."""
    assert _normalize_concept(None) == []
    assert _normalize_concept([]) == []
    assert _normalize_concept({}) == []


def test_normalize_concept_concept_tags():
    """Dict with concept_tags extracts tag names."""
    data = {"total": 2, "concept_tags": ["银行", "破净股"]}
    result = _normalize_concept(data)
    assert len(result) == 2
    assert result[0] == {"name": "银行"}
    assert result[1] == {"name": "破净股"}


def test_normalize_concept_boards_only():
    """Dict with boards but no concept_tags extracts board names."""
    data = {"boards": [{"name": "白酒"}, {"name": "消费"}]}
    result = _normalize_concept(data)
    assert len(result) == 2
    assert result[0]["name"] == "白酒"


def test_normalize_concept_tags_take_precedence():
    """When both concept_tags and boards present, concept_tags wins."""
    data = {"concept_tags": ["A"], "boards": [{"name": "B"}]}
    result = _normalize_concept(data)
    assert len(result) == 1
    assert result[0]["name"] == "A"


def test_normalize_concept_in_collect_snapshot():
    """Dict concept provider normalises to list in snapshot."""
    snapshot = collect_snapshot("600000", provider=_make_provider(
        concept=lambda code: {"total": 1, "concept_tags": ["新能源"]},
    ), today="2026-06-14")

    concepts = snapshot["sources"]["signals"]["concept"]
    assert isinstance(concepts, list)
    assert concepts[0]["name"] == "新能源"

    analyzed = analyze_snapshot(snapshot)
    md = render_markdown(analyzed)
    assert "新能源" in md
    assert "concept_tags" not in md


# --- _normalize_dragon_tiger unit tests ---


def test_normalize_dragon_tiger_passthrough_list():
    """A canonical list passes through unchanged."""
    data = [{"reason": "涨幅偏离"}]
    assert _normalize_dragon_tiger(data) is data


def test_normalize_dragon_tiger_empty_returns_empty():
    """Empty/None inputs return empty list."""
    assert _normalize_dragon_tiger(None) == []
    assert _normalize_dragon_tiger([]) == []
    assert _normalize_dragon_tiger({}) == []


def test_normalize_dragon_tiger_records():
    """Dict with records extracts the list."""
    data = {"records": [{"reason": "涨幅偏离"}], "seats": {"buy": [], "sell": []}}
    result = _normalize_dragon_tiger(data)
    assert len(result) == 1
    assert result[0]["reason"] == "涨幅偏离"


def test_normalize_dragon_tiger_empty_records():
    """Dict with empty records returns empty list."""
    data = {"records": [], "seats": {}}
    result = _normalize_dragon_tiger(data)
    assert result == []


def test_normalize_dragon_tiger_in_collect_snapshot():
    """Dict dragon_tiger provider normalises to list in snapshot."""
    snapshot = collect_snapshot("600000", provider=_make_provider(
        dragon_tiger=lambda code, trade_date: {
            "records": [{"trade_date": trade_date, "reason": "日换手率达20%"}],
            "institution": True,
        },
    ), today="2026-06-14")

    dt = snapshot["sources"]["signals"]["dragon_tiger"]
    assert isinstance(dt, list)
    assert len(dt) == 1
    assert dt[0]["reason"] == "日换手率达20%"

    analyzed = analyze_snapshot(snapshot)
    md = render_markdown(analyzed)
    assert "龙虎榜记录数：1" in md
    assert "日换手率达20%" in md


# --- Regression: no raw dict repr in Markdown for normalised shapes ---


def test_markdown_no_raw_dict_repr_for_normalized_shapes():
    """Normalised concept/dragon_tiger must not leak raw dict repr into Markdown."""
    snapshot = collect_snapshot("600000", provider=_make_provider(
        concept=lambda code: {"total": 1, "concept_tags": ["芯片"]},
        dragon_tiger=lambda code, trade_date: {
            "records": [{"trade_date": trade_date, "reason": "涨幅偏离"}],
        },
    ), today="2026-06-14")
    analyzed = analyze_snapshot(snapshot)
    md = render_markdown(analyzed)

    assert "concept_tags" not in md
    assert "{'records'" not in md
    assert "{'name'" not in md


# ── PR-LIVE-002: Derived market metrics ──────────────────────────────────


def test_derived_change_pct_from_price_last_close():
    """change_pct derived from price and last_close when not provided."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 11.0, "last_close": 10.0}},
    ), today="2026-06-14"))
    summary = snapshot["analysis"]["summary"]
    assert summary["change_pct"] == 10.0
    assert summary["change_amount"] == 1.0


def test_derived_change_pct_preserves_direct_field():
    """Direct change_pct from provider is preserved."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 10.0, "change_pct": 3.5}},
    ), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["change_pct"] == 3.5


def test_derived_amplitude_pct():
    """amplitude_pct derived from high, low, last_close."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {
            "code": codes[0], "name": "测试", "price": 10.5,
            "last_close": 10.0, "high": 11.0, "low": 9.5,
        }},
    ), today="2026-06-14"))
    summary = snapshot["analysis"]["summary"]
    assert summary["amplitude_pct"] == 15.0  # (11 - 9.5) / 10 * 100


def test_derived_ma_and_returns():
    """MA5, MA20, return_5d, return_20d from bars."""
    # 25 bars of close prices: 10, 11, 12, ..., 34
    bars = [{"date": f"2026-05-{i+1:02d}", "close": float(10 + i)} for i in range(25)]
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 34.0, "last_close": 33.0}},
        bars=lambda code, **kw: bars,
    ), today="2026-06-14"))
    summary = snapshot["analysis"]["summary"]
    # MA5 of last 5: 30, 31, 32, 33, 34 → 32.0
    assert summary["ma5"] == 32.0
    # MA20 of last 20: 15, 16, ..., 34 → 24.5
    assert summary["ma20"] == 24.5
    # return_5d: (34 / 29 - 1) * 100 ≈ 17.24
    assert summary["return_5d"] is not None
    assert summary["return_5d"] > 15
    # return_20d: (34 / 14 - 1) * 100 ≈ 142.86
    assert summary["return_20d"] is not None
    assert summary["return_20d"] > 100


def test_derived_volatility_and_drawdown():
    """volatility_20d and drawdown_60d from bars."""
    # 65 bars with some variation
    import math
    bars = [{"date": f"2026-{(i//30)+1:02d}-{(i%30)+1:02d}", "close": 100.0 + 5 * math.sin(i * 0.3)} for i in range(65)]
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 100.0, "last_close": 99.0}},
        bars=lambda code, **kw: bars,
    ), today="2026-06-14"))
    summary = snapshot["analysis"]["summary"]
    assert summary["volatility_20d"] is not None
    assert summary["volatility_20d"] > 0
    assert summary["drawdown_60d"] is not None
    assert summary["drawdown_60d"] >= 0


def test_derived_insufficient_bars_warnings():
    """Insufficient bars produce explicit warnings, not silent blanks."""
    bars = [{"date": "2026-06-12", "close": 10.0}]  # only 1 bar
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        bars=lambda code, **kw: bars,
    ), today="2026-06-14"))
    meta = snapshot["analysis"]["summary"]["_meta"]
    assert meta["bars_count"] == 1
    assert any("MA5" in w for w in meta["warnings"])
    assert any("MA20" in w for w in meta["warnings"])
    assert any("波动率" in w for w in meta["warnings"])
    assert any("回撤" in w for w in meta["warnings"])


def test_derived_no_bars_all_none():
    """No bars → all bar-derived fields are None."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        bars=lambda code, **kw: [],
    ), today="2026-06-14"))
    summary = snapshot["analysis"]["summary"]
    assert summary["ma5"] is None
    assert summary["ma20"] is None
    assert summary["return_5d"] is None
    assert summary["return_20d"] is None
    assert summary["volatility_20d"] is None
    assert summary["drawdown_60d"] is None
    assert summary["avg_price"] is None


def test_derived_avg_price_direct_field():
    """Direct quote.avg_price takes priority over computation."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {
            "code": codes[0], "name": "测试", "price": 10.0, "last_close": 9.5,
            "avg_price": 12.34,
        }},
    ), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["avg_price"] == 12.34


def test_derived_avg_price_share_volume():
    """avg_price from amount / vol when vol_unit=股 (shares)."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {
            "code": codes[0], "name": "测试", "price": 10.0, "last_close": 9.5,
            "amount": 15000000.0, "vol": 1500000.0, "vol_unit": "股",
        }},
    ), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["avg_price"] == 10.0


def test_derived_avg_price_lot_volume():
    """avg_price from amount / (vol × 100) when vol_unit=手 (lots)."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {
            "code": codes[0], "name": "测试", "price": 10.0, "last_close": 9.5,
            "amount": 15000000.0, "vol": 15000.0, "vol_unit": "手",
        }},
    ), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["avg_price"] == 10.0


def test_derived_avg_price_ambiguous_unit():
    """avg_price is None when vol_unit is missing — ambiguous unit not guessed."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {
            "code": codes[0], "name": "测试", "price": 10.0, "last_close": 9.5,
            "amount": 15000000.0, "vol": 1500000.0,
        }},
    ), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["avg_price"] is None
    assert any("vol_unit" in w for w in snapshot["analysis"]["summary"]["_meta"]["warnings"])


def test_derived_avg_price_none_when_no_turnover():
    """avg_price is None and warns when quote lacks amount or vol."""
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(), today="2026-06-14"))
    assert snapshot["analysis"]["summary"]["avg_price"] is None
    assert any("成交均价" in w for w in snapshot["analysis"]["summary"]["_meta"]["warnings"])


def test_derived_metrics_in_markdown():
    """Derived metrics appear in Markdown output."""
    bars = [{"date": f"2026-06-{i+1:02d}", "close": float(10 + i)} for i in range(10)]
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=_make_provider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试", "price": 19.0, "last_close": 18.0}},
        bars=lambda code, **kw: bars,
    ), today="2026-06-14"))
    md = render_markdown(snapshot)
    assert "变动" in md  # change_amount
    assert "振幅" in md  # amplitude_pct
    assert "MA5" in md
    assert "MA20" in md
