from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
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

    quote_map = _safe_call("quote", provider.quote, [code], warnings=warnings, default={})
    quote = quote_map.get(code, {}) if isinstance(quote_map, dict) else {}
    f10 = _safe_call("f10", provider.f10, code, warnings=warnings, default={})
    if isinstance(f10, dict) and f10.get("status") == "unsupported":
        warnings.extend(str(item) for item in f10.get("warnings", []))

    sources = {
        "quote": quote,
        "bars": _safe_call("bars", provider.bars, code, category=4, offset=60, adjust="qfq", warnings=warnings, default=[]),
        "metrics": _safe_call("metrics", provider.metrics, [code], warnings=warnings, default={}).get(code, {}),
        "valuation": _safe_call("valuation", provider.valuation, code, warnings=warnings, default={}),
        "fundamentals": _safe_call("fundamentals", provider.fundamentals, code, warnings=warnings, default={}),
        "finance": _safe_call("finance", provider.finance, code, warnings=warnings, default={}),
        "f10": f10,
        "reports": _safe_call("reports", provider.reports, code, warnings=warnings, default=[]),
        "news": _safe_call("news", provider.news, code, warnings=warnings, default=[]),
        "filings": _safe_call("filings", provider.filings, code, start_date, end_date, warnings=warnings, default=[]),
        "signals": {
            "hot": _safe_call("hot", provider.hot, today, exclude_st=True, warnings=warnings, default=[]),
            "concept": _safe_call("concept", provider.concept, code, warnings=warnings, default=[]),
            "fund_flow": _safe_call("fund_flow", provider.fund_flow, code, days=20, warnings=warnings, default=[]),
            "dragon_tiger": _safe_call("dragon_tiger", provider.dragon_tiger, code, trade_date, warnings=warnings, default=[]),
            "lockup": _safe_call("lockup", provider.lockup, code, trade_date, forward_days=90, warnings=warnings, default=[]),
            "industry": _safe_call("industry", provider.industry, top_n=20, warnings=warnings, default=[]),
            "margin_trading": _safe_call("margin_trading", provider.margin_trading, code, page_size=30, warnings=warnings, default=[]),
            "block_trade": _safe_call("block_trade", provider.block_trade, code, page_size=20, warnings=warnings, default=[]),
            "holder_num": _safe_call("holder_num", provider.holder_num, code, page_size=10, warnings=warnings, default=[]),
            "dividend": _safe_call("dividend", provider.dividend, code, page_size=20, warnings=warnings, default=[]),
        },
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
