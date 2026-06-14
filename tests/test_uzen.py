from __future__ import annotations

import json

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
