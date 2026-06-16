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
    governance: Callable[[str], dict] = _empty_mapping
    business: Callable[[str], dict] = _empty_mapping
    event: Callable[[str], dict] = _empty_mapping


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
        governance=fundamentals.governance_summary,
        business=fundamentals.business_summary,
        event=signals.event_summary,
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
        "governance", "business", "event",
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
        "governance", "business", "events", "lhb_detail",
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

    def _is_empty_result(result: Any) -> bool:
        if result is None:
            return True
        if hasattr(result, "empty"):
            return bool(getattr(result, "empty"))
        if isinstance(result, (dict, list, tuple, set, str, bytes)):
            return len(result) == 0
        return False

    def _map_or_skip(key: str, func: Callable, *args: Any, required: bool = True, **kwargs: Any) -> dict:
        if key not in needed:
            quality_records[key] = _quality_record(key, quality="skipped", source=f"provider.{key}", warnings=[], required=required)
            return {}
        result, error = _safe_call(key, func, *args, warnings=warnings, default={}, **kwargs)
        if error:
            quality_records[key] = _quality_record(key, quality="error", source=f"provider.{key}", warnings=[error], required=required)
        elif _is_empty_result(result):
            quality_records[key] = _quality_record(key, quality="missing", source=f"provider.{key}", warnings=[], required=required)
        elif isinstance(result, dict) and result.get("status") in ("data_needed", "missing"):
            # PR-DATA-001 interfaces return non-empty dicts with status: "data_needed"
            # when data is unavailable. Treat as "missing" and propagate warnings.
            payload_warnings = [str(w) for w in result.get("warnings", []) if w]
            quality_records[key] = _quality_record(key, quality="missing", source=f"provider.{key}", warnings=payload_warnings, required=required)
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
        elif _is_empty_result(result):
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
        "governance": _map_or_skip("governance", provider.governance, code),
        "business": _map_or_skip("business", provider.business, code),
        "event": _map_or_skip("event", provider.event, code),
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

    # --- normalise live provider shapes (PR-LIVE-001 / PR-LIVE-003) ---------
    sources["finance"] = _normalize_finance(sources.get("finance"))
    original_finance = dict(sources["finance"])  # snapshot before F10 merge
    # Merge finance fields from F10 sections if finance is incomplete
    sources["finance"] = _normalize_f10(sources.get("f10", {}), sources["finance"])
    signals = sources.get("signals", {})
    signals["concept"] = _normalize_concept(signals.get("concept"))
    signals["dragon_tiger"] = _normalize_dragon_tiger(signals.get("dragon_tiger"))

    # --- field-level finance quality (PR-LIVE-003) --------------------------
    # Only evaluate when finance was actually fetched (not skipped)
    finance_rec = quality_records.get("finance")
    if finance_rec and finance_rec.get("quality") != "skipped":
        f10_source = sources.get("f10", {})
        finance_q = _finance_field_quality(sources["finance"], f10_source, original_finance)
        for field, rec in finance_q.items():
            quality_map = {"available": "full", "missing": "missing", "unsupported": "missing"}
            qrec = _quality_record(
                f"finance.{field}",
                quality=quality_map.get(rec["status"], "missing"),
                source=rec["source"],
                warnings=[rec["warning"]] if rec["warning"] else [],
                required=False,
            )
            qrec["status"] = rec["status"]  # preserve available/missing/unsupported
            quality_records[f"finance.{field}"] = qrec

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


def _quote_change_pct(quote: dict[str, Any]) -> float | None:
    change_pct = _first_number(quote.get("change_pct"))
    if change_pct is not None:
        return change_pct
    price = _first_number(quote.get("price"))
    last_close = _first_number(quote.get("last_close"))
    if price is None or last_close in (None, 0):
        return None
    return round((price - last_close) / last_close * 100, 2)


# --- Derived market metrics (PR-LIVE-002) ---------------------------------
# Compute deterministic OHLCV-derived metrics from quote and bars so basic
# report fields do not remain missing when providers expose the inputs.


def _quote_change_amount(quote: dict[str, Any]) -> float | None:
    """Derive change_amount = price - last_close."""
    amount = _first_number(quote.get("change_amount"))
    if amount is not None:
        return amount
    price = _first_number(quote.get("price"))
    last_close = _first_number(quote.get("last_close"))
    if price is None or last_close is None:
        return None
    return round(price - last_close, 4)


def _quote_amplitude_pct(quote: dict[str, Any]) -> float | None:
    """Derive amplitude_pct = (high - low) / last_close * 100."""
    amp = _first_number(quote.get("amplitude_pct"))
    if amp is not None:
        return amp
    high = _first_number(quote.get("high"))
    low = _first_number(quote.get("low"))
    last_close = _first_number(quote.get("last_close"))
    if high is None or low is None or last_close in (None, 0):
        return None
    return round((high - low) / last_close * 100, 2)


def _bars_closes(bars: list[dict]) -> list[float]:
    """Extract valid close prices from bars, oldest first."""
    closes: list[float] = []
    for bar in bars:
        c = _first_number(bar.get("close"))
        if c is not None:
            closes.append(c)
    return closes


