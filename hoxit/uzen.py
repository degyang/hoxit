from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable


def _empty(*args, **kwargs):
    return []


def _empty_mapping(*args, **kwargs):
    return {}


@dataclass(frozen=True)
class UzenDataProvider:
    quote: Callable[[list[str]], dict[str, dict]]
    bars: Callable[..., list[dict]]
    metrics: Callable[[list[str]], dict[str, dict]]
    valuation: Callable[[str], dict]
    fundamentals: Callable[[str], dict]
    finance: Callable[[str], dict]
    f10: Callable[[str], dict]
    reports: Callable[[str], list[dict]]
    news: Callable[[str], list[dict]]
    filings: Callable[[str, str, str], list[dict]]
    hot: Callable[..., list[dict]]
    concept: Callable[[str], list[dict]]
    fund_flow: Callable[..., list[dict]]
    dragon_tiger: Callable[[str, str], list[dict]]
    lockup: Callable[..., list[dict]]
    industry: Callable[..., list[dict]]
    margin_trading: Callable[..., list[dict]] = _empty
    block_trade: Callable[..., list[dict]] = _empty
    holder_num: Callable[..., list[dict]] = _empty
    dividend: Callable[..., list[dict]] = _empty


def default_provider() -> UzenDataProvider:
    from . import filings, fundamentals, market, news, reports, signals, valuation

    return UzenDataProvider(
        quote=market.mootdx_quote,
        bars=market.mootdx_bars,
        metrics=market.tencent_metrics,
        valuation=valuation.full_valuation,
        fundamentals=fundamentals.individual_info,
        finance=fundamentals.finance_snapshot,
        f10=fundamentals.f10,
        reports=reports.eastmoney_reports,
        news=news.stock_news,
        filings=filings.cninfo_reports,
        hot=signals.ths_hot_reason,
        concept=signals.baidu_concept_blocks,
        fund_flow=signals.baidu_fund_flow_history,
        dragon_tiger=signals.dragon_tiger_board,
        lockup=signals.lockup_expiry,
        industry=signals.industry_comparison,
        margin_trading=signals.margin_trading,
        block_trade=signals.block_trade,
        holder_num=signals.holder_num_change,
        dividend=signals.dividend_history,
    )


