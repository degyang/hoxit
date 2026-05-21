from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from . import iwencai
from .utils import normalize_code

BAIDU_PAE_HEADERS = {
    "Host": "finance.pae.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0",
    "Accept": "application/vnd.finance-web.v1+json",
    "Origin": "https://gushitong.baidu.com",
    "Referer": "https://gushitong.baidu.com/",
}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


def eastmoney_datacenter(
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
    http_get: Callable | None = None,
) -> list[dict]:
    params = {
        "reportName": report_name,
        "columns": columns,
        "filter": filter_str,
        "pageNumber": "1",
        "pageSize": str(page_size),
        "sortColumns": sort_columns,
        "sortTypes": sort_types,
        "source": "WEB",
        "client": "WEB",
    }
    response = (http_get or _requests_get)(
        DATACENTER_URL,
        params=params,
        headers={"User-Agent": UA, "Referer": "https://data.eastmoney.com/"},
        timeout=15,
    )
    data = response.json()
    result = data.get("result") or {}
    return result.get("data") or []


def _is_st_stock(row: dict) -> bool:
    name = str(row.get("name") or row.get("名称") or "")
    return "ST" in name.upper() or "＊ST" in name.upper() or "*ST" in name.upper()


def ths_hot_reason(date: str | None = None, exclude_st: bool = False, http_get: Callable | None = None) -> list[dict]:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date}/orderby/date/orderway/desc/charset/GBK/"
    response = (http_get or _requests_get)(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = response.json()
    if data.get("errocode", 0) != 0:
        raise RuntimeError(f"同花顺热点错误: {data.get('errormsg', '')}")
    rows = data.get("data") or []
    if exclude_st:
        rows = [row for row in rows if not _is_st_stock(row)]
    return rows


def hsgt_realtime(http_get: Callable | None = None) -> list[dict]:
    response = (http_get or _requests_get)(
        "https://data.hexin.cn/market/hsgtApi/method/dayChart/",
        headers={"User-Agent": "Mozilla/5.0", "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"},
        timeout=10,
    )
    data = response.json()
    times = data.get("time", [])
    hgt = data.get("hgt", [])
    sgt = data.get("sgt", [])
    rows = []
    for index, value in enumerate(times):
        rows.append({
            "time": value,
            "hgt_yi": hgt[index] if index < len(hgt) else None,
            "sgt_yi": sgt[index] if index < len(sgt) else None,
        })
    return rows


def northbound_cache_path(base_dir: str | Path | None = None) -> Path:
    if base_dir is None:
        base = Path.home() / ".tradingagents" / "cache"
    else:
        base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    return base / "northbound_daily.csv"


def save_northbound_snapshot(date: str, hgt: float, sgt: float, base_dir: str | Path | None = None) -> Path:
    path = northbound_cache_path(base_dir)
    rows: dict[str, tuple[str, str]] = {}
    if path.exists():
        with path.open(newline="") as file:
            for row in csv.DictReader(file):
                rows[row["date"]] = (row["hgt"], row["sgt"])
    rows[date] = (str(hgt), str(sgt))
    with path.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["date", "hgt", "sgt"])
        for row_date in sorted(rows):
            writer.writerow([row_date, rows[row_date][0], rows[row_date][1]])
    return path


def load_northbound_history(n: int = 20, base_dir: str | Path | None = None) -> list[dict]:
    path = northbound_cache_path(base_dir)
    if not path.exists():
        return []
    with path.open(newline="") as file:
        rows = list(csv.DictReader(file))
    return rows[-n:]


def baidu_concept_blocks(code: str, http_get: Callable | None = None) -> dict:
    code = normalize_code(code)
    url = f"https://finance.pae.baidu.com/api/getrelatedblock?code={code}&market=ab&typeCode=all&finClientType=pc"
    data = (http_get or _requests_get)(url, headers=BAIDU_PAE_HEADERS, timeout=10).json()
    if str(data.get("ResultCode", -1)) != "0":
        raise RuntimeError(f"百度PAE错误: {data}")
    result = {"industry": [], "concept": [], "region": [], "concept_tags": []}
    for block in data.get("Result", []):
        block_type = block.get("type", "")
        for item in block.get("list", []):
            entry = {"name": item.get("name", ""), "change_pct": item.get("increase", ""), "desc": item.get("desc", "")}
            if "行业" in block_type:
                result["industry"].append(entry)
            elif "概念" in block_type:
                result["concept"].append(entry)
                result["concept_tags"].append(entry["name"])
            elif "地域" in block_type:
                result["region"].append(entry)
    return result