def _bars_ma(closes: list[float], n: int) -> float | None:
    """Simple moving average of last n closes."""
    if len(closes) < n:
        return None
    return round(sum(closes[-n:]) / n, 4)


def _bars_return(closes: list[float], n: int) -> float | None:
    """Return over last n bars: (latest / older - 1) * 100."""
    if len(closes) <= n:
        return None
    older = closes[-(n + 1)]
    if older == 0:
        return None
    return round((closes[-1] / older - 1) * 100, 2)


def _bars_volatility(closes: list[float], n: int) -> float | None:
    """Annualised volatility from last n daily returns."""
    if len(closes) < n + 1:
        return None
    recent = closes[-(n + 1):]
    returns = [(recent[i] / recent[i - 1] - 1) for i in range(1, len(recent)) if recent[i - 1] != 0]
    if len(returns) < 2:
        return None
    mean_r = sum(returns) / len(returns)
    variance = sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)
    daily_vol = variance ** 0.5
    return round(daily_vol * (242 ** 0.5) * 100, 2)  # annualised, 242 trading days


def _bars_drawdown(closes: list[float], n: int) -> float | None:
    """Max drawdown over last n bars: (peak - trough) / peak * 100."""
    if len(closes) < n:
        return None
    recent = closes[-n:]
    peak = recent[0]
    max_dd = 0.0
    for c in recent:
        if c > peak:
            peak = c
        if peak > 0:
            dd = (peak - c) / peak * 100
            if dd > max_dd:
                max_dd = dd
    return round(max_dd, 2)


def _quote_avg_price(quote: dict[str, Any]) -> float | None:
    """Volume-weighted average price from quote turnover/volume (成交均价).

    Priority:
    1. Direct ``avg_price`` field from provider — use as-is.
    2. Compute from ``amount`` / volume when ``vol_unit`` is explicit:
       - ``"shares"`` or ``"股"`` → amount / vol
       - ``"lots"`` or ``"手"`` → amount / (vol × 100)
    3. Returns None with warning when unit is ambiguous or data missing.

    A-share ``vol`` may be in 手 (lots, 1手=100股) or 股 (shares) depending
    on provider.  Guessing the unit produces plausible-but-wrong numbers, so
    we require an explicit signal.
    """
    # 1. Direct field takes priority
    direct = _first_number(quote.get("avg_price"))
    if direct is not None:
        return direct

    # 2. Compute from amount / vol with explicit unit
    amount = _first_number(quote.get("amount"))
    vol = _first_number(quote.get("vol"))
    if amount is None or vol is None or vol <= 0:
        return None

    unit = str(quote.get("vol_unit", "")).strip().lower()
    if unit in ("shares", "股"):
        return round(amount / vol, 4)
    if unit in ("lots", "手"):
        return round(amount / (vol * 100), 4)

    # 3. Ambiguous unit — refuse to guess
    return None


def _derive_market_metrics(quote: dict[str, Any], bars: list[dict]) -> dict[str, Any]:
    """Compute deterministic market metrics from quote and bars.

    Returns a dict with derived fields and a ``_meta`` key recording which
    inputs were available.  Direct provider fields are preserved when present.
    """
    closes = _bars_closes(bars)
    meta: dict[str, Any] = {
        "quote_inputs": [],
        "bars_count": len(closes),
    }

    # --- Quote-derived ---
    change_pct = _quote_change_pct(quote)
    change_amount = _quote_change_amount(quote)
    amplitude_pct = _quote_amplitude_pct(quote)

    if _first_number(quote.get("price")) is not None:
        meta["quote_inputs"].append("price")
    if _first_number(quote.get("last_close")) is not None:
        meta["quote_inputs"].append("last_close")
    if _first_number(quote.get("high")) is not None:
        meta["quote_inputs"].append("high")
    if _first_number(quote.get("low")) is not None:
        meta["quote_inputs"].append("low")

    # --- Bars-derived ---
    ma5 = _bars_ma(closes, 5)
    ma20 = _bars_ma(closes, 20)
    return_5d = _bars_return(closes, 5)
    return_20d = _bars_return(closes, 20)
    volatility_20d = _bars_volatility(closes, 20)
    drawdown_60d = _bars_drawdown(closes, 60)
    avg_price = _quote_avg_price(quote)

    # Track missing inputs for warnings
    warnings: list[str] = []
    if change_pct is None:
        warnings.append("涨跌幅缺失：需 price 和 last_close")
    if ma5 is None and len(closes) < 5:
        warnings.append(f"MA5 不可用：仅 {len(closes)} 根 K 线（需 5）")
    if ma20 is None and len(closes) < 20:
        warnings.append(f"MA20 不可用：仅 {len(closes)} 根 K 线（需 20）")
    if return_20d is None and len(closes) <= 20:
        warnings.append(f"20日收益不可用：仅 {len(closes)} 根 K 线（需 21）")
    if volatility_20d is None and len(closes) < 21:
        warnings.append(f"20日波动率不可用：仅 {len(closes)} 根 K 线（需 21）")
    if drawdown_60d is None and len(closes) < 60:
        warnings.append(f"60日回撤不可用：仅 {len(closes)} 根 K 线（需 60）")
    if avg_price is None:
        has_amount = _first_number(quote.get("amount")) is not None
        has_vol = _first_number(quote.get("vol")) is not None
        if has_amount and has_vol:
            warnings.append("成交均价缺失：vol_unit 未标注（需明确 \"股\" 或 \"手\"）")
        else:
            warnings.append("成交均价缺失：需 amount（成交额）、vol（成交量）和 vol_unit（\"股\" 或 \"手\"）")

    meta["warnings"] = warnings

    return {
        "change_pct": change_pct,
        "change_amount": change_amount,
        "amplitude_pct": amplitude_pct,
        "avg_price": avg_price,
        "return_5d": return_5d,
        "return_20d": return_20d,
        "ma5": ma5,
        "ma20": ma20,
        "volatility_20d": volatility_20d,
        "drawdown_60d": drawdown_60d,
        "_meta": meta,
    }