def _safe_call(label: str, func: Callable, *args, warnings: list[str], default: Any, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        warnings.append(f"{label}: {exc}")
        return default


# Mode execution profiles: which source keys each mode actually needs.
# Unknown modes fall back to the full set (analyze-stock behavior).
_MODE_SOURCES: dict[str, set[str]] = {
    "analyze-stock": {
        "quote", "bars", "metrics", "valuation", "fundamentals", "finance", "f10",
        "reports", "news", "filings",
        "hot", "concept", "fund_flow", "dragon_tiger", "lockup", "industry",
        "margin_trading", "block_trade", "holder_num", "dividend",
    },
    "quick-scan": {
        "quote", "metrics", "valuation", "fundamentals",
        "concept", "fund_flow",
    },
    "panel-only": {
        "quote", "metrics", "valuation", "fundamentals", "finance",
    },
    "scan-trap": {
        "quote", "bars",
        "concept", "fund_flow", "margin_trading", "block_trade", "holder_num", "dragon_tiger",
    },
    "lhb-analyzer": {
        "quote",
        "concept", "fund_flow", "dragon_tiger", "block_trade", "margin_trading", "lockup",
    },
    "dcf": {
        "quote", "metrics", "valuation", "fundamentals", "finance",
    },
    "comps": {
        "quote", "metrics", "fundamentals", "industry",
    },
}


def _sources_for_mode(mode: str) -> set[str]:
    """Return the set of source keys to collect for *mode*.

    Unknown modes fall back to the full analyze-stock set.
    """
    return _MODE_SOURCES.get(mode, _MODE_SOURCES["analyze-stock"])


def _date_window(today: str) -> tuple[str, str]:
    end = datetime.strptime(today, "%Y-%m-%d").date()
    start = end - timedelta(days=365)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def collect_snapshot(
    code: str,
    *,
    mode: str = "analyze-stock",
    provider: UzenDataProvider | None = None,
    today: str | None = None,
    trade_date: str | None = None,
) -> dict[str, Any]:
    provider = provider or default_provider()
    today = today or date.today().strftime("%Y-%m-%d")
    trade_date = trade_date or today
    start_date, end_date = _date_window(today)
    warnings: list[str] = []

    needed = _sources_for_mode(mode)

    # --- helpers ----------------------------------------------------------
    _SENTINEL_LIST: list[dict] = []

    def _map_or_skip(key: str, func: Callable, *args: Any, **kwargs: Any) -> dict:
        if key not in needed:
            return {}
        return _safe_call(key, func, *args, warnings=warnings, default={}, **kwargs)

    def _list_or_skip(key: str, func: Callable, *args: Any, **kwargs: Any) -> list[dict]:
        if key not in needed:
            return _SENTINEL_LIST
        return _safe_call(key, func, *args, warnings=warnings, default=[], **kwargs)

    # --- top-level sources ------------------------------------------------
    quote_map = _map_or_skip("quote", provider.quote, [code])
    quote = quote_map.get(code, {}) if isinstance(quote_map, dict) else {}

    f10 = _map_or_skip("f10", provider.f10, code)
    if isinstance(f10, dict) and f10.get("status") == "unsupported":
        warnings.extend(str(item) for item in f10.get("warnings", []))

    metrics_raw = _map_or_skip("metrics", provider.metrics, [code])
    metrics = metrics_raw.get(code, {}) if isinstance(metrics_raw, dict) else {}

    sources: dict[str, Any] = {
        "quote": quote,
        "bars": _list_or_skip("bars", provider.bars, code, category=4, offset=60, adjust="qfq"),
        "metrics": metrics,
        "valuation": _map_or_skip("valuation", provider.valuation, code),
        "fundamentals": _map_or_skip("fundamentals", provider.fundamentals, code),
        "finance": _map_or_skip("finance", provider.finance, code),
        "f10": f10,
        "reports": _list_or_skip("reports", provider.reports, code),
        "news": _list_or_skip("news", provider.news, code),
        "filings": _list_or_skip("filings", provider.filings, code, start_date, end_date),
    }

    # --- signal sources ---------------------------------------------------
    sources["signals"] = {
        "hot": _list_or_skip("hot", provider.hot, today, exclude_st=True),
        "concept": _list_or_skip("concept", provider.concept, code),
        "fund_flow": _list_or_skip("fund_flow", provider.fund_flow, code, days=20),
        "dragon_tiger": _list_or_skip("dragon_tiger", provider.dragon_tiger, code, trade_date),
        "lockup": _list_or_skip("lockup", provider.lockup, code, trade_date, forward_days=90),
        "industry": _list_or_skip("industry", provider.industry, top_n=20),
        "margin_trading": _list_or_skip("margin_trading", provider.margin_trading, code, page_size=30),
        "block_trade": _list_or_skip("block_trade", provider.block_trade, code, page_size=20),
        "holder_num": _list_or_skip("holder_num", provider.holder_num, code, page_size=10),
        "dividend": _list_or_skip("dividend", provider.dividend, code, page_size=20),
    }

    return {
        "code": code,
        "market": "A",
        "mode": mode,
        "generated_at": f"{today}T00:00:00+08:00",
        "data_quality": {"complete": not warnings, "warnings": warnings},
        "sources": sources,
        "analysis": {},
    }


def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace("%", "").replace(",", ""))
            except ValueError:
                continue
    return None


def _panel_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    valuation = snapshot["sources"].get("valuation", {})
    metrics = snapshot["sources"].get("metrics", {})
    finance = snapshot["sources"].get("finance", {})
    pe = _first_number(valuation.get("forward_pe"), metrics.get("pe_ttm"), metrics.get("pe"))
    roe = _first_number(finance.get("roe"), finance.get("ROE"))
    score = 50
    reasons: list[str] = []
    if pe is not None and pe < 20:
        score += 10
        reasons.append("估值低于 20 倍 PE 区间")
    if pe is not None and pe > 60:
        score -= 15
        reasons.append("估值高于 60 倍 PE 区间")
    if roe is not None and roe >= 10:
        score += 10
        reasons.append("ROE 达到双位数")
    verdict = "bullish" if score >= 65 else "bearish" if score <= 40 else "neutral"
    return {"score": score, "verdict": verdict, "reasons": reasons or ["第一版轻量面板基于估值和财务质量打分"]}


def _trap_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    signals = snapshot["sources"].get("signals", {})
    flags: list[str] = []
    if signals.get("block_trade"):
        flags.append("存在大宗交易记录")
    if signals.get("margin_trading"):
        flags.append("存在融资融券变化记录")
    holder_rows = signals.get("holder_num") or []
    if len(holder_rows) >= 2:
        flags.append("股东户数存在可跟踪变化")
    if not signals.get("fund_flow"):
        flags.append("资金流数据缺失")
    level = "high" if len(flags) >= 3 else "medium" if flags else "low"
    return {"level": level, "flags": flags}


