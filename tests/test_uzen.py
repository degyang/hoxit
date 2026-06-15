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

    risk = analyzed["analysis"]["trap_risk"]
    assert risk["level"] in {"low", "medium", "high"}
    assert isinstance(risk["flags"], list)


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
        "## 风险与杀猪盘检查",
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
