from __future__ import annotations

import math
from typing import Callable

from .market import tencent_metrics
from .utils import normalize_code


def forward_pe(price: float, eps_forecast: float) -> float:
    if eps_forecast <= 0:
        return float("inf")
    return price / eps_forecast


def pe_digestion(current_pe: float, cagr: float, target_pe: float = 30) -> float:
    if current_pe <= target_pe:
        return 0.0
    if cagr <= 0:
        return float("inf")
    return math.log(current_pe / target_pe) / math.log(1 + cagr)


def calc_peg(pe: float, cagr: float) -> float:
    if cagr <= 0:
        return float("inf")
    return pe / (cagr * 100)


def ths_eps_forecast(code: str):
    import pandas as pd
    import requests

    url = f"https://basic.10jqka.com.cn/new/{normalize_code(code)}/worth.html"
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Referer": "https://basic.10jqka.com.cn/",
        },
        timeout=15,
    )
    response.encoding = "gbk"
    tables = pd.read_html(response.text)
    for table in tables:
        columns = [str(column) for column in table.columns]
        if any("每股收益" in column or "均值" in column for column in columns):
            return table
    return tables[0] if tables else pd.DataFrame()


def _extract_eps_forecast(forecast) -> tuple[float | None, float | None, int]:
    if forecast is None or getattr(forecast, "empty", False):
        return None, None, 0
    if "年度" not in forecast or "均值" not in forecast:
        return None, None, 0
    years = sorted(str(year) for year in forecast["年度"].dropna().unique())
    eps_cur = eps_next = None
    analyst_count = 0
    try:
        import pandas as pd
        for _, row in forecast.iterrows():
            year = str(row.get("年度", ""))
            if years and year == years[0]:
                v = row.get("均值")
                eps_cur = float(v) if pd.notna(v) else None
                cnt = row.get("预测机构数", 0)
                analyst_count = int(cnt) if pd.notna(cnt) else 0
            elif len(years) > 1 and year == years[1]:
                v = row.get("均值")
                eps_next = float(v) if pd.notna(v) else None
    except (ValueError, TypeError) as e:
        print(f"[WARN] full_valuation EPS 解析失败({e})，估值可能不完整")
    return eps_cur, eps_next, analyst_count


def full_valuation(
    code: str,
    quote_provider: Callable[[list[str]], dict[str, dict]] = tencent_metrics,
    forecast_provider: Callable[[str], object] = ths_eps_forecast,
) -> dict:
    code = normalize_code(code)
    quotes = quote_provider([code])
    if code not in quotes:
        raise RuntimeError(f"quote not found for {code}")
    quote = quotes[code]

    try:
        forecast = forecast_provider(code)
    except Exception:
        forecast = None
    eps_cur, eps_next, analyst_count = _extract_eps_forecast(forecast)

    pe_fwd = forward_pe(quote["price"], eps_cur) if eps_cur else float("inf")
    cagr = (eps_next / eps_cur - 1) if eps_cur and eps_next else 0
    peg = calc_peg(pe_fwd, cagr)
    digest = pe_digestion(pe_fwd, cagr)

    return {
        **quote,
        "eps_cur": eps_cur,
        "eps_next": eps_next,
        "pe_fwd": round(pe_fwd, 1) if math.isfinite(pe_fwd) else None,
        "cagr_pct": round(cagr * 100, 0) if cagr else None,
        "peg": round(peg, 2) if math.isfinite(peg) else None,
        "digest_years": round(digest, 1) if math.isfinite(digest) else None,
        "analyst_count": analyst_count,
    }