# --- Provider normalization helpers (PR-LIVE-001) -------------------------
# Live hoxit providers may return pandas DataFrame-like objects or nested
# mappings instead of plain dict/list.  These helpers normalise at the
# collect_snapshot boundary so downstream analysis and rendering always
# receive stable types.


def _to_scalar(value: Any) -> Any:
    """Extract a scalar from a nested pandas-like structure.

    pandas ``.to_dict()`` may produce:
    - ``{0: 12.0}`` (single-row DataFrame)
    - ``{"2024Q1": 12.0, "2024Q2": 15.0}`` (period-indexed DataFrame)
    - ``[12.0]`` (single-element list/Series)

    This helper unwraps to a scalar so downstream consumers always get
    ``int | float | str | None``, never a nested container.
    """
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    if isinstance(value, dict):
        if not value:
            return None
        # Take the first value
        first = next(iter(value.values()))
        # Recurse in case of deeper nesting
        return _to_scalar(first)
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return None
        return _to_scalar(value[0])
    # pandas scalar types (numpy int64, float64, etc.)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_finance(result: Any) -> dict[str, Any]:
    """Normalise finance provider output to a stable dict with canonical field names.

    Steps:
    1. Convert DataFrame-like objects to plain dict (PR-LIVE-001).
    2. Map field aliases (Chinese, legacy, variant) to canonical names.
    3. Flatten nested pandas-like values to scalars.
    4. Preserve any extra fields not in the alias map.
    """
    # Step 1: DataFrame → dict
    if result is None:
        result = {}
    elif not isinstance(result, dict):
        if hasattr(result, "to_dict") and callable(result.to_dict):
            try:
                converted = result.to_dict()
                if isinstance(converted, dict):
                    result = converted
            except Exception:
                pass
        if not isinstance(result, dict) and hasattr(result, "__dict__"):
            result = dict(result.__dict__)
        if not isinstance(result, dict):
            return {}

    # Step 2: Alias normalization — copy to avoid mutating provider data
    out: dict[str, Any] = {}
    for key, value in result.items():
        canonical = _FINANCE_ALIASES.get(key, key)
        # First-wins: don't overwrite a canonical value with an alias
        if canonical not in out:
            # Step 3: Flatten nested pandas-like values
            out[canonical] = _to_scalar(value)
    return out


# Canonical finance field names and their aliases.
# Keys are canonical; values are lists of aliases that map TO that canonical name.
_FINANCE_ALIASES: dict[str, str] = {
    # ROE
    "ROE": "roe",
    "净资产收益率": "roe",
    "roe_ttm": "roe",
    # Net profit
    "净利润": "net_profit",
    "net_profit_ttm": "net_profit",
    "归母净利润": "net_profit",
    "归属于母公司所有者的净利润": "net_profit",
    # Revenue
    "营业收入": "revenue",
    "revenue_ttm": "revenue",
    "营业总收入": "revenue",
    # Gross margin
    "毛利率": "gross_margin",
    "gross_profit_margin": "gross_margin",
    "销售毛利率": "gross_margin",
    # Net margin
    "净利率": "net_margin",
    "net_profit_margin": "net_margin",
    "销售净利率": "net_margin",
    # Total assets
    "总资产": "total_assets",
    "assets": "total_assets",
    # Total equity
    "净资产": "total_equity",
    "股东权益": "total_equity",
    "股东权益合计": "total_equity",
    "equity": "total_equity",
    # Total shares
    "股本": "total_shares",
    "总股本": "total_shares",
    "shares": "total_shares",
    "share_count": "total_shares",
    # NIM (Net Interest Margin)
    "净息差": "nim",
    "net_interest_margin": "nim",
    # NPL ratio (Non-Performing Loan)
    "不良贷款率": "npl_ratio",
    "npl": "npl_ratio",
    "不良率": "npl_ratio",
    # Provision coverage
    "拨备覆盖率": "provision_coverage",
    "provision_coverage_ratio": "provision_coverage",
    # Capital adequacy
    "资本充足率": "capital_adequacy",
    "capital_adequacy_ratio": "capital_adequacy",
    "car": "capital_adequacy",
}


