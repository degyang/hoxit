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


def governance_summary(code: str, http_post=None) -> dict:
    """股权结构与治理摘要 — 使用 iwencai management route。

    返回 dict 包含：实控人、股权质押、增减持等字段。
    数据不足时返回空值结构，不抛异常。
    """
    code = normalize_code(code)
    try:
        rows = iwencai.query_rows(
            "management",
            f"{code} 实际控制人 股权质押比例 股东增减持 高管持股",
            limit="5",
            http_post=http_post,
        )
    except Exception:
        rows = []

    if not rows:
        return {
            "code": code,
            "actual_controller": "",
            "pledge_ratio": None,
            "shareholder_changes": [],
            "executive_holding": None,
            "status": "data_needed",
            "warnings": ["治理数据不足"],
        }

    row = rows[0]
    return {
        "code": row.get("股票代码", code),
        "actual_controller": row.get("实际控制人") or row.get("实控人") or "",
        "pledge_ratio": _safe_float(row.get("股权质押比例") or row.get("质押比例")),
        "shareholder_changes": _extract_shareholder_changes(rows),
        "executive_holding": _safe_float(row.get("高管持股比例") or row.get("管理层持股比例")),
        "status": "computed",
        "warnings": [],
    }


def business_summary(code: str, http_post=None) -> dict:
    """经营与产业链摘要 — 使用 iwencai business route。

    返回 dict 包含：主营构成、客户/供应商集中度等字段。
    数据不足时返回空值结构，不抛异常。
    """
    code = normalize_code(code)
    try:
        rows = iwencai.query_rows(
            "business",
            f"{code} 主营业务收入构成 客户集中度 供应商集中度 前五大客户",
            limit="5",
            http_post=http_post,
        )
    except Exception:
        rows = []

    if not rows:
        return {
            "code": code,
            "revenue_segments": [],
            "customer_concentration": None,
            "supplier_concentration": None,
            "top_customers": [],
            "status": "data_needed",
            "warnings": ["经营数据不足"],
        }

    row = rows[0]
    return {
        "code": row.get("股票代码", code),
        "revenue_segments": _extract_revenue_segments(row),
        "customer_concentration": _safe_float(
            row.get("前五大客户销售占比") or row.get("客户集中度")
        ),
        "supplier_concentration": _safe_float(
            row.get("前五大供应商采购占比") or row.get("供应商集中度")
        ),
        "top_customers": _extract_top_items(row, "客户"),
        "status": "computed",
        "warnings": [],
    }


def _safe_float(value) -> float | None:
    """Try to convert value to float, return None on failure."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_shareholder_changes(rows: list[dict]) -> list[dict]:
    """Extract shareholder change records from iwencai rows."""
    changes = []
    for row in rows[:5]:
        name = row.get("股东名称") or row.get("变动人") or ""
        change_type = row.get("变动方向") or row.get("增减持") or ""
        shares = row.get("变动股数") or row.get("变动数量") or 0
        if name:
            changes.append({
                "name": str(name),
                "type": str(change_type),
                "shares": _safe_float(shares) or 0,
            })
    return changes


def _extract_revenue_segments(row: dict) -> list[dict]:
    """Extract revenue segment breakdown from iwencai row."""
    segments = []
    # Try structured fields
    for key in ("主营业务收入构成", "收入构成", "主营构成"):
        value = row.get(key)
        if isinstance(value, list):
            for item in value[:5]:
                if isinstance(item, dict):
                    segments.append({
                        "name": item.get("name") or item.get("项目") or str(item),
                        "revenue": _safe_float(item.get("revenue") or item.get("收入")),
                        "ratio": _safe_float(item.get("ratio") or item.get("占比")),
                    })
            break
        elif isinstance(value, str) and value:
            segments.append({"name": value, "revenue": None, "ratio": None})
            break
    return segments


def _extract_top_items(row: dict, keyword: str) -> list[str]:
    """Extract top-N items (customers/suppliers) from iwencai row."""
    items = []
    for key, value in row.items():
        if keyword in str(key) and isinstance(value, str) and value:
            items.append(value)
        elif keyword in str(key) and isinstance(value, list):
            items.extend(str(v) for v in value[:5])
    return items[:5]


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
