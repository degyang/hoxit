from __future__ import annotations

from . import iwencai
from .utils import em_get, normalize_code

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


def _first_iwencai_value(row: dict, names: tuple[str, ...], prefixes: tuple[str, ...] = ()):
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    for key, value in row.items():
        if value in (None, ""):
            continue
        normalized_key = str(key).lower()
        if any(normalized_key.startswith(prefix.lower()) for prefix in prefixes):
            return value
    return ""


def individual_info(code: str, http_get=None, ak_module=None):
    code = normalize_code(code)
    secid = f"1.{code}" if code.startswith(("6", "9")) else f"0.{code}"
    data = {}
    for _ in range(2):
        try:
            data = (http_get or em_get)(
                "https://push2.eastmoney.com/api/qt/stock/get",
                params={
                    "fltt": "2",
                    "invt": "2",
                    "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
                    "secid": secid,
                },
                headers={"Referer": "https://quote.eastmoney.com/", "Origin": "https://quote.eastmoney.com"},
                timeout=10,
            ).json().get("data", {}) or {}
            break
        except Exception:
            data = {}
    result = {
        "code": data.get("f57", ""),
        "name": data.get("f58", ""),
        "industry": data.get("f127", ""),
        "total_shares": data.get("f84", 0),
        "float_shares": data.get("f85", 0),
        "mcap": data.get("f116", 0),
        "float_mcap": data.get("f117", 0),
        "list_date": str(data.get("f189", "")),
        "price": data.get("f43", 0),
    }
    if result["code"]:
        return result

    try:
        rows = iwencai.query_rows("basicinfo", f"{code} 公司基本资料 行业 总股本 上市日期", limit="5")
    except Exception:
        rows = []
    if not rows:
        return result
    row = rows[0]
    industry = row.get("所属同花顺行业") or row.get("所属行业") or row.get("行业") or ""
    if isinstance(industry, list):
        industry = " / ".join(str(item) for item in industry if item)
    total_shares = _first_iwencai_value(
        row,
        ("总股本", "总股本[最新]"),
        ("总股本[",),
    ) or 0
    float_shares = _first_iwencai_value(
        row,
        ("流通a股", "流通A股", "流通股", "流通股本", "流通A股[最新]", "流通股本[最新]"),
        ("流通a股[", "流通A股[", "流通股[", "流通股本["),
    ) or 0
    list_date = _first_iwencai_value(
        row,
        ("上市日期", "上市日期[最新]"),
        ("上市日期[",),
    )
    return {
        "code": row.get("股票代码", code),
        "name": row.get("股票简称", ""),
        "industry": industry,
        "total_shares": total_shares,
        "float_shares": float_shares,
        "mcap": row.get("最新a股流通市值", 0) or row.get("总市值", 0),
        "float_mcap": row.get("最新a股流通市值", 0) or row.get("流通市值", 0),
        "list_date": str(list_date),
        "price": row.get("最新价", 0),
    }


def finance_snapshot(code: str, client=None):
    code = normalize_code(code)
    if client is None:
        from mootdx.quotes import Quotes

        client = Quotes.factory(market="std")
    return client.finance(symbol=code)


def f10(code: str, client=None):
    code = normalize_code(code)
    if client is None:
        from mootdx.quotes import Quotes

        client = Quotes.factory(market="std")
    if hasattr(client, "f10"):
        return client.f10(symbol=code)
    return {
        "code": code,
        "source": "mootdx",
        "status": "unsupported",
        "sections": {},
        "warnings": [
            "mootdx client does not expose f10(); use fundamentals info, finance snapshot, filings cninfo, reports eastmoney, and iwc query as substitutes"
        ],
    }