def eastmoney_fund_flow_minute(code: str, http_get: Callable | None = None) -> list[dict]:
    code = normalize_code(code)
    secid = f"1.{code}" if code.startswith(("6", "9")) else f"0.{code}"
    url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    params = {
        "secid": secid,
        "klt": 1,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/", "Origin": "https://quote.eastmoney.com"}
    data = {}
    for _ in range(2):
        try:
            data = (http_get or _requests_get)(url, params=params, headers=headers, timeout=10).json()
            break
        except Exception:
            data = {}
    rows = []
    for line in data.get("data", {}).get("klines", []) or []:
        parts = line.split(",")
        if len(parts) >= 6:
            rows.append({
                "time": parts[0],
                "main_net": float(parts[1]) if parts[1] != "-" else 0,
                "small_net": float(parts[2]) if parts[2] != "-" else 0,
                "mid_net": float(parts[3]) if parts[3] != "-" else 0,
                "large_net": float(parts[4]) if parts[4] != "-" else 0,
                "super_net": float(parts[5]) if parts[5] != "-" else 0,
            })
    return rows


def stock_fund_flow_120d(code: str, days: int = 120, http_get: Callable | None = None) -> list[dict]:
    code = normalize_code(code)
    secid = f"1.{code}" if code.startswith(("6", "9")) else f"0.{code}"
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "lmt": str(days),
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/", "Origin": "https://quote.eastmoney.com"}
    data = {}
    for _ in range(2):
        try:
            data = (http_get or _requests_get)(url, params=params, headers=headers, timeout=15).json()
            break
        except Exception:
            data = {}
    rows = []
    for line in data.get("data", {}).get("klines", []) or []:
        parts = line.split(",")
        if len(parts) >= 6:
            rows.append({
                "date": parts[0],
                "main_net": float(parts[1]) if parts[1] != "-" else 0,
                "small_net": float(parts[2]) if parts[2] != "-" else 0,
                "mid_net": float(parts[3]) if parts[3] != "-" else 0,
                "large_net": float(parts[4]) if parts[4] != "-" else 0,
                "super_net": float(parts[5]) if parts[5] != "-" else 0,
            })
    return rows[-days:]


def baidu_fund_flow_realtime(code: str, date: str, http_get: Callable | None = None) -> list[dict]:
    return eastmoney_fund_flow_minute(code, http_get=http_get)


def baidu_fund_flow_history(code: str, days: int = 20, http_get: Callable | None = None) -> list[dict]:
    return stock_fund_flow_120d(code, days=days, http_get=http_get)


def dragon_tiger_board(code: str, trade_date: str, look_back: int = 30, http_get: Callable | None = None, ak_module=None) -> dict:
    code = normalize_code(code)
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=look_back)
    start_str = start.strftime("%Y-%m-%d")
    records = []
    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=50,
        sort_columns="TRADE_DATE",
        sort_types="-1",
        http_get=http_get,
    )
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(float(row.get("TURNOVERRATE") or 0), 2),
        })

    seats = {"buy": [], "sell": []}
    buy_data: list[dict] = []
    sell_data: list[dict] = []
    if records:
        latest_date = records[0]["date"]
        buy_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10,
            sort_columns="BUY",
            sort_types="-1",
            http_get=http_get,
        )
        sell_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10,
            sort_columns="SELL",
            sort_types="-1",
            http_get=http_get,
        )
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })

    institution = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}
    for detail_data, side in ((buy_data, "buy"), (sell_data, "sell")):
        for row in detail_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                if side == "buy":
                    institution["buy_amt"] += row.get("BUY") or 0
                else:
                    institution["sell_amt"] += row.get("SELL") or 0
    institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
    institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
    institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)
    return {"records": records, "seats": seats, "institution": institution}


def lockup_expiry(code: str, trade_date: str, forward_days: int = 90, http_get: Callable | None = None, ak_module=None) -> dict:
    code = normalize_code(code)
    end_date = (datetime.strptime(trade_date, "%Y-%m-%d") + timedelta(days=forward_days)).strftime("%Y-%m-%d")
    history = []
    history_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=15,
        sort_columns="FREE_DATE",
        sort_types="-1",
        http_get=http_get,
    )
    for row in history_data:
        history.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("LIMITED_STOCK_TYPE", ""),
            "shares": row.get("FREE_SHARES_NUM", 0),
            "ratio": row.get("FREE_RATIO", 0),
        })

    upcoming = []
    upcoming_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{trade_date}')(FREE_DATE<='{end_date}')",
        page_size=20,
        sort_columns="FREE_DATE",
        sort_types="1",
        http_get=http_get,
    )
    for row in upcoming_data:
        upcoming.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("LIMITED_STOCK_TYPE", ""),
            "shares": row.get("FREE_SHARES_NUM", 0),
            "ratio": row.get("FREE_RATIO", 0),
        })
    return {"history": history, "upcoming": upcoming}


