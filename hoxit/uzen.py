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


def _safe_call(label: str, func: Callable, *args, warnings: list[str], default: Any, **kwargs) -> tuple[Any, str | None]:
    """Call *func* and return ``(result, error_message)``.

    On success ``error_message`` is ``None``; on exception it contains the
    stringified exception and *default* is returned instead.
    """
    try:
        return func(*args, **kwargs), None
    except Exception as exc:
        warnings.append(f"{label}: {exc}")
        return default, str(exc)


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


# Mode-to-Markdown-section profiles: which sections each mode should render.
# Unknown modes fall back to the full set (analyze-stock behavior).
_MODE_SECTIONS: dict[str, set[str]] = {
    "analyze-stock": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "reports_news_filings", "capital_flow", "industry",
        "panel", "market_risk", "trap_risk", "dcf", "comps", "synthesis", "followups",
    },
    "quick-scan": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "capital_flow", "synthesis", "followups",
    },
    "dcf": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "dcf", "synthesis", "followups",
    },
    "comps": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "industry", "comps", "synthesis", "followups",
    },
    "panel-only": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "panel", "synthesis", "followups",
    },
    "scan-trap": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "market_risk", "trap_risk", "synthesis", "followups",
    },
    "lhb-analyzer": {
        "core", "data_quality", "market_valuation", "fundamentals",
        "capital_flow", "lhb", "synthesis", "followups",
    },
}


def _sections_for_mode(mode: str) -> set[str]:
    """Return the set of Markdown section keys to render for *mode*.

    Unknown modes fall back to the full analyze-stock set.
    """
    return _MODE_SECTIONS.get(mode, _MODE_SECTIONS["analyze-stock"])