def _mode_profile(mode: str) -> dict[str, str]:
    profiles = {
        "quick-scan": {"depth": "lite", "primary_section": "summary"},
        "dcf": {"depth": "focused", "primary_section": "valuation"},
        "comps": {"depth": "focused", "primary_section": "industry"},
        "panel-only": {"depth": "focused", "primary_section": "panel"},
        "scan-trap": {"depth": "focused", "primary_section": "trap_risk"},
        "lhb-analyzer": {"depth": "focused", "primary_section": "dragon_tiger"},
        "analyze-stock": {"depth": "standard", "primary_section": "full_report"},
    }
    return profiles.get(mode, profiles["analyze-stock"])


def analyze_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    quote = snapshot["sources"].get("quote", {})
    fundamentals = snapshot["sources"].get("fundamentals", {})
    snapshot["analysis"] = {
        "summary": {
            "name": quote.get("name") or fundamentals.get("name") or "",
            "price": quote.get("price"),
            "change_pct": quote.get("change_pct"),
        },
        "valuation": snapshot["sources"].get("valuation", {}),
        "industry": {"rows": snapshot["sources"].get("signals", {}).get("industry", [])},
        "panel": _panel_summary(snapshot),
        "trap_risk": _trap_risk(snapshot),
        "mode_profile": _mode_profile(snapshot.get("mode", "analyze-stock")),
        "followups": [],
    }
    return snapshot


def render_markdown(snapshot: dict[str, Any]) -> str:
    analysis = snapshot.get("analysis") or {}
    summary = analysis.get("summary", {})
    panel = analysis.get("panel", {})
    risk = analysis.get("trap_risk", {})
    sources = snapshot.get("sources", {})
    signals = sources.get("signals", {})
    warnings = snapshot.get("data_quality", {}).get("warnings", [])
    lines = [
        f"# UZEN A股分析：{snapshot['code']}",
        "",
        "## 核心结论",
        f"- 名称：{summary.get('name') or '未知'}",
        f"- 最新价：{summary.get('price') if summary.get('price') is not None else '缺失'}",
        f"- 轻量面板：{panel.get('verdict', 'neutral')}，分数 {panel.get('score', 50)}",
        "",
        "## 数据完整性",
        f"- 完整性：{'完整' if snapshot.get('data_quality', {}).get('complete') else '存在缺口'}",
    ]
    lines.extend(f"- 警告：{warning}" for warning in warnings)
    lines.extend([
        "",
        "## 行情与估值",
        f"- 行情：{sources.get('quote', {})}",
        f"- 估值：{sources.get('valuation', {})}",
        "",
        "## 基本面与财务",
        f"- 基本面：{sources.get('fundamentals', {})}",
        f"- 财务：{sources.get('finance', {})}",
        "",
        "## 研报、新闻与公告",
        f"- 研报数量：{len(sources.get('reports', []))}",
        f"- 新闻数量：{len(sources.get('news', []))}",
        f"- 公告数量：{len(sources.get('filings', []))}",
        "",
        "## 资金、龙虎榜与题材",
        f"- 概念：{signals.get('concept', [])}",
        f"- 资金流记录数：{len(signals.get('fund_flow', []))}",
        f"- 龙虎榜记录数：{len(signals.get('dragon_tiger', []))}",
        "",
        "## 行业与同业",
        f"- 行业样本数：{len(signals.get('industry', []))}",
        "",
        "## 投资者面板",
        f"- 结论：{panel.get('verdict', 'neutral')}",
        f"- 理由：{'；'.join(panel.get('reasons', []))}",
        "",
        "## 风险与杀猪盘检查",
        f"- 风险等级：{risk.get('level', 'low')}",
        f"- 风险标记：{'；'.join(risk.get('flags', [])) if risk.get('flags') else '未触发第一版风险标记'}",
        "",
        "## 后续跟踪项",
        "- 对缺失数据源做人工复核。",
        "",
        "> 本报告仅用于信息整理，不构成投资建议。",
        "",
    ])
    return "\n".join(lines)


def run_analysis(
    code: str,
    *,
    mode: str = "analyze-stock",
    provider: UzenDataProvider | None = None,
    output_dir: str | Path = "uzen-skills/reports",
    today: str | None = None,
    trade_date: str | None = None,
) -> dict[str, Any]:
    snapshot = collect_snapshot(code, mode=mode, provider=provider, today=today, trade_date=trade_date)
    snapshot = analyze_snapshot(snapshot)
    markdown = render_markdown(snapshot)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / f"{code}-{mode}.json"
    markdown_path = target / f"{code}-{mode}.md"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "code": code,
        "mode": mode,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "snapshot": snapshot,
    }