def industry_comparison(top_n: int = 20, http_get: Callable | None = None, ak_module=None) -> dict:
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "100",
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    data = (http_get or _requests_get)(url, params=params, headers={"User-Agent": UA}, timeout=15).json()
    items = data.get("data", {}).get("diff", []) or []
    if not items:
        return {"top": [], "bottom": [], "total": 0}
    rows = []
    for index, row in enumerate(items):
        rows.append({
            "rank": index + 1,
            "name": row.get("f14", ""),
            "change_pct": row.get("f3", 0),
            "code": row.get("f12", ""),
            "up_count": row.get("f104", 0),
            "down_count": row.get("f105", 0),
            "leader": row.get("f140", ""),
            "leader_change": row.get("f136", 0),
        })
    return {"top": rows[:top_n], "bottom": rows[-top_n:], "total": len(rows)}


def daily_dragon_tiger(trade_date: str | None = None, min_net_buy: float | None = None, http_get: Callable | None = None) -> dict:
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y-%m-%d")
    rows = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{trade_date}')(TRADE_DATE<='{trade_date}')",
        page_size=500,
        sort_columns="BILLBOARD_NET_AMT",
        sort_types="-1",
        http_get=http_get,
    )
    stocks = []
    for row in rows:
        net_buy = (row.get("BILLBOARD_NET_AMT") or 0) / 10000
        if min_net_buy is not None and net_buy < min_net_buy:
            continue
        stocks.append({
            "code": row.get("SECURITY_CODE", ""),
            "name": row.get("SECURITY_NAME_ABBR", ""),
            "reason": row.get("EXPLANATION", ""),
            "close": row.get("CLOSE_PRICE") or 0,
            "change_pct": round(float(row.get("CHANGE_RATE") or 0), 2),
            "net_buy_wan": round(net_buy, 1),
            "buy_wan": round((row.get("BILLBOARD_BUY_AMT") or 0) / 10000, 1),
            "sell_wan": round((row.get("BILLBOARD_SELL_AMT") or 0) / 10000, 1),
            "turnover_pct": round(float(row.get("TURNOVERRATE") or 0), 2),
        })
    actual_date = rows[0].get("TRADE_DATE", "")[:10] if rows else trade_date
    if stocks:
        return {"date": actual_date, "total_records": len(stocks), "stocks": stocks}

    try:
        fallback_rows = iwencai.query_rows("event", f"{actual_date} 龙虎榜 净买入额 排名 前5", limit="10")
    except Exception:
        fallback_rows = []
    fallback_stocks = []
    for row in fallback_rows:
        net_buy = row.get("净买入额") or row.get(f"净买入额[{actual_date.replace('-', '')}]") or 0
        if min_net_buy is not None and float(net_buy or 0) / 10000 < min_net_buy:
            continue
        buy_amt = row.get("买入额") or row.get(f"买入额[{actual_date.replace('-', '')}]") or 0
        sell_amt = row.get("卖出额") or row.get(f"卖出额[{actual_date.replace('-', '')}]") or 0
        turnover = row.get("换手率") or row.get(f"换手率[{actual_date.replace('-', '')}]") or 0
        fallback_stocks.append({
            "code": row.get("股票代码", ""),
            "name": row.get("股票简称", ""),
            "reason": row.get("上榜原因", row.get("原因", "")),
            "close": row.get("最新价", 0),
            "change_pct": float(row.get("最新涨跌幅", 0) or 0),
            "net_buy_wan": round(float(net_buy or 0) / 10000, 1),
            "buy_wan": round(float(buy_amt or 0) / 10000, 1),
            "sell_wan": round(float(sell_amt or 0) / 10000, 1),
            "turnover_pct": round(float(turnover or 0), 2),
        })
    return {"date": actual_date, "total_records": len(fallback_stocks), "stocks": fallback_stocks}


get_concept_blocks = baidu_concept_blocks
get_fund_flow = baidu_fund_flow_history
get_dragon_tiger_board = dragon_tiger_board
get_lockup_expiry = lockup_expiry
get_industry_comparison = industry_comparison
