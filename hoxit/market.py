from __future__ import annotations

import socket
import urllib.request
from typing import Callable

from .utils import normalize_code, prefixed_code, safe_float


_TDX_SERVERS = [
    ("119.97.185.59", 7709),
    ("124.70.133.119", 7709),
    ("116.205.183.150", 7709),
    ("123.60.73.44", 7709),
    ("116.205.163.254", 7709),
    ("121.36.225.169", 7709),
    ("123.60.70.228", 7709),
    ("124.71.9.153", 7709),
    ("110.41.147.114", 7709),
    ("124.71.187.122", 7709),
]


def _probe_tdx_server(ip: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def tdx_client(market: str = "std", quotes_factory: Callable | None = None):
    """Create a mootdx client without relying on an empty BESTIP config."""
    from mootdx.quotes import Quotes

    factory = quotes_factory or Quotes.factory
    for ip, port in _TDX_SERVERS:
        if _probe_tdx_server(ip, port):
            return factory(market=market, server=(ip, port))
    try:
        return factory(market=market, bestip=True)
    except Exception:
        pass
    try:
        return factory(market=market)
    except Exception as exc:
        raise RuntimeError(
            "所有 mootdx 服务器均不可达；请检查 TCP 7709 网络、国内网络环境或更新 _TDX_SERVERS 列表。"
        ) from exc


def _mootdx_client():
    return tdx_client()


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


def _patch_mootdx_pandas_fillna_method() -> None:
    """Keep mootdx adjustment compatible with pandas 3.x."""
    try:
        from pandas.core.generic import NDFrame
    except Exception:
        return

    original = NDFrame.fillna
    if getattr(original, "_hoxit_mootdx_compat", False):
        return

    def fillna_compat(self, value=None, *args, **kwargs):
        method = kwargs.pop("method", None)
        if method == "ffill":
            return self.ffill(
                axis=kwargs.pop("axis", None),
                inplace=kwargs.pop("inplace", False),
                limit=kwargs.pop("limit", None),
            )
        if method == "bfill":
            return self.bfill(
                axis=kwargs.pop("axis", None),
                inplace=kwargs.pop("inplace", False),
                limit=kwargs.pop("limit", None),
            )
        return original(self, value, *args, **kwargs)

    fillna_compat._hoxit_mootdx_compat = True
    NDFrame.fillna = fillna_compat


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


def mootdx_bars(code: str, frequency: int = 9, offset: int = 10, client=None) -> list[dict]:
    """取 mootdx K 线数据。

    ⚠️ 参数名是 ``frequency``（不是 ``category``！传 ``category`` 会被 ``**kwargs``
    静默吞掉，永远退化成默认 frequency=9 日线，拿不到分钟数据）。

    mootdx 0.11.7 实测频率值表：
        0=5分钟  1=15分钟  2=30分钟  3=60分钟(1小时)  4=日线  5=周线  6=月线
        8=1分钟  9=日线(默认)  10=季线  11=年线  （7=1分钟除权口径，少用）

    ⚠️ 复权：bars 返回**不复权**原始价（通达信原始数据，无 adjust 参数）。
    跨除权除息日做估值/回测前需自行复权，或改用带前复权的日 K 数据源（腾讯财经）。
    """
    _patch_mootdx_pandas_fillna_method()
    quote_client = client or _mootdx_client()
    return _records_from_frame(quote_client.bars(
        symbol=normalize_code(code), frequency=frequency, offset=offset
    ))


def mootdx_transactions(code: str, date: str, client=None) -> list[dict]:
    quote_client = client or _mootdx_client()
    return _records_from_frame(quote_client.transaction(symbol=normalize_code(code), date=date))


# Backward-compatible name. New code should use tencent_metrics for PE/PB/market-cap data.
tencent_quote = tencent_metrics