def _normalize_f10(f10: dict[str, Any], finance: dict[str, Any]) -> dict[str, Any]:
    """Extract finance fields from F10 sections and merge into finance dict.

    F10 may contain structured sections (e.g. ``{"sections": {"financial_summary": {...}}}``).
    This helper extracts known finance fields from those sections and merges them
    into the finance dict, preserving existing (direct provider) values.

    Returns the (possibly enriched) finance dict.
    """
    if not f10 or not isinstance(f10, dict):
        return finance

    sections = f10.get("sections")
    if not isinstance(sections, dict):
        return finance

    # Look for finance data in common F10 section names
    candidate_sections = [
        "financial_summary", "financial_highlights", "main_financial",
        "financial_indicator", "basic_financial",
    ]

    enriched = dict(finance)  # copy
    for section_name in candidate_sections:
        section = sections.get(section_name)
        if not isinstance(section, dict):
            continue
        normalized = _normalize_finance(section)
        for field in ("roe", "net_profit", "revenue", "gross_margin", "net_margin",
                       "total_assets", "total_equity", "total_shares"):
            if field not in enriched and field in normalized:
                enriched[field] = normalized[field]

    return enriched


# Finance fields tracked for field-level source quality.
_FINANCE_TRACKED_FIELDS = (
    "roe", "net_profit", "revenue", "gross_margin", "net_margin",
    "total_assets", "total_equity", "total_shares",
    # Bank-specific
    "nim", "npl_ratio", "provision_coverage", "capital_adequacy",
)


