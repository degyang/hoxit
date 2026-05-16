from __future__ import annotations

import urllib.request
from typing import Callable

from .utils import normalize_code, prefixed_code, safe_float


def _mootdx_client():
    from mootdx.quotes import Quotes

    return Quotes.factory(market="std")


def _records_from_frame(value) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    if hasattr(value, "to_dict"):
        try:
            return value.to_dict("records")
        except TypeError:
            return [value.to_dict()]
    return []


def _normalize_mootdx_quote_rows(rows: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for row in rows:
        code = row.get("code") or row.get("symbol") or row.get("代码")
        if not code:
            continue
        code = normalize_code(str(code))
        result[code] = {
            "source": "mootdx",
            "code": code,
            "name": row.get("name") or row.get("名称", ""),
            "price": safe_float(row.get("price") if "price" in row else row.get("现价")),
            "open": safe_float(row.get("open") if "open" in row else row.get("今开")),
            "high": safe_float(row.get("high") if "high" in row else row.get("最高")),
            "low": safe_float(row.get("low") if "low" in row else row.get("最低")),
            "last_close": safe_float(row.get("last_close") if "last_close" in row else row.get("昨收")),
            "vol": safe_float(row.get("vol") if "vol" in row else row.get("成交量")),
            "amount": safe_float(row.get("amount") if "amount" in row else row.get("成交额")),
            "servertime": row.get("servertime") or row.get("time") or row.get("时间", ""),
            "raw": row,
        }
    return result


def parse_tencent_response(data: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for line in data.strip().split(";"):
        if not line.strip() or "=" not in line or '"' not in line:
            continue
        key = line.split("=", 1)[0].split("_")[-1]
        vals = line.split('"')[1].split("~")
        if len(vals) < 53:
            continue
        code = key[2:]
        result[code] = {
            "name": vals[1],
            "code": code,
            "price": safe_float(vals[3]),
            "last_close": safe_float(vals[4]),
            "open": safe_float(vals[5]),
            "change_amt": safe_float(vals[31]),
            "change_pct": safe_float(vals[32]),
            "high": safe_float(vals[33]),
            "low": safe_float(vals[34]),
            "amount_wan": safe_float(vals[37]),
            "turnover_pct": safe_float(vals[38]),
            "pe_ttm": safe_float(vals[39]),
            "amplitude_pct": safe_float(vals[43]),
            "mcap_yi": safe_float(vals[44]),
            "float_mcap_yi": safe_float(vals[45]),
            "pb": safe_float(vals[46]),
            "limit_up": safe_float(vals[47]),
            "limit_down": safe_float(vals[48]),
            "vol_ratio": safe_float(vals[49]),
            "pe_static": safe_float(vals[52]),
        }
    return result


def tencent_metrics(
    codes: list[str],
    urlopen: Callable | None = None,
    timeout: int = 10,
) -> dict[str, dict]:
    normalized = [normalize_code(code) for code in codes]
    url = "https://qt.gtimg.cn/q=" + ",".join(prefixed_code(code) for code in normalized)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    opener = urlopen or urllib.request.urlopen
    with opener(request, timeout=timeout) as response:
        data = response.read().decode("gbk")
    result = parse_tencent_response(data)
    for row in result.values():
        row["source"] = "tencent"
    return result


def mootdx_quote(
    codes: list[str],
    client=None,
    fallback: Callable[[list[str]], dict[str, dict]] | None = tencent_metrics,
) -> dict[str, dict]:
    normalized = [normalize_code(code) for code in codes]
    try:
        quote_client = client or _mootdx_client()
        rows = _records_from_frame(quote_client.quotes(symbol=normalized))
        result = _normalize_mootdx_quote_rows(rows)
        missing = [code for code in normalized if code not in result]
        if missing and fallback is not None:
            result.update(fallback(missing))
        return result
    except Exception:
        if fallback is None:
            raise
        return fallback(normalized)


def mootdx_bars(code: str, category: int = 4, offset: int = 10, client=None) -> list[dict]:
    quote_client = client or _mootdx_client()
    return _records_from_frame(quote_client.bars(symbol=normalize_code(code), category=category, offset=offset))


def mootdx_transactions(code: str, date: str, client=None) -> list[dict]:
    quote_client = client or _mootdx_client()
    return _records_from_frame(quote_client.transaction(symbol=normalize_code(code), date=date))


# Backward-compatible name. New code should use tencent_metrics for PE/PB/market-cap data.
tencent_quote = tencent_metrics