def _quality_record(
    label: str,
    *,
    quality: str,
    source: str,
    warnings: list[str],
    required: bool = True,
    optional_missing: list[str] | None = None,
) -> dict[str, Any]:
    """Build a single source quality record."""
    return {
        "label": label,
        "quality": quality,
        "source": source,
        "warnings": list(warnings),
        "required": required,
        "optional_missing": list(optional_missing or []),
    }


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
    quality_records: dict[str, dict[str, Any]] = {}

    needed = _sources_for_mode(mode)

    # --- helpers ----------------------------------------------------------
    _SENTINEL_LIST: list[dict] = []

    def _map_or_skip(key: str, func: Callable, *args: Any, required: bool = True, **kwargs: Any) -> dict:
        if key not in needed:
            quality_records[key] = _quality_record(key, quality="skipped", source=f"provider.{key}", warnings=[], required=required)
            return {}
        result, error = _safe_call(key, func, *args, warnings=warnings, default={}, **kwargs)
        if error:
            quality_records[key] = _quality_record(key, quality="error", source=f"provider.{key}", warnings=[error], required=required)
        elif not result:
            quality_records[key] = _quality_record(key, quality="missing", source=f"provider.{key}", warnings=[], required=required)
        else:
            quality_records[key] = _quality_record(key, quality="full", source=f"provider.{key}", warnings=[], required=required)
        return result

    def _list_or_skip(key: str, func: Callable, *args: Any, required: bool = True, **kwargs: Any) -> list[dict]:
        if key not in needed:
            quality_records[key] = _quality_record(key, quality="skipped", source=f"provider.{key}", warnings=[], required=required)
            return _SENTINEL_LIST
        result, error = _safe_call(key, func, *args, warnings=warnings, default=[], **kwargs)
        if error:
            quality_records[key] = _quality_record(key, quality="error", source=f"provider.{key}", warnings=[error], required=required)
        elif not result:
            quality_records[key] = _quality_record(key, quality="missing", source=f"provider.{key}", warnings=[], required=required)
        else:
            quality_records[key] = _quality_record(key, quality="full", source=f"provider.{key}", warnings=[], required=required)
        return result

    # --- top-level sources ------------------------------------------------
    quote_map = _map_or_skip("quote", provider.quote, [code])
    quote = quote_map.get(code, {}) if isinstance(quote_map, dict) else {}

    if "f10" not in needed:
        quality_records["f10"] = _quality_record("f10", quality="skipped", source="provider.f10", warnings=[], required=True)
        f10: dict[str, Any] = {}
    else:
        f10_raw, f10_error = _safe_call("f10", provider.f10, code, warnings=warnings, default={})
        f10 = f10_raw
        if f10_error:
            quality_records["f10"] = _quality_record("f10", quality="error", source="provider.f10", warnings=[f10_error], required=True)
        elif isinstance(f10, dict) and f10.get("status") == "unsupported":
            f10_warnings = [str(item) for item in f10.get("warnings", [])]
            warnings.extend(f10_warnings)
            quality_records["f10"] = _quality_record("f10", quality="partial", source="provider.f10", warnings=f10_warnings, required=True, optional_missing=["f10 sections unavailable"])
        elif not f10:
            quality_records["f10"] = _quality_record("f10", quality="missing", source="provider.f10", warnings=[], required=True)
        else:
            quality_records["f10"] = _quality_record("f10", quality="full", source="provider.f10", warnings=[], required=True)

    if "metrics" not in needed:
        quality_records["metrics"] = _quality_record("metrics", quality="skipped", source="provider.metrics", warnings=[], required=True)
        metrics: dict[str, Any] = {}
    else:
        metrics_raw, metrics_error = _safe_call("metrics", provider.metrics, [code], warnings=warnings, default={})
        if metrics_error:
            quality_records["metrics"] = _quality_record("metrics", quality="error", source="provider.metrics", warnings=[metrics_error], required=True)
            metrics = {}
        elif not metrics_raw or not metrics_raw.get(code):
            quality_records["metrics"] = _quality_record("metrics", quality="missing", source="provider.metrics", warnings=[], required=True)
            metrics = {}
        else:
            quality_records["metrics"] = _quality_record("metrics", quality="full", source="provider.metrics", warnings=[], required=True)
            metrics = metrics_raw.get(code, {})

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

    # --- data quality -----------------------------------------------------
    # Skipped sources must not make top-level complete false.
    # Only non-skipped warnings affect completeness.
    non_skipped_warnings = [
        w for key, rec in quality_records.items()
        if rec["quality"] != "skipped"
        for w in rec["warnings"]
    ]

    return {
        "code": code,
        "market": "A",
        "mode": mode,
        "generated_at": f"{today}T00:00:00+08:00",
        "data_quality": {
            "complete": not non_skipped_warnings,
            "warnings": warnings,
            "sources": quality_records,
        },
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


def _value_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Value investor: low PE, reasonable PB, stable earnings."""
    valuation = snapshot["sources"].get("valuation", {})
    metrics = snapshot["sources"].get("metrics", {})
    finance = snapshot["sources"].get("finance", {})

    pe = _first_number(valuation.get("forward_pe"), metrics.get("pe_ttm"), metrics.get("pe"))
    pb = _first_number(metrics.get("pb"))
    roe = _first_number(finance.get("roe"), finance.get("ROE"))

    reasoning: list[str] = []
    score = 50
    data_available = False

    if pe is not None:
        data_available = True
        if pe < 15:
            score += 20
            reasoning.append(f"PE {pe:.1f} 倍，估值偏低")
        elif pe < 25:
            score += 10
            reasoning.append(f"PE {pe:.1f} 倍，估值合理")
        elif pe > 50:
            score -= 15
            reasoning.append(f"PE {pe:.1f} 倍，估值偏高")

    if pb is not None:
        data_available = True
        if pb < 1.5:
            score += 10
            reasoning.append(f"PB {pb:.1f} 倍，资产折价")
        elif pb > 5:
            score -= 10
            reasoning.append(f"PB {pb:.1f} 倍，资产溢价")

    if not data_available:
        return {
            "investor_id": "value",
            "name": "价值投资者",
            "group": "fundamental",
            "signal": "data_needed",
            "score": 50,
            "confidence": 0.0,
            "reasoning": ["估值数据不足"],
        }

    signal = "pass" if score >= 60 else "fail" if score <= 40 else "neutral"
    confidence = min(1.0, max(0.0, (score - 30) / 40))
    return {
        "investor_id": "value",
        "name": "价值投资者",
        "group": "fundamental",
        "signal": signal,
        "score": score,
        "confidence": round(confidence, 2),
        "reasoning": reasoning or ["估值处于中性区间"],
    }


def _quality_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Quality investor: high ROE, stable profitability."""
    finance = snapshot["sources"].get("finance", {})
    metrics = snapshot["sources"].get("metrics", {})

    roe = _first_number(finance.get("roe"), finance.get("ROE"))
    net_profit = _first_number(finance.get("net_profit"))
    pe = _first_number(metrics.get("pe_ttm"), metrics.get("pe"))

    reasoning: list[str] = []
    score = 50
    data_available = False

    if roe is not None:
        data_available = True
        if roe >= 15:
            score += 20
            reasoning.append(f"ROE {roe:.1f}%，盈利能力强")
        elif roe >= 10:
            score += 10
            reasoning.append(f"ROE {roe:.1f}%，盈利能力良好")
        elif roe < 5:
            score -= 15
            reasoning.append(f"ROE {roe:.1f}%，盈利能力弱")

    if net_profit is not None:
        data_available = True
        if net_profit > 0:
            score += 5
            reasoning.append("净利润为正")
        else:
            score -= 10
            reasoning.append("净利润为负")

    if not data_available:
        return {
            "investor_id": "quality",
            "name": "质量投资者",
            "group": "fundamental",
            "signal": "data_needed",
            "score": 50,
            "confidence": 0.0,
            "reasoning": ["财务数据不足"],
        }

    signal = "pass" if score >= 60 else "fail" if score <= 40 else "neutral"
    confidence = min(1.0, max(0.0, (score - 30) / 40))
    return {
        "investor_id": "quality",
        "name": "质量投资者",
        "group": "fundamental",
        "signal": signal,
        "score": score,
        "confidence": round(confidence, 2),
        "reasoning": reasoning or ["财务质量处于中性区间"],
    }


def _growth_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Growth investor: earnings growth, revenue growth."""
    valuation = snapshot["sources"].get("valuation", {})
    metrics = snapshot["sources"].get("metrics", {})

    growth = _first_number(
        valuation.get("earnings_growth"),
        metrics.get("earnings_growth"),
        metrics.get("profit_growth"),
    )
    pe = _first_number(valuation.get("forward_pe"), metrics.get("pe_ttm"), metrics.get("pe"))

    reasoning: list[str] = []
    score = 50
    data_available = False

    if growth is not None:
        data_available = True
        if growth > 30:
            score += 20
            reasoning.append(f"盈利增长 {growth:.1f}%，高增长")
        elif growth > 15:
            score += 10
            reasoning.append(f"盈利增长 {growth:.1f}%，稳健增长")
        elif growth < 0:
            score -= 15
            reasoning.append(f"盈利增长 {growth:.1f}%，增长为负")

    if pe is not None and growth is not None and growth > 0:
        peg = pe / growth
        if peg < 1:
            score += 10
            reasoning.append(f"PEG {peg:.2f}，增长估值匹配")
        elif peg > 2:
            score -= 10
            reasoning.append(f"PEG {peg:.2f}，估值偏高")

    if not data_available:
        return {
            "investor_id": "growth",
            "name": "成长投资者",
            "group": "fundamental",
            "signal": "data_needed",
            "score": 50,
            "confidence": 0.0,
            "reasoning": ["增长数据不足"],
        }

    signal = "pass" if score >= 60 else "fail" if score <= 40 else "neutral"
    confidence = min(1.0, max(0.0, (score - 30) / 40))
    return {
        "investor_id": "growth",
        "name": "成长投资者",
        "group": "fundamental",
        "signal": signal,
        "score": score,
        "confidence": round(confidence, 2),
        "reasoning": reasoning or ["增长处于中性区间"],
    }


def _momentum_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Momentum investor: price trend, volume, fund flow."""
    quote = snapshot["sources"].get("quote", {})
    signals = snapshot["sources"].get("signals", {})

    change_pct = _first_number(quote.get("change_pct"))
    fund_flow = signals.get("fund_flow", [])
    dragon_tiger = signals.get("dragon_tiger", [])

    reasoning: list[str] = []
    score = 50
    data_available = False

    if change_pct is not None:
        data_available = True
        if change_pct > 3:
            score += 15
            reasoning.append(f"涨幅 {change_pct:.2f}%，强势")
        elif change_pct < -3:
            score -= 15
            reasoning.append(f"跌幅 {change_pct:.2f}%，弱势")

    if fund_flow:
        data_available = True
        recent = fund_flow[-1] if fund_flow else {}
        net_inflow = _first_number(recent.get("main_net_inflow"))
        if net_inflow is not None:
            if net_inflow > 0:
                score += 10
                reasoning.append("主力资金净流入")
            else:
                score -= 10
                reasoning.append("主力资金净流出")

    if dragon_tiger:
        data_available = True
        score += 5
        reasoning.append("存在龙虎榜记录")

    if not data_available:
        return {
            "investor_id": "momentum",
            "name": "动量投资者",
            "group": "technical",
            "signal": "data_needed",
            "score": 50,
            "confidence": 0.0,
            "reasoning": ["动量数据不足"],
        }

    signal = "pass" if score >= 60 else "fail" if score <= 40 else "neutral"
    confidence = min(1.0, max(0.0, (score - 30) / 40))
    return {
        "investor_id": "momentum",
        "name": "动量投资者",
        "group": "technical",
        "signal": signal,
        "score": score,
        "confidence": round(confidence, 2),
        "reasoning": reasoning or ["动量处于中性区间"],
    }


def _hot_money_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Hot-money suitability: block trade, margin trading, holder changes."""
    signals = snapshot["sources"].get("signals", {})

    block_trade = signals.get("block_trade", [])
    margin_trading = signals.get("margin_trading", [])
    holder_num = signals.get("holder_num", [])
    dragon_tiger = signals.get("dragon_tiger", [])

    reasoning: list[str] = []
    score = 50
    data_available = False

    if block_trade:
        data_available = True
        score += 10
        reasoning.append("存在大宗交易记录")

    if margin_trading:
        data_available = True
        score += 10
        reasoning.append("存在融资融券记录")

    if holder_num and len(holder_num) >= 2:
        data_available = True
        score += 10
        reasoning.append("股东户数存在变化")

    if dragon_tiger:
        data_available = True
        score += 15
        reasoning.append("存在龙虎榜记录")

    if not data_available:
        return {
            "investor_id": "hot_money",
            "name": "游资 suitability",
            "group": "technical",
            "signal": "data_needed",
            "score": 50,
            "confidence": 0.0,
            "reasoning": ["游资数据不足"],
        }

    signal = "pass" if score >= 60 else "fail" if score <= 40 else "neutral"
    confidence = min(1.0, max(0.0, (score - 30) / 40))
    return {
        "investor_id": "hot_money",
        "name": "游资 suitability",
        "group": "technical",
        "signal": signal,
        "score": score,
        "confidence": round(confidence, 2),
        "reasoning": reasoning or ["游资指标处于中性区间"],
    }


def _panel_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute investor panel with signals and vote distribution."""
    # Run all investor archetypes
    signals = [
        _value_investor(snapshot),
        _quality_investor(snapshot),
        _growth_investor(snapshot),
        _momentum_investor(snapshot),
        _hot_money_investor(snapshot),
    ]

    # Compute vote distribution
    vote_distribution: dict[str, int] = {"pass": 0, "fail": 0, "neutral": 0, "data_needed": 0}
    for sig in signals:
        vote_distribution[sig["signal"]] = vote_distribution.get(sig["signal"], 0) + 1

    # Compute aggregate score (weighted average of non-data_needed signals)
    valid_scores = [s["score"] for s in signals if s["signal"] != "data_needed"]
    if valid_scores:
        score = round(sum(valid_scores) / len(valid_scores))
    else:
        score = 50

    # Compute verdict
    verdict = "bullish" if score >= 65 else "bearish" if score <= 40 else "neutral"

    # Compute reasons from top signals
    reasons: list[str] = []
    for sig in signals:
        if sig["signal"] == "pass" and sig["reasoning"]:
            reasons.append(f"{sig['name']}：{sig['reasoning'][0]}")
        elif sig["signal"] == "fail" and sig["reasoning"]:
            reasons.append(f"{sig['name']}：{sig['reasoning'][0]}")

    return {
        "score": score,
        "verdict": verdict,
        "reasons": reasons or ["面板基于估值、财务、动量等多维度打分"],
        "signals": signals,
        "vote_distribution": vote_distribution,
    }


def _market_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute market-data-based risk flags.

    These flags are derived from observable market data (block trades, margin
    trading, holder count changes, fund flow availability). They do NOT imply
    social manipulation or trap evidence.
    """
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
    return {"level": level, "basis": "market_data", "flags": flags}


def _trap_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute social/manipulation trap risk status.

    Currently unsupported — no social media scraping or evidence collection
    is implemented. Returns status="unsupported" with empty evidence.
    """
    return {
        "status": "unsupported",
        "basis": "social_evidence",
        "evidence": [],
        "warnings": ["社交/操纵证据采集尚未实现"],
    }


def _dcf_analysis(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute a light DCF analysis from snapshot data.

    Returns a dict with status, inputs, assumptions, intrinsic value, margin of safety,
    sensitivity table, and warnings. When data is insufficient, returns status="data_needed".
    """
    sources = snapshot.get("sources", {})
    quote = sources.get("quote", {})
    valuation = sources.get("valuation", {})
    metrics = sources.get("metrics", {})
    finance = sources.get("finance", {})

    warnings: list[str] = []
    inputs: dict[str, Any] = {}
    assumptions: dict[str, Any] = {}

    # --- Extract market price ---
    market_price = _first_number(quote.get("price"))
    if market_price is None:
        warnings.append("市场价格缺失")
    inputs["market_price"] = market_price

    # --- Extract net profit as cash flow proxy ---
    net_profit = _first_number(finance.get("net_profit"))
    if net_profit is None:
        warnings.append("净利润缺失（用作现金流代理）")
    inputs["net_profit"] = net_profit

    # --- Extract share count ---
    share_count = _first_number(
        metrics.get("total_shares"),
        metrics.get("share_count"),
        finance.get("total_shares"),
    )
    if share_count is None:
        warnings.append("总股本缺失")
    inputs["share_count"] = share_count

    # --- Extract growth rate from valuation or metrics ---
    growth_rate = _first_number(
        valuation.get("earnings_growth"),
        metrics.get("earnings_growth"),
        metrics.get("profit_growth"),
    )
    if growth_rate is None:
        # Conservative default
        growth_rate = 5.0
        assumptions["growth_rate"] = {"value": growth_rate, "source": "保守默认值 5%"}
    else:
        assumptions["growth_rate"] = {"value": growth_rate, "source": "hoxit 数据"}
    inputs["growth_rate"] = growth_rate

    # --- Assumptions ---
    discount_rate = 10.0
    terminal_growth = 3.0
    explicit_years = 5
    assumptions["discount_rate"] = {"value": discount_rate, "source": "默认 10%"}
    assumptions["terminal_growth"] = {"value": terminal_growth, "source": "默认 3%"}
    assumptions["explicit_years"] = {"value": explicit_years, "source": "默认 5 年"}

    # --- Build input quality ---
    required = ["net_profit", "share_count"]
    available = []
    missing = []
    proxy_used = []

    if market_price is not None:
        available.append("market_price")
    else:
        missing.append("market_price")

    if net_profit is not None:
        available.append("net_profit")
        proxy_used.append("net_profit_as_cash_flow")
    else:
        missing.append("net_profit")

    if share_count is not None and share_count > 0:
        available.append("share_count")
    else:
        missing.append("share_count")

    input_quality = {
        "required": required,
        "available": available,
        "missing": missing,
        "proxy_used": proxy_used,
    }

    # --- Check data sufficiency ---
    if net_profit is None or share_count is None or share_count == 0:
        return {
            "status": "data_needed",
            "inputs": inputs,
            "assumptions": assumptions,
            "intrinsic_value_per_share": None,
            "market_price": market_price,
            "margin_of_safety": None,
            "sensitivity": [],
            "input_quality": input_quality,
            "warnings": warnings,
        }

    # --- Calculate DCF ---
    # Explicit period cash flows
    growth_factor = 1 + growth_rate / 100
    discount_factor = 1 + discount_rate / 100

    explicit_cf = []
    for year in range(1, explicit_years + 1):
        cf = net_profit * (growth_factor ** year)
        pv = cf / (discount_factor ** year)
        explicit_cf.append({"year": year, "cash_flow": cf, "present_value": pv})

    total_pv_explicit = sum(item["present_value"] for item in explicit_cf)

    # Terminal value
    terminal_cf = explicit_cf[-1]["cash_flow"] * (1 + terminal_growth / 100)
    terminal_value = terminal_cf / (discount_rate / 100 - terminal_growth / 100)
    pv_terminal = terminal_value / (discount_factor ** explicit_years)

    # Intrinsic value
    total_value = total_pv_explicit + pv_terminal
    intrinsic_value_per_share = total_value / share_count

    # Margin of safety
    margin_of_safety = None
    if market_price is not None and market_price > 0:
        margin_of_safety = (intrinsic_value_per_share - market_price) / market_price * 100

    # Sensitivity table
    sensitivity = []
    for dr in [8.0, 10.0, 12.0]:
        for tg in [2.0, 3.0, 4.0]:
            df = 1 + dr / 100
            tcf = explicit_cf[-1]["cash_flow"] * (1 + tg / 100)
            tv = tcf / (dr / 100 - tg / 100)
            pv_tv = tv / (df ** explicit_years)
            t_pv = sum(cf["cash_flow"] / (df ** cf["year"]) for cf in explicit_cf)
            iv = (t_pv + pv_tv) / share_count
            sensitivity.append({
                "discount_rate": dr,
                "terminal_growth": tg,
                "intrinsic_value_per_share": round(iv, 2),
            })

    return {
        "status": "computed",
        "inputs": inputs,
        "assumptions": assumptions,
        "intrinsic_value_per_share": round(intrinsic_value_per_share, 2),
        "market_price": market_price,
        "margin_of_safety": round(margin_of_safety, 2) if margin_of_safety is not None else None,
        "sensitivity": sensitivity,
        "input_quality": input_quality,
        "warnings": warnings,
    }


def _comps_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute a comparable-company summary from snapshot data.

    Uses subject's PE/PB and industry peer multiples to determine relative
    valuation position. Returns status="data_needed" when peer data is
    insufficient for meaningful comparison.
    """
    sources = snapshot.get("sources", {})
    metrics = sources.get("metrics", {})
    fundamentals = sources.get("fundamentals", {})
    signals = sources.get("signals", {})
    industry_rows = signals.get("industry", [])

    warnings: list[str] = []

    # --- Extract subject metrics ---
    subject_pe = _first_number(metrics.get("pe_ttm"), metrics.get("pe"))
    subject_pb = _first_number(metrics.get("pb"))
    subject_name = fundamentals.get("name") or metrics.get("name") or snapshot.get("code", "")
    subject_industry = fundamentals.get("industry") or ""

    subject = {
        "name": subject_name,
        "industry": subject_industry,
        "pe_ttm": subject_pe,
        "pb": subject_pb,
    }

    # --- Extract peer multiples from industry rows ---
    peer_pe_values: list[float] = []
    peer_pb_values: list[float] = []
    rows: list[dict] = []

    for row in industry_rows:
        if not isinstance(row, dict):
            continue
        pe_val = _first_number(row.get("pe_ttm"), row.get("pe"))
        pb_val = _first_number(row.get("pb"))
        row_entry: dict[str, Any] = {
            "name": row.get("name", ""),
            "code": row.get("code", ""),
            "pe_ttm": pe_val,
            "pb": pb_val,
        }
        rows.append(row_entry)
        if pe_val is not None and pe_val > 0:
            peer_pe_values.append(pe_val)
        if pb_val is not None and pb_val > 0:
            peer_pb_values.append(pb_val)

    # --- Compute medians ---
    median_pe: float | None = None
    median_pb: float | None = None

    if peer_pe_values:
        sorted_pe = sorted(peer_pe_values)
        n = len(sorted_pe)
        median_pe = sorted_pe[n // 2] if n % 2 == 1 else (sorted_pe[n // 2 - 1] + sorted_pe[n // 2]) / 2

    if peer_pb_values:
        sorted_pb = sorted(peer_pb_values)
        n = len(sorted_pb)
        median_pb = sorted_pb[n // 2] if n % 2 == 1 else (sorted_pb[n // 2 - 1] + sorted_pb[n // 2]) / 2

    # --- Build input quality ---
    input_quality = {
        "peer_rows": len(rows),
        "pe_samples": len(peer_pe_values),
        "pb_samples": len(peer_pb_values),
        "missing": [],
    }
    if not peer_pe_values:
        input_quality["missing"].append("peer_pe")
    if not peer_pb_values:
        input_quality["missing"].append("peer_pb")
    if subject_pe is None:
        input_quality["missing"].append("subject_pe")
    if subject_pb is None:
        input_quality["missing"].append("subject_pb")

    # --- Determine data sufficiency ---
    if not peer_pe_values and not peer_pb_values:
        warnings.append("行业同业 PE/PB 数据不足，无法计算中位数")
        return {
            "status": "data_needed",
            "subject": subject,
            "rows": rows,
            "median_pe": None,
            "median_pb": None,
            "position": "unknown",
            "input_quality": input_quality,
            "warnings": warnings,
        }

    # --- Determine position ---
    position = "unknown"
    if subject_pe is not None and median_pe is not None:
        ratio = subject_pe / median_pe if median_pe > 0 else None
        if ratio is not None:
            if ratio < 0.9:
                position = "below_median"
            elif ratio > 1.1:
                position = "above_median"
            else:
                position = "near_median"

    if not peer_pe_values:
        warnings.append("行业同业 PE 数据不足")
    if not peer_pb_values:
        warnings.append("行业同业 PB 数据不足")

    return {
        "status": "computed",
        "subject": subject,
        "rows": rows,
        "median_pe": round(median_pe, 2) if median_pe is not None else None,
        "median_pb": round(median_pb, 2) if median_pb is not None else None,
        "position": position,
        "input_quality": input_quality,
        "warnings": warnings,
    }


def _lhb_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute a deterministic LHB (龙虎榜) summary from snapshot data.

    Derives row count, net-buy totals, and simple signals from
    sources.signals.dragon_tiger. Does NOT infer institution/hot-money/seat
    identity unless already present in the source rows.
    """
    signals = snapshot.get("sources", {}).get("signals", {})
    dragon_tiger = signals.get("dragon_tiger", [])

    warnings: list[str] = []

    if not dragon_tiger:
        warnings.append("龙虎榜数据缺失")
        return {
            "status": "data_needed",
            "rows": 0,
            "net_buy": None,
            "has_dragon_tiger": False,
            "signals": [],
            "warnings": warnings,
        }

    # Count rows
    row_count = len(dragon_tiger)

    # Sum net_buy across all rows (if field exists)
    net_buy_total = 0.0
    net_buy_found = False
    for row in dragon_tiger:
        if not isinstance(row, dict):
            continue
        nb = row.get("net_buy") or row.get("net_buy_amt") or row.get("buy_minus_sell")
        if nb is not None:
            try:
                net_buy_total += float(nb)
                net_buy_found = True
            except (TypeError, ValueError):
                pass

    # Derive simple signals
    lhb_signals: list[str] = []
    if net_buy_found:
        if net_buy_total > 0:
            lhb_signals.append("龙虎榜净买入为正")
        elif net_buy_total < 0:
            lhb_signals.append("龙虎榜净卖出")
        else:
            lhb_signals.append("龙虎榜买卖平衡")

    if row_count > 0:
        lhb_signals.append(f"龙虎榜共 {row_count} 条记录")

    return {
        "status": "computed",
        "rows": row_count,
        "net_buy": round(net_buy_total, 2) if net_buy_found else None,
        "has_dragon_tiger": True,
        "signals": lhb_signals,
        "warnings": warnings,
    }


# ── Agent analysis envelope ─────────────────────────────────────────────────────


_DEFAULT_AGENT_ANALYSIS: dict[str, Any] = {
    "status": "not_provided",
    "basis": "agent_qualitative_input",
    "thesis": "",
    "assumptions": [],
    "conflicts": [],
    "followups": [],
    "warnings": [],
}


def _empty_agent_analysis() -> dict[str, Any]:
    """Return a deep copy of the default agent analysis envelope."""
    return {
        "status": "not_provided",
        "basis": "agent_qualitative_input",
        "thesis": "",
        "assumptions": [],
        "conflicts": [],
        "followups": [],
        "warnings": [],
    }


def _validate_agent_analysis(raw: Any) -> dict[str, Any]:
    """Validate and normalize an agent analysis envelope.

    Raises ValueError if the input is not a dict with required fields.
    """
    if not isinstance(raw, dict):
        raise ValueError("agent_analysis must be a JSON object")

    envelope = _empty_agent_analysis()
    envelope["status"] = "provided"
    envelope["basis"] = "agent_qualitative_input"

    if "thesis" in raw:
        if not isinstance(raw["thesis"], str):
            raise ValueError("agent_analysis.thesis must be a string")
        envelope["thesis"] = raw["thesis"]

    for key in ("assumptions", "conflicts", "followups", "warnings"):
        if key in raw:
            val = raw[key]
            if not isinstance(val, list) or not all(isinstance(x, str) for x in val):
                raise ValueError(f"agent_analysis.{key} must be a list of strings")
            envelope[key] = val

    return envelope


def _dimension_summary(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Compute deterministic dimension summaries from snapshot data.

    Each dimension summarizes the status and quality of one analysis area.
    """
    quality_records = snapshot.get("data_quality", {}).get("sources", {})
    analysis = snapshot.get("analysis", {})

    def _dim_status(analysis_key: str, fallback: str = "computed") -> str:
        """Get status from analysis object."""
        obj = analysis.get(analysis_key, {})
        if isinstance(obj, dict):
            return obj.get("status", fallback)
        return fallback

    def _dim_quality(source_keys: list[str]) -> str:
        """Determine quality from source quality records."""
        qualities = []
        for key in source_keys:
            rec = quality_records.get(key, {})
            q = rec.get("quality", "missing")
            qualities.append(q)
        if not qualities:
            return "missing"
        if all(q == "full" for q in qualities):
            return "full"
        if any(q == "error" for q in qualities):
            return "error"
        if any(q == "skipped" for q in qualities):
            return "skipped"
        if any(q == "partial" for q in qualities):
            return "partial"
        return "missing"

    def _dim_warnings(source_keys: list[str]) -> list[str]:
        """Collect warnings from source quality records."""
        warnings = []
        for key in source_keys:
            rec = quality_records.get(key, {})
            warnings.extend(rec.get("warnings", []))
        return warnings

    # Basic: quote, fundamentals
    basic_sources = ["quote", "fundamentals"]
    basic_quality = _dim_quality(basic_sources)
    basic_warnings = _dim_warnings(basic_sources)

    # Market: quote, bars, metrics
    market_sources = ["quote", "bars", "metrics"]
    market_quality = _dim_quality(market_sources)
    market_warnings = _dim_warnings(market_sources)

    # Valuation: valuation, metrics
    valuation_sources = ["valuation", "metrics"]
    valuation_quality = _dim_quality(valuation_sources)
    valuation_warnings = _dim_warnings(valuation_sources)

    # Fundamentals: fundamentals, finance, f10
    fundamentals_sources = ["fundamentals", "finance", "f10"]
    fundamentals_quality = _dim_quality(fundamentals_sources)
    fundamentals_warnings = _dim_warnings(fundamentals_sources)

    # Capital flow: concept, fund_flow, dragon_tiger
    capital_flow_sources = ["concept", "fund_flow", "dragon_tiger"]
    capital_flow_quality = _dim_quality(capital_flow_sources)
    capital_flow_warnings = _dim_warnings(capital_flow_sources)

    # Panel: panel analysis
    panel_status = _dim_status("panel", "computed")
    panel_quality = "full" if panel_status == "computed" else "partial"

    # Risk: market_risk, trap_risk
    market_risk_status = _dim_status("market_risk", "computed")
    trap_risk_status = _dim_status("trap_risk", "unsupported")
    trap_risk_warnings = _dim_warnings(["trap_risk"]) if trap_risk_status == "unsupported" else []
    risk_warnings = trap_risk_warnings or (["社交/操纵风险检查尚未实现"] if trap_risk_status == "unsupported" else [])
    if trap_risk_status == "unsupported":
        risk_status = "partial"
        risk_quality = "partial"
    elif market_risk_status == "computed":
        risk_status = "computed"
        risk_quality = "full"
    else:
        risk_status = "partial"
        risk_quality = "partial"

    # LHB: lhb analysis
    lhb_status = _dim_status("lhb", "data_needed")
    lhb_quality = "full" if lhb_status == "computed" else "missing"

    # DCF: dcf analysis
    dcf_status = _dim_status("dcf", "data_needed")
    dcf_quality = "full" if dcf_status == "computed" else "missing"

    # Comps: comps analysis
    comps_status = _dim_status("comps", "data_needed")
    comps_quality = "full" if comps_status == "computed" else "missing"

    return {
        "basic": {
            "status": "computed" if basic_quality == "full" else "partial",
            "quality": basic_quality,
            "inputs": basic_sources,
            "outputs": ["summary"],
            "warnings": basic_warnings,
        },
        "market": {
            "status": "computed" if market_quality == "full" else "partial",
            "quality": market_quality,
            "inputs": market_sources,
            "outputs": ["quote", "bars", "metrics"],
            "warnings": market_warnings,
        },
        "valuation": {
            "status": "computed" if valuation_quality == "full" else "partial",
            "quality": valuation_quality,
            "inputs": valuation_sources,
            "outputs": ["valuation"],
            "warnings": valuation_warnings,
        },
        "fundamentals": {
            "status": "computed" if fundamentals_quality == "full" else "partial",
            "quality": fundamentals_quality,
            "inputs": fundamentals_sources,
            "outputs": ["fundamentals", "finance", "f10"],
            "warnings": fundamentals_warnings,
        },
        "capital_flow": {
            "status": "computed" if capital_flow_quality == "full" else "partial",
            "quality": capital_flow_quality,
            "inputs": capital_flow_sources,
            "outputs": ["concept", "fund_flow", "dragon_tiger"],
            "warnings": capital_flow_warnings,
        },
        "panel": {
            "status": panel_status,
            "quality": panel_quality,
            "inputs": ["quote", "metrics", "valuation", "finance"],
            "outputs": ["panel"],
            "warnings": [],
        },
        "risk": {
            "status": risk_status,
            "quality": risk_quality,
            "inputs": ["block_trade", "margin_trading", "holder_num", "fund_flow"],
            "outputs": ["market_risk", "trap_risk"],
            "warnings": risk_warnings,
        },
        "lhb": {
            "status": lhb_status,
            "quality": lhb_quality,
            "inputs": ["dragon_tiger"],
            "outputs": ["lhb"],
            "warnings": [],
        },
        "dcf": {
            "status": dcf_status,
            "quality": dcf_quality,
            "inputs": ["quote", "metrics", "valuation", "finance"],
            "outputs": ["dcf"],
            "warnings": [],
        },
        "comps": {
            "status": comps_status,
            "quality": comps_quality,
            "inputs": ["quote", "metrics", "fundamentals", "industry"],
            "outputs": ["comps"],
            "warnings": [],
        },
    }


# ── Synthesis layer ─────────────────────────────────────────────────────────


def _synthesis_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute deterministic synthesis from existing analysis objects.

    Uses only: panel, market_risk, dcf, comps, lhb, dimensions, data_quality.
    No LLM or agent-authored content.
    """
    analysis = snapshot.get("analysis", {})
    panel = analysis.get("panel", {})
    market_risk = analysis.get("market_risk", {})
    dcf = analysis.get("dcf", {})
    comps = analysis.get("comps", {})
    lhb = analysis.get("lhb", {})
    dimensions = analysis.get("dimensions", {})
    data_quality = snapshot.get("data_quality", {})

    drivers: list[str] = []
    risks: list[str] = []
    conflicts: list[str] = []
    followups: list[str] = []

    # --- Stance from panel verdict ---
    panel_verdict = panel.get("verdict", "neutral")
    panel_score = panel.get("score", 50)
    vote_dist = panel.get("vote_distribution", {})
    data_needed_count = vote_dist.get("data_needed", 0)
    total_votes = sum(vote_dist.values())

    # If all signals are data_needed, synthesis is data_needed
    if total_votes > 0 and data_needed_count == total_votes:
        stance = "data_needed"
    elif panel_verdict in ("bullish", "bearish"):
        stance = panel_verdict
    else:
        stance = "neutral"

    # --- Confidence from data completeness and signal agreement ---
    complete = data_quality.get("complete", False)
    pass_count = vote_dist.get("pass", 0)
    fail_count = vote_dist.get("fail", 0)
    max_single = max(pass_count, fail_count, data_needed_count)

    if stance == "data_needed":
        confidence = "low"
    elif complete and total_votes > 0 and max_single >= 3:
        confidence = "high"
    elif total_votes > 0 and max_single >= 2 and complete:
        confidence = "medium"
    else:
        confidence = "low"

    # --- Drivers from panel reasons and positive signals ---
    panel_reasons = panel.get("reasons", [])
    for reason in panel_reasons[:3]:
        drivers.append(reason)

    # --- Risks from market risk flags and risk dimension warnings ---
    risk_flags = market_risk.get("flags", [])
    for flag in risk_flags:
        risks.append(flag)

    # Risk dimension warnings (includes trap_risk unsupported warning)
    risk_dimension = dimensions.get("risk", {})
    for warning in risk_dimension.get("warnings", []):
        if warning not in risks:
            risks.append(warning)

    # --- Conflicts: disagreeing investor signals ---
    panel_signals = panel.get("signals", [])
    has_bullish = any(s["signal"] == "pass" for s in panel_signals)
    has_bearish = any(s["signal"] == "fail" for s in panel_signals)
    if has_bullish and has_bearish:
        conflicts.append("投资者面板内部存在多空分歧")

    # DCF vs comps disagreement
    dcf_status = dcf.get("status", "data_needed")
    comps_status = comps.get("status", "data_needed")
    if dcf_status == "computed" and comps_status == "computed":
        dcf_mos = dcf.get("margin_of_safety")
        comps_position = comps.get("position", "unknown")
        if dcf_mos is not None and dcf_mos > 20 and comps_position == "above_median":
            conflicts.append("DCF 显示安全边际但同业估值偏高")
        elif dcf_mos is not None and dcf_mos < -20 and comps_position == "below_median":
            conflicts.append("DCF 显示高估但同业估值偏低")

    # --- Followups from data gaps ---
    for dim_key, dim in dimensions.items():
        if dim.get("quality") in ("missing", "error"):
            followups.append(f"补充 {dim_key} 维度数据")

    # LHB data needed
    if lhb.get("status") == "data_needed":
        followups.append("补充龙虎榜数据")

    return {
        "basis": "deterministic_hoxit_analysis",
        "stance": stance,
        "confidence": confidence,
        "drivers": drivers,
        "risks": risks,
        "conflicts": conflicts,
        "followups": followups,
    }


def _mode_profile(mode: str) -> dict[str, str]:
    profiles = {
        "quick-scan": {"depth": "lite", "primary_section": "summary"},
        "dcf": {"depth": "focused", "primary_section": "valuation"},
        "comps": {"depth": "focused", "primary_section": "industry"},
        "panel-only": {"depth": "focused", "primary_section": "panel"},
        "scan-trap": {"depth": "focused", "primary_section": "market_risk"},
        "lhb-analyzer": {"depth": "focused", "primary_section": "dragon_tiger"},
        "analyze-stock": {"depth": "standard", "primary_section": "full_report"},
    }
    return profiles.get(mode, profiles["analyze-stock"])


def analyze_snapshot(
    snapshot: dict[str, Any],
    *,
    agent_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    quote = snapshot["sources"].get("quote", {})
    fundamentals = snapshot["sources"].get("fundamentals", {})

    # Validate agent_analysis if provided
    validated_agent = _empty_agent_analysis()
    if agent_analysis is not None:
        validated_agent = _validate_agent_analysis(agent_analysis)

    snapshot["analysis"] = {
        "summary": {
            "name": quote.get("name") or fundamentals.get("name") or "",
            "price": quote.get("price"),
            "change_pct": quote.get("change_pct"),
        },
        "valuation": snapshot["sources"].get("valuation", {}),
        "industry": {"rows": snapshot["sources"].get("signals", {}).get("industry", [])},
        "panel": _panel_summary(snapshot),
        "market_risk": _market_risk(snapshot),
        "trap_risk": _trap_risk(snapshot),
        "dcf": _dcf_analysis(snapshot),
        "comps": _comps_summary(snapshot),
        "lhb": _lhb_summary(snapshot),
        "mode_profile": _mode_profile(snapshot.get("mode", "analyze-stock")),
        "agent_analysis": validated_agent,
        "followups": [],
    }
    # Compute dimensions after analysis dict is populated so _dim_status can read it
    snapshot["analysis"]["dimensions"] = _dimension_summary(snapshot)
    # Compute synthesis after dimensions are populated
    snapshot["analysis"]["synthesis"] = _synthesis_summary(snapshot)
    return snapshot


def _fmt_number(value: Any, suffix: str = "", precision: int = 2) -> str:
    """Format a number with optional suffix, or return '缺失'."""
    if value is None:
        return "缺失"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "缺失"
    if precision == 0:
        return f"{num:,.0f}{suffix}"
    return f"{num:,.{precision}f}{suffix}"


def _fmt_pct(value: Any) -> str:
    """Format a percentage value."""
    if value is None:
        return "缺失"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "缺失"
    sign = "+" if num > 0 else ""
    return f"{sign}{num:.2f}%"


def _fmt_market_cap(value: Any) -> str:
    """Format market cap in 亿 units."""
    if value is None:
        return "缺失"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "缺失"
    yi = num / 1e8
    return f"{yi:,.2f}亿"


def _compact_list(items: list[dict], key: str, max_items: int = 3) -> str:
    """Format a list of dicts as compact bullet points."""
    if not items:
        return "暂无数据"
    selected = items[:max_items]
    parts = [f"  - {item.get(key, '未知')}" for item in selected]
    if len(items) > max_items:
        parts.append(f"  - ……共 {len(items)} 条")
    return "\n".join(parts)


def _compact_concepts(concepts: list[dict], max_items: int = 8) -> str:
    """Format concept list as comma-separated names."""
    if not concepts:
        return "暂无概念数据"
    names = [c.get("name", "未知") for c in concepts[:max_items]]
    result = "、".join(names)
    if len(concepts) > max_items:
        result += f"等 {len(concepts)} 个概念"
    return result


def _group_warnings(warnings: list[str]) -> list[str]:
    """Group and de-duplicate warnings."""
    if not warnings:
        return ["无警告"]
    seen: set[str] = set()
    unique: list[str] = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique


def render_markdown(snapshot: dict[str, Any], *, mode: str | None = None) -> str:
    analysis = snapshot.get("analysis") or {}
    summary = analysis.get("summary", {})
    panel = analysis.get("panel", {})
    risk = analysis.get("market_risk", {})
    sources = snapshot.get("sources", {})
    signals = sources.get("signals", {})
    raw_warnings = snapshot.get("data_quality", {}).get("warnings", [])
    warnings = _group_warnings(raw_warnings)

    # Determine which sections to render
    mode = mode or snapshot.get("mode", "analyze-stock")
    sections = _sections_for_mode(mode)

    # --- 核心结论 ---
    quote = sources.get("quote", {})
    valuation = sources.get("valuation", {})
    metrics = sources.get("metrics", {})
    fundamentals = sources.get("fundamentals", {})
    finance = sources.get("finance", {})

    name = summary.get("name") or "未知"
    price = _fmt_number(summary.get("price"), "元")
    change_pct = _fmt_pct(summary.get("change_pct"))
    panel_verdict = panel.get("verdict", "neutral")
    panel_score = panel.get("score", 50)

    lines = [
        f"# UZEN A股分析：{snapshot['code']}",
        "",
        "## 核心结论",
        f"- 名称：{name}",
        f"- 最新价：{price}",
        f"- 涨跌幅：{change_pct}",
        f"- 轻量面板：{panel_verdict}，分数 {panel_score}",
    ]

    # --- 数据完整性 ---
    if "data_quality" in sections:
        lines.extend([
            "",
            "## 数据完整性",
            f"- 完整性：{'完整' if snapshot.get('data_quality', {}).get('complete') else '存在缺口'}",
        ])
        lines.extend(f"- 警告：{w}" for w in warnings)

    # --- 行情与估值 ---
    if "market_valuation" in sections:
        forward_pe = _fmt_number(valuation.get("forward_pe"), "倍")
        peg = _fmt_number(valuation.get("peg"))
        pe_ttm = _fmt_number(metrics.get("pe_ttm"), "倍")
        pb = _fmt_number(metrics.get("pb"))
        market_cap = _fmt_market_cap(metrics.get("market_cap"))

        lines.extend([
            "",
            "## 行情与估值",
            f"- 前瞻 PE：{forward_pe}",
            f"- PEG：{peg}",
            f"- PE TTM：{pe_ttm}",
            f"- PB：{pb}",
            f"- 总市值：{market_cap}",
        ])

    # --- 基本面与财务 ---
    if "fundamentals" in sections:
        industry = fundamentals.get("industry") or "未知行业"
        roe = _fmt_number(finance.get("roe") or finance.get("ROE"), "%")
        net_profit = _fmt_number(finance.get("net_profit"), "元")

        lines.extend([
            "",
            "## 基本面与财务",
            f"- 行业：{industry}",
            f"- ROE：{roe}",
            f"- 净利润：{net_profit}",
        ])

    # --- 研报、新闻与公告 ---
    if "reports_news_filings" in sections:
        reports = sources.get("reports", [])
        news = sources.get("news", [])
        filings = sources.get("filings", [])

        lines.extend([
            "",
            "## 研报、新闻与公告",
            f"- 研报（{len(reports)} 条）：",
            _compact_list(reports, "title"),
            f"- 新闻（{len(news)} 条）：",
            _compact_list(news, "title"),
            f"- 公告（{len(filings)} 条）：",
            _compact_list(filings, "title"),
        ])

    # --- 资金、龙虎榜与题材 ---
    if "capital_flow" in sections:
        concepts = signals.get("concept", [])
        fund_flow = signals.get("fund_flow", [])
        dragon_tiger = signals.get("dragon_tiger", [])

        lines.extend([
            "",
            "## 资金、龙虎榜与题材",
            f"- 概念：{_compact_concepts(concepts)}",
            f"- 资金流记录数：{len(fund_flow)}",
            f"- 龙虎榜记录数：{len(dragon_tiger)}",
        ])

    # --- 龙虎榜分析 ---
    if "lhb" in sections:
        lhb = analysis.get("lhb", {})
        lhb_status = lhb.get("status", "data_needed")
        lines.extend([
            "",
            "## 龙虎榜分析",
        ])
        if lhb_status == "computed":
            lines.extend([
                f"- 状态：已计算",
                f"- 记录数：{lhb.get('rows', 0)}",
            ])
            net_buy = lhb.get("net_buy")
            if net_buy is not None:
                lines.append(f"- 净买入合计：{_fmt_number(net_buy, '元')}")
            lhb_signals = lhb.get("signals", [])
            if lhb_signals:
                lines.append("- 信号：")
                for sig in lhb_signals:
                    lines.append(f"  - {sig}")
        else:
            lines.extend([
                f"- 状态：数据不足（data_needed）",
            ])
            lhb_warnings = lhb.get("warnings", [])
            if lhb_warnings:
                lines.extend(f"- 缺失：{w}" for w in lhb_warnings)
            else:
                lines.append("- 缺失：龙虎榜数据不完整")

    # --- 行业与同业 ---
    if "industry" in sections:
        industry_rows = signals.get("industry", [])
        lines.extend([
            "",
            "## 行业与同业",
            f"- 行业样本数：{len(industry_rows)}",
        ])

    # --- 投资者面板 ---
    if "panel" in sections:
        panel_reasons = panel.get("reasons", [])
        panel_signals = panel.get("signals", [])
        vote_dist = panel.get("vote_distribution", {})

        lines.extend([
            "",
            "## 投资者面板",
            f"- 综合结论：{panel_verdict}",
            f"- 综合分数：{panel_score}",
        ])

        # Vote distribution
        if vote_dist:
            vote_parts = []
            for signal_type in ["pass", "fail", "neutral", "data_needed"]:
                count = vote_dist.get(signal_type, 0)
                if count > 0:
                    label = {
                        "pass": "看多",
                        "fail": "看空",
                        "neutral": "中性",
                        "data_needed": "数据不足",
                    }.get(signal_type, signal_type)
                    vote_parts.append(f"{label} {count}")
            lines.append(f"- 投票分布：{'，'.join(vote_parts)}")

        # Individual signals
        if panel_signals:
            lines.append("- 投资者信号：")
            for sig in panel_signals:
                signal_label = {
                    "pass": "✓ 看多",
                    "fail": "✗ 看空",
                    "neutral": "— 中性",
                    "data_needed": "? 数据不足",
                }.get(sig["signal"], sig["signal"])
                lines.append(f"  - {sig['name']}：{signal_label}（{sig['score']}分）")
                if sig["reasoning"]:
                    lines.append(f"    - {sig['reasoning'][0]}")

        # Reasons
        if panel_reasons:
            lines.append(f"- 关键理由：{'；'.join(panel_reasons[:3])}")

    # --- 市场数据风险检查 ---
    if "market_risk" in sections:
        risk_level = risk.get("level", "low")
        risk_flags = risk.get("flags", [])
        lines.extend([
            "",
            "## 市场数据风险检查",
            f"- 风险等级：{risk_level}",
            f"- 数据来源：市场数据（非社交证据）",
            f"- 风险标记：{'；'.join(risk_flags) if risk_flags else '未触发市场数据风险标记'}",
        ])

    # --- 社交/操纵风险检查 ---
    if "trap_risk" in sections:
        trap = analysis.get("trap_risk", {})
        trap_status = trap.get("status", "unsupported")
        trap_warnings = trap.get("warnings", [])
        lines.extend([
            "",
            "## 社交/操纵风险检查",
            f"- 状态：{'尚未支持' if trap_status == 'unsupported' else trap_status}",
            f"- 说明：社交证据采集尚未实现，当前不提供杀猪盘/操纵证据判断",
        ])
        if trap_warnings:
            lines.extend(f"- 提示：{w}" for w in trap_warnings)

    # --- DCF 估值 ---
    if "dcf" in sections:
        dcf = analysis.get("dcf", {})
        dcf_status = dcf.get("status", "data_needed")
        if dcf_status == "computed":
            iv = _fmt_number(dcf.get("intrinsic_value_per_share"), "元")
            mp = _fmt_number(dcf.get("market_price"), "元")
            mos = _fmt_number(dcf.get("margin_of_safety"), "%")
            lines.extend([
                "",
                "## DCF 估值",
                f"- 状态：已计算",
                f"- 内在价值（Intrinsic Value）：{iv}",
                f"- 市场价格：{mp}",
                f"- 安全边际（Margin of Safety）：{mos}",
                f"- 折现率（Discount Rate）：{dcf.get('assumptions', {}).get('discount_rate', {}).get('value', 'N/A')}%",
                f"- 终端增长率（Terminal Growth）：{dcf.get('assumptions', {}).get('terminal_growth', {}).get('value', 'N/A')}%",
            ])
            # Sensitivity table
            sensitivity = dcf.get("sensitivity", [])
            if sensitivity:
                lines.append("- 敏感性分析（Sensitivity）：")
                for s in sensitivity:
                    lines.append(f"  - 折现率 {s['discount_rate']}% / 终端增长 {s['terminal_growth']}%：{_fmt_number(s['intrinsic_value_per_share'], '元')}")
            # Input quality
            iq = dcf.get("input_quality", {})
            if iq:
                available = iq.get("available", [])
                missing = iq.get("missing", [])
                proxy = iq.get("proxy_used", [])
                if available:
                    lines.append(f"- 输入可用：{'、'.join(available)}")
                if missing:
                    lines.append(f"- 输入缺失：{'、'.join(missing)}")
                if proxy:
                    lines.append(f"- 代理指标：{'、'.join(proxy)}")
            # Warnings
            dcf_warnings = dcf.get("warnings", [])
            if dcf_warnings:
                lines.extend(f"- 警告：{w}" for w in dcf_warnings)
        else:
            lines.extend([
                "",
                "## DCF 估值",
                f"- 状态：数据不足（data_needed）",
            ])
            # Input quality
            iq = dcf.get("input_quality", {})
            if iq:
                missing = iq.get("missing", [])
                if missing:
                    lines.append(f"- 输入缺失：{'、'.join(missing)}")
            dcf_warnings = dcf.get("warnings", [])
            if dcf_warnings:
                lines.extend(f"- 缺失：{w}" for w in dcf_warnings)
            else:
                lines.append("- 缺失：输入数据不完整")

    # --- 同业比较（Comps） ---
    if "comps" in sections:
        comps = analysis.get("comps", {})
        comps_status = comps.get("status", "data_needed")
        comps_subject = comps.get("subject", {})
        comps_position = comps.get("position", "unknown")
        position_label = {
            "below_median": "低于中位数",
            "near_median": "接近中位数",
            "above_median": "高于中位数",
            "unknown": "未知",
        }.get(comps_position, "未知")

        lines.extend([
            "",
            "## 同业比较（Comps）",
        ])

        if comps_status == "computed":
            median_pe = _fmt_number(comps.get("median_pe"), "倍")
            median_pb = _fmt_number(comps.get("median_pb"))
            subject_pe = _fmt_number(comps_subject.get("pe_ttm"), "倍")
            subject_pb = _fmt_number(comps_subject.get("pb"))
            peer_count = len(comps.get("rows", []))

            lines.extend([
                f"- 状态：已计算",
                f"- 样本数：{peer_count} 家同业",
                f"- 主体 PE TTM：{subject_pe}",
                f"- 行业中位 PE：{median_pe}",
                f"- 主体 PB：{subject_pb}",
                f"- 行业中位 PB：{median_pb}",
                f"- 估值位置：{position_label}",
            ])
            # Input quality
            iq = comps.get("input_quality", {})
            if iq:
                pe_samples = iq.get("pe_samples", 0)
                pb_samples = iq.get("pb_samples", 0)
                missing = iq.get("missing", [])
                lines.append(f"- PE 样本数：{pe_samples}")
                lines.append(f"- PB 样本数：{pb_samples}")
                if missing:
                    lines.append(f"- 输入缺失：{'、'.join(missing)}")
            comps_warnings = comps.get("warnings", [])
            if comps_warnings:
                lines.extend(f"- 警告：{w}" for w in comps_warnings)
        else:
            lines.extend([
                f"- 状态：数据不足（data_needed）",
            ])
            # Input quality
            iq = comps.get("input_quality", {})
            if iq:
                peer_rows = iq.get("peer_rows", 0)
                missing = iq.get("missing", [])
                lines.append(f"- 同业行数：{peer_rows}")
                if missing:
                    lines.append(f"- 输入缺失：{'、'.join(missing)}")
            comps_warnings = comps.get("warnings", [])
            if comps_warnings:
                lines.extend(f"- 缺失：{w}" for w in comps_warnings)
            else:
                lines.append("- 缺失：同业数据不完整")

    # --- 综合研判 ---
    if "synthesis" in sections:
        synth = analysis.get("synthesis", {})
        synth_stance = synth.get("stance", "data_needed")
        synth_confidence = synth.get("confidence", "low")

        stance_label = {
            "bullish": "看多",
            "bearish": "看空",
            "neutral": "中性",
            "data_needed": "数据不足",
        }.get(synth_stance, "数据不足")

        confidence_label = {
            "high": "高",
            "medium": "中",
            "low": "低",
        }.get(synth_confidence, "低")

        lines.extend([
            "",
            "## 综合研判",
            f"- 立场：{stance_label}",
            f"- 置信度：{confidence_label}",
        ])

        synth_drivers = synth.get("drivers", [])
        if synth_drivers:
            lines.append("- 驱动因素：")
            for d in synth_drivers[:3]:
                lines.append(f"  - {d}")

        synth_risks = synth.get("risks", [])
        if synth_risks:
            lines.append("- 风险因素：")
            for r in synth_risks[:3]:
                lines.append(f"  - {r}")

        synth_conflicts = synth.get("conflicts", [])
        if synth_conflicts:
            lines.append("- 矛盾信号：")
            for c in synth_conflicts:
                lines.append(f"  - {c}")

        synth_followups = synth.get("followups", [])
        if synth_followups:
            lines.append("- 后续验证：")
            for f in synth_followups[:3]:
                lines.append(f"  - {f}")

    # --- Agent Analysis ---
    agent = analysis.get("agent_analysis", {})
    if agent.get("status") == "provided":
        lines.extend([
            "",
            "## Agent 定性分析",
        ])
        if agent.get("thesis"):
            lines.append(f"- 核心论点：{agent['thesis']}")
        if agent.get("assumptions"):
            lines.append("- 假设条件：")
            for a in agent["assumptions"]:
                lines.append(f"  - {a}")
        if agent.get("conflicts"):
            lines.append("- 矛盾/风险：")
            for c in agent["conflicts"]:
                lines.append(f"  - {c}")
        if agent.get("followups"):
            lines.append("- 后续验证项：")
            for f in agent["followups"]:
                lines.append(f"  - {f}")
        if agent.get("warnings"):
            lines.append("- 警告：")
            for w in agent["warnings"]:
                lines.append(f"  - {w}")

    # --- 后续跟踪项 ---
    if "followups" in sections:
        lines.extend([
            "",
            "## 后续跟踪项",
            "- 对缺失数据源做人工复核。",
        ])

    # --- 免责声明 ---
    lines.extend([
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
    agent_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot = collect_snapshot(code, mode=mode, provider=provider, today=today, trade_date=trade_date)
    snapshot = analyze_snapshot(snapshot, agent_analysis=agent_analysis)
    markdown = render_markdown(snapshot, mode=mode)
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