def _finance_field_quality(
    finance: dict[str, Any],
    f10: dict[str, Any],
    original_finance: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Evaluate field-level source quality for each tracked finance field.

    Args:
        finance: Merged finance dict (after F10 enrichment).
        f10: Raw F10 provider output.
        original_finance: Finance dict before F10 merge.  When provided,
            allows distinguishing provider.finance fields from f10 fields.

    Returns a dict mapping field name → quality record with:
    - status: "available" | "missing" | "unsupported"
    - source: which provider supplied the value ("provider.finance" | "f10")
    - warning: explanation when missing/unsupported
    """
    records: dict[str, dict[str, Any]] = {}
    f10_available = isinstance(f10, dict) and f10.get("status") != "unsupported"

    for field in _FINANCE_TRACKED_FIELDS:
        value = finance.get(field)
        if value is not None:
            # Determine which source supplied the value
            if original_finance is not None and field in original_finance:
                source = "provider.finance"
            else:
                source = "f10"
            records[field] = {
                "status": "available",
                "source": source,
                "warning": "",
            }
        elif f10_available:
            records[field] = {
                "status": "missing",
                "source": "provider.finance",
                "warning": f"{field} 不在 provider.finance 和 f10 中",
            }
        else:
            records[field] = {
                "status": "unsupported",
                "source": "provider.finance",
                "warning": f"{field} 缺失（f10 不可用）",
            }

    return records


def _normalize_concept(result: Any) -> list[dict]:
    """Normalise concept provider output to a list of ``{name: …}`` dicts.

    Live providers may return:
    - a list of ``{name: …}`` dicts (canonical)
    - a dict ``{total, boards, concept_tags}``
    """
    if not result:
        return []
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        tags = result.get("concept_tags") or []
        if tags:
            return [{"name": str(tag)} for tag in tags]
        boards = result.get("boards") or []
        if boards:
            return boards if isinstance(boards[0], dict) else [{"name": str(b)} for b in boards]
    return []


def _normalize_dragon_tiger(result: Any) -> list[dict]:
    """Normalise dragon-tiger provider output to a list of record dicts.

    Live providers may return:
    - a list of record dicts (canonical)
    - a dict ``{records, seats, institution}``
    """
    if not result:
        return []
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        records = result.get("records")
        if records is not None:
            return records if isinstance(records, list) else []
    return []


def _value_investor(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Value investor: low PE, reasonable PB, stable earnings."""
    valuation = snapshot["sources"].get("valuation", {})
    metrics = snapshot["sources"].get("metrics", {})
    finance = snapshot["sources"].get("finance", {})

    pe = _first_number(valuation.get("forward_pe"), metrics.get("pe_ttm"), metrics.get("pe"))
    pb = _first_number(metrics.get("pb"))
    roe = _first_number(finance.get("roe"))

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

    roe = _first_number(finance.get("roe"))
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


_BANK_INDUSTRY_KEYWORDS = ("银行", "bank", "商业银行", "城市银行", "农村银行")


def _is_bank_stock(snapshot: dict[str, Any]) -> bool:
    """Detect bank stocks from hoxit fundamentals/concept/industry fields."""
    fundamentals = snapshot.get("sources", {}).get("fundamentals", {})
    industry = str(fundamentals.get("industry", "")).lower()
    if any(kw in industry for kw in _BANK_INDUSTRY_KEYWORDS):
        return True
    # Check concept tags
    signals = snapshot.get("sources", {}).get("signals", {})
    concepts = signals.get("concept", [])
    for c in concepts:
        name = str(c.get("name", "")).lower()
        if any(kw in name for kw in _BANK_INDUSTRY_KEYWORDS):
            return True
    return False


def _bank_metrics_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Extract bank-specific metrics with quality status.

    Returns dict with fields: nim, npl_ratio, provision_coverage, capital_adequacy,
    plus data_needed list for missing fields.
    """
    finance = snapshot.get("sources", {}).get("finance", {})
    metrics: dict[str, Any] = {}
    data_needed: list[str] = []

    bank_fields = {
        "nim": "净息差 (NIM)",
        "npl_ratio": "不良贷款率 (NPL)",
        "provision_coverage": "拨备覆盖率",
        "capital_adequacy": "资本充足率",
    }

    for field, label in bank_fields.items():
        value = _first_number(finance.get(field))
        metrics[field] = value
        if value is None:
            data_needed.append(label)

    return {
        "is_bank": _is_bank_stock(snapshot),
        "metrics": metrics,
        "data_needed": data_needed,
    }


def _dcf_analysis(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute a light DCF analysis from snapshot data.

    Returns a dict with status, inputs, assumptions, intrinsic value, margin of safety,
    sensitivity table, and warnings. When data is insufficient, returns status="data_needed".

    For bank stocks, FCFF DCF is not the primary valuation model; a warning is added.
    """
    sources = snapshot.get("sources", {})
    quote = sources.get("quote", {})
    valuation = sources.get("valuation", {})
    metrics_data = sources.get("metrics", {})
    finance = sources.get("finance", {})

    is_bank = _is_bank_stock(snapshot)

    warnings: list[str] = []
    inputs: dict[str, Any] = {}
    assumptions: dict[str, Any] = {}

    # --- Bank stock DCF caveat ---
    if is_bank:
        warnings.append("银行股 FCFF DCF 不适用：银行现金流受资本充足率等监管约束，净利润折现仅作参考")

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
        metrics_data.get("total_shares"),
        metrics_data.get("share_count"),
        finance.get("total_shares"),
    )
    if share_count is None:
        warnings.append("总股本缺失")
    inputs["share_count"] = share_count

    # --- Extract growth rate from valuation or metrics ---
    growth_rate = _first_number(
        valuation.get("earnings_growth"),
        metrics_data.get("earnings_growth"),
        metrics_data.get("profit_growth"),
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
    "data_gap_acknowledged": {},
    "dimension_commentary": {},
    "panel_insights": "",
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
        "data_gap_acknowledged": {},
        "dimension_commentary": {},
        "panel_insights": "",
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

    # Deep review fields (Phase 5)
    if "data_gap_acknowledged" in raw:
        val = raw["data_gap_acknowledged"]
        if not isinstance(val, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in val.items()
        ):
            raise ValueError("agent_analysis.data_gap_acknowledged must be a dict[str, str]")
        envelope["data_gap_acknowledged"] = val

    if "dimension_commentary" in raw:
        val = raw["dimension_commentary"]
        if not isinstance(val, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in val.items()
        ):
            raise ValueError("agent_analysis.dimension_commentary must be a dict[str, str]")
        envelope["dimension_commentary"] = val

    if "panel_insights" in raw:
        val = raw["panel_insights"]
        if not isinstance(val, str):
            raise ValueError("agent_analysis.panel_insights must be a string")
        envelope["panel_insights"] = val

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

    # --- Phase 6: A-share coverage dimensions ---

    # Governance / ownership: governance source
    governance_sources = ["governance"]
    governance_quality = _dim_quality(governance_sources)
    governance_warnings = _dim_warnings(governance_sources)

    # Business / supply-chain: business source
    business_sources = ["business"]
    business_quality = _dim_quality(business_sources)
    business_warnings = _dim_warnings(business_sources)

    # Events / catalysts: event source
    event_sources = ["event"]
    event_quality = _dim_quality(event_sources)
    event_warnings = _dim_warnings(event_sources)

    # Policy / macro context: not yet implemented (no source)
    policy_status = "unsupported"
    policy_quality = "missing"
    policy_warnings = ["政策/宏观上下文检查尚未实现"]

    # Sentiment / social evidence boundary: not yet implemented (no source)
    sentiment_status = "unsupported"
    sentiment_quality = "missing"
    sentiment_warnings = ["社交情绪/舆情检查尚未实现"]

    # LHB detail coverage: dragon_tiger source (separate from lhb analysis)
    lhb_detail_sources = ["dragon_tiger"]
    lhb_detail_quality = _dim_quality(lhb_detail_sources)
    lhb_detail_warnings = _dim_warnings(lhb_detail_sources)

    # --- Deferred UZI dimensions (unsupported) ---

    # Materials / commodities: not yet implemented
    materials_status = "unsupported"
    materials_quality = "missing"
    materials_warnings = ["大宗商品/原材料数据尚未实现"]

    # Futures / derivatives: not yet implemented
    futures_status = "unsupported"
    futures_quality = "missing"
    futures_warnings = ["期货/衍生品数据尚未实现"]

    # Moat / patents: not yet implemented
    moat_status = "unsupported"
    moat_quality = "missing"
    moat_warnings = ["护城河/专利分析尚未实现"]

    # Contests / competitions: not yet implemented
    contest_status = "unsupported"
    contest_quality = "missing"
    contest_warnings = ["竞争格局分析尚未实现"]

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
        # --- Phase 6: A-share coverage dimensions ---
        "governance": {
            "status": "computed" if governance_quality == "full" else "partial",
            "quality": governance_quality,
            "inputs": governance_sources,
            "outputs": ["governance"],
            "warnings": governance_warnings,
        },
        "business": {
            "status": "computed" if business_quality == "full" else "partial",
            "quality": business_quality,
            "inputs": business_sources,
            "outputs": ["business"],
            "warnings": business_warnings,
        },
        "events": {
            "status": "computed" if event_quality == "full" else "partial",
            "quality": event_quality,
            "inputs": event_sources,
            "outputs": ["event"],
            "warnings": event_warnings,
        },
        "policy": {
            "status": policy_status,
            "quality": policy_quality,
            "inputs": [],
            "outputs": [],
            "warnings": policy_warnings,
        },
        "sentiment": {
            "status": sentiment_status,
            "quality": sentiment_quality,
            "inputs": [],
            "outputs": [],
            "warnings": sentiment_warnings,
        },
        "lhb_detail": {
            "status": "computed" if lhb_detail_quality == "full" else "partial",
            "quality": lhb_detail_quality,
            "inputs": lhb_detail_sources,
            "outputs": ["dragon_tiger"],
            "warnings": lhb_detail_warnings,
        },
        # --- Deferred UZI dimensions (unsupported) ---
        "materials": {
            "status": materials_status,
            "quality": materials_quality,
            "inputs": [],
            "outputs": [],
            "warnings": materials_warnings,
        },
        "futures": {
            "status": futures_status,
            "quality": futures_quality,
            "inputs": [],
            "outputs": [],
            "warnings": futures_warnings,
        },
        "moat": {
            "status": moat_status,
            "quality": moat_quality,
            "inputs": [],
            "outputs": [],
            "warnings": moat_warnings,
        },
        "contest": {
            "status": contest_status,
            "quality": contest_quality,
            "inputs": [],
            "outputs": [],
            "warnings": contest_warnings,
        },
    }


