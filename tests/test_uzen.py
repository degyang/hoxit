from __future__ import annotations

import json
from typing import Any, Callable

from hoxit.uzen import UzenDataProvider, analyze_snapshot, collect_snapshot, render_markdown, run_analysis


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

    # quick-scan uses these
    assert sq["quote"]["quality"] == "full"
    assert sq["metrics"]["quality"] == "full"
    assert sq["valuation"]["quality"] == "full"
    assert sq["fundamentals"]["quality"] == "full"
    assert sq["concept"]["quality"] == "full"
    assert sq["fund_flow"]["quality"] == "full"


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

    required_keys = {"basic", "market", "valuation", "fundamentals", "capital_flow", "panel", "risk", "lhb", "dcf", "comps"}
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