# ── Synthesis layer ─────────────────────────────────────────────────────────


def _synthesis_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Compute deterministic synthesis from existing analysis objects.

    Uses only: panel, market_risk, dcf, comps, lhb, dimensions, data_quality,
    and Phase 6 source summaries (governance, business, event).
    No LLM or agent-authored content.
    """
    analysis = snapshot.get("analysis", {})
    sources = snapshot.get("sources", {})
    panel = analysis.get("panel", {})
    market_risk = analysis.get("market_risk", {})
    dcf = analysis.get("dcf", {})
    comps = analysis.get("comps", {})
    lhb = analysis.get("lhb", {})
    dimensions = analysis.get("dimensions", {})
    data_quality = snapshot.get("data_quality", {})

    # Phase 6 source summaries
    governance = sources.get("governance", {})
    business = sources.get("business", {})
    event = sources.get("event", {})

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

    # --- Phase 6: Governance drivers/risks ---
    if governance.get("status") == "computed":
        controller = governance.get("actual_controller", "")
        if controller:
            drivers.append(f"实控人：{controller}")
        pledge = governance.get("pledge_ratio")
        if pledge is not None and pledge > 50:
            risks.append(f"股权质押比例偏高（{pledge}%）")

    # --- Phase 6: Business drivers ---
    if business.get("status") == "computed":
        segments = business.get("revenue_segments", [])
        if segments:
            top_segment = segments[0].get("name", "")
            if top_segment:
                drivers.append(f"主营构成：{top_segment}")

    # --- Phase 6: Event drivers/risks ---
    if event.get("status") == "computed":
        positive_count = event.get("positive_count", 0)
        negative_count = event.get("negative_count", 0)
        if positive_count > negative_count:
            drivers.append(f"近期正面事件 {positive_count} 条")
        elif negative_count > positive_count:
            risks.append(f"近期负面事件 {negative_count} 条")

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


# ── Report self-review ──────────────────────────────────────────────────────


def _report_review(
    snapshot: dict[str, Any],
    markdown: str,
    *,
    mode: str = "analyze-stock",
) -> dict[str, Any]:
    """Audit JSON and Markdown artifact contract deterministically.

    Non-blocking: status is "passed" or "warnings", never "failed".
    """
    analysis = snapshot.get("analysis", {})
    checks: list[dict[str, Any]] = []
    all_warnings: list[str] = []

    # --- Check 1: required analysis sections ---
    required_sections = ["panel", "market_risk", "dcf", "comps", "lhb", "dimensions", "synthesis"]
    missing = [s for s in required_sections if s not in analysis]
    section_check = {
        "name": "required_analysis_sections",
        "status": "passed" if not missing else "warnings",
        "warnings": [f"缺失分析模块：{s}" for s in missing],
    }
    checks.append(section_check)
    all_warnings.extend(section_check["warnings"])

    # --- Check 2: disclaimer presence ---
    has_disclaimer = "不构成投资建议" in markdown
    disclaimer_check = {
        "name": "disclaimer_present",
        "status": "passed" if has_disclaimer else "warnings",
        "warnings": [] if has_disclaimer else ["Markdown 缺少免责声明"],
    }
    checks.append(disclaimer_check)
    all_warnings.extend(disclaimer_check["warnings"])

    # --- Check 3: no raw dict repr in Markdown ---
    # Count `{` and `}` outside of code fences
    lines = markdown.split("\n")
    in_code = False
    raw_dict_lines: list[int] = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and "{" in line and "}" in line:
            raw_dict_lines.append(i)
    raw_dict_check = {
        "name": "no_raw_dict_repr",
        "status": "passed" if not raw_dict_lines else "warnings",
        "warnings": [] if not raw_dict_lines else [f"Markdown 第 {raw_dict_lines[0]} 行疑似原始 dict 表示"],
    }
    checks.append(raw_dict_check)
    all_warnings.extend(raw_dict_check["warnings"])

    # --- Check 4: mode section alignment ---
    expected_sections = _sections_for_mode(mode)
    # Check that key mode-specific sections appear in Markdown when expected
    section_markers = {
        "dcf": "## DCF 估值",
        "comps": "## 同业比较",
        "panel": "## 投资者面板",
        "market_risk": "## 市场数据风险检查",
        "trap_risk": "## 社交/操纵风险检查",
        "lhb": "## 龙虎榜分析",
        "synthesis": "## 综合研判",
    }
    alignment_warnings: list[str] = []
    for section_key, marker in section_markers.items():
        if section_key in expected_sections and marker not in markdown:
            alignment_warnings.append(f"模式 {mode} 期望包含 {marker} 但未找到")
    alignment_check = {
        "name": "mode_section_alignment",
        "status": "passed" if not alignment_warnings else "warnings",
        "warnings": alignment_warnings,
    }
    checks.append(alignment_check)
    all_warnings.extend(alignment_warnings)

    # --- Check 5: unsupported feature wording ---
    trap_risk = analysis.get("trap_risk", {})
    trap_warnings: list[str] = []
    if trap_risk.get("status") == "unsupported":
        if "尚未支持" not in markdown and "尚未实现" not in markdown:
            trap_warnings.append("trap_risk 状态为 unsupported 但 Markdown 未包含相应提示")
    unsupported_check = {
        "name": "unsupported_feature_wording",
        "status": "passed" if not trap_warnings else "warnings",
        "warnings": trap_warnings,
    }
    checks.append(unsupported_check)
    all_warnings.extend(trap_warnings)

    overall_status = "passed" if not all_warnings else "warnings"

    return {
        "status": overall_status,
        "checks": checks,
        "warnings": all_warnings,
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
    bars = snapshot["sources"].get("bars", [])

    # Validate agent_analysis if provided
    validated_agent = _empty_agent_analysis()
    if agent_analysis is not None:
        validated_agent = _validate_agent_analysis(agent_analysis)

    # Derive market metrics from quote + bars
    derived = _derive_market_metrics(quote, bars)

    snapshot["analysis"] = {
        "summary": {
            "name": quote.get("name") or fundamentals.get("name") or "",
            "price": quote.get("price"),
            "change_pct": derived["change_pct"],
            "change_amount": derived["change_amount"],
            "amplitude_pct": derived["amplitude_pct"],
            "avg_price": derived["avg_price"],
            "return_5d": derived["return_5d"],
            "return_20d": derived["return_20d"],
            "ma5": derived["ma5"],
            "ma20": derived["ma20"],
            "volatility_20d": derived["volatility_20d"],
            "drawdown_60d": derived["drawdown_60d"],
            "_meta": derived["_meta"],
        },
        "valuation": snapshot["sources"].get("valuation", {}),
        "industry": {"rows": snapshot["sources"].get("signals", {}).get("industry", [])},
        "panel": _panel_summary(snapshot),
        "bank_metrics": _bank_metrics_summary(snapshot),
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


def _compact_concepts(concepts: Any, max_items: int = 8) -> str:
    """Format concept list as comma-separated names."""
    if not concepts:
        return "暂无概念数据"
    if isinstance(concepts, dict):
        tags = concepts.get("concept_tags") or []
        if tags:
            names = [str(tag) for tag in tags[:max_items]]
            total = concepts.get("total") or len(tags)
        else:
            boards = concepts.get("boards") or []
            names = [str(c.get("name", "未知")) for c in boards[:max_items]]
            total = concepts.get("total") or len(boards)
    else:
        names = [c.get("name", "未知") for c in concepts[:max_items]]
        total = len(concepts)
    if not names:
        return "暂无概念数据"
    result = "、".join(names)
    if total > max_items:
        result += f"等 {total} 个概念"
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
    change_amount = _fmt_number(summary.get("change_amount"), "元")
    amplitude_pct = _fmt_pct(summary.get("amplitude_pct"))
    ma5 = _fmt_number(summary.get("ma5"), "元")
    ma20 = _fmt_number(summary.get("ma20"), "元")
    return_5d = _fmt_pct(summary.get("return_5d"))
    volatility_20d = _fmt_pct(summary.get("volatility_20d"))
    panel_verdict = panel.get("verdict", "neutral")
    panel_score = panel.get("score", 50)

    lines = [
        f"# UZEN A股分析：{snapshot['code']}",
        "",
        "## 核心结论",
        f"- 名称：{name}",
        f"- 最新价：{price}",
        f"- 涨跌幅：{change_pct}（变动 {change_amount}）",
        f"- 振幅：{amplitude_pct}",
        f"- MA5：{ma5}，MA20：{ma20}",
        f"- 5日收益：{return_5d}，20日波动率：{volatility_20d}",
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
        roe = _fmt_number(finance.get("roe"), "%")
        net_profit = _fmt_number(finance.get("net_profit"), "元")

        lines.extend([
            "",
            "## 基本面与财务",
            f"- 行业：{industry}",
            f"- ROE：{roe}",
            f"- 净利润：{net_profit}",
        ])

        # Bank-specific metrics
        bank = snapshot.get("analysis", {}).get("bank_metrics", {})
        if bank.get("is_bank"):
            bm = bank.get("metrics", {})
            nim = _fmt_number(bm.get("nim"), "%")
            npl = _fmt_number(bm.get("npl_ratio"), "%")
            prov_cov = _fmt_number(bm.get("provision_coverage"), "%")
            car = _fmt_number(bm.get("capital_adequacy"), "%")
            lines.extend([
                "",
                "### 银行专项指标",
                f"- 净息差 (NIM)：{nim}",
                f"- 不良贷款率 (NPL)：{npl}",
                f"- 拨备覆盖率：{prov_cov}",
                f"- 资本充足率：{car}",
            ])
            if bank.get("data_needed"):
                lines.append(f"- 缺失字段：{'、'.join(bank['data_needed'])}")

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

    # --- 治理与股权结构 ---
    if "governance" in sections:
        governance = sources.get("governance", {})
        gov_status = governance.get("status", "data_needed")
        lines.extend([
            "",
            "## 治理与股权结构",
        ])
        if gov_status == "computed":
            controller = governance.get("actual_controller", "")
            pledge = governance.get("pledge_ratio")
            exec_holding = governance.get("executive_holding")
            changes = governance.get("shareholder_changes", [])
            lines.append(f"- 实控人：{controller or '未知'}")
            if pledge is not None:
                lines.append(f"- 股权质押比例：{pledge}%")
            if exec_holding is not None:
                lines.append(f"- 高管持股比例：{exec_holding}%")
            if changes:
                lines.append(f"- 近期增减持：{len(changes)} 条")
        else:
            lines.append(f"- 状态：数据不足")

    # --- 经营与产业链 ---
    if "business" in sections:
        business = sources.get("business", {})
        biz_status = business.get("status", "data_needed")
        lines.extend([
            "",
            "## 经营与产业链",
        ])
        if biz_status == "computed":
            segments = business.get("revenue_segments", [])
            customer_conc = business.get("customer_concentration")
            supplier_conc = business.get("supplier_concentration")
            if segments:
                lines.append("- 主营构成：")
                for seg in segments[:3]:
                    name = seg.get("name", "")
                    ratio = seg.get("ratio")
                    ratio_str = f"（{ratio}%）" if ratio is not None else ""
                    lines.append(f"  - {name}{ratio_str}")
            if customer_conc is not None:
                lines.append(f"- 客户集中度：{customer_conc}%")
            if supplier_conc is not None:
                lines.append(f"- 供应商集中度：{supplier_conc}%")
        else:
            lines.append(f"- 状态：数据不足")

    # --- 事件与催化剂 ---
    if "events" in sections:
        event = sources.get("event", {})
        event_status = event.get("status", "data_needed")
        lines.extend([
            "",
            "## 事件与催化剂",
        ])
        if event_status == "computed":
            events = event.get("events", [])
            catalysts = event.get("catalysts", [])
            positive = event.get("positive_count", 0)
            negative = event.get("negative_count", 0)
            lines.append(f"- 近期事件：{len(events)} 条（正面 {positive}，负面 {negative}）")
            if catalysts:
                lines.append(f"- 催化剂：{'、'.join(catalysts[:3])}")
            if events:
                lines.append("- 最新事件：")
                for evt in events[:3]:
                    title = evt.get("title", "")
                    sentiment = evt.get("sentiment", "neutral")
                    label = {"positive": "↑", "negative": "↓", "neutral": "—"}.get(sentiment, "—")
                    lines.append(f"  - {label} {title}")
        else:
            lines.append(f"- 状态：数据不足")

    # --- 龙虎榜详情 ---
    if "lhb_detail" in sections:
        dragon_tiger = signals.get("dragon_tiger", [])
        dragon_tiger_records = dragon_tiger.get("records", []) if isinstance(dragon_tiger, dict) else dragon_tiger
        lines.extend([
            "",
            "## 龙虎榜详情",
            f"- 龙虎榜记录数：{len(dragon_tiger_records)}",
        ])
        if dragon_tiger_records:
            latest = dragon_tiger_records[0]
            reason = latest.get("reason", "")
            if reason:
                lines.append(f"- 最新上榜原因：{reason}")

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
        # Deep review fields (Phase 5)
        if agent.get("panel_insights"):
            lines.append(f"- 面板洞察：{agent['panel_insights']}")
        data_gaps = agent.get("data_gap_acknowledged", {})
        if data_gaps:
            lines.append("- 数据缺口确认：")
            for dim, note in data_gaps.items():
                lines.append(f"  - {dim}：{note}")
        dim_commentary = agent.get("dimension_commentary", {})
        if dim_commentary:
            lines.append("- 维度评注：")
            for dim, comment in dim_commentary.items():
                lines.append(f"  - {dim}：{comment}")

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
    snapshot["analysis"]["report_review"] = _report_review(snapshot, markdown, mode=mode)
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
