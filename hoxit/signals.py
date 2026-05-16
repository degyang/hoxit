from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from .utils import iter_dates, normalize_code

BAIDU_PAE_HEADERS = {
    "Host": "finance.pae.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0",
    "Accept": "application/vnd.finance-web.v1+json",
    "Origin": "https://gushitong.baidu.com",
    "Referer": "https://gushitong.baidu.com/",
}


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


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


def baidu_fund_flow_realtime(code: str, date: str, http_get: Callable | None = None) -> list[dict]:
    code = normalize_code(code)
    url = f"https://finance.pae.baidu.com/vapi/v1/fundflow?code={code}&market=ab&date={date}&finClientType=pc"
    data = (http_get or _requests_get)(url, headers=BAIDU_PAE_HEADERS, timeout=10).json()
    if str(data.get("ResultCode", -1)) != "0":
        return []
    raw = data.get("Result", {}).get("update_data", "")
    rows = []
    for segment in raw.split(";"):
        parts = segment.split(",")
        if len(parts) >= 9:
            rows.append({
                "time": parts[0],
                "mainForce": float(parts[2]) if parts[2] else 0,
                "retail": float(parts[3]) if parts[3] else 0,
                "super": float(parts[4]) if parts[4] else 0,
                "large": float(parts[5]) if parts[5] else 0,
                "price": float(parts[8]) if parts[8] else 0,
            })
    return rows


def baidu_fund_flow_history(code: str, days: int = 20, http_get: Callable | None = None) -> list[dict]:
    code = normalize_code(code)
    url = f"https://finance.pae.baidu.com/vapi/v1/fundsortlist?code={code}&market=ab&pn=0&rn={days}&finClientType=pc"
    data = (http_get or _requests_get)(url, headers=BAIDU_PAE_HEADERS, timeout=10).json()
    if str(data.get("ResultCode", -1)) != "0":
        return []
    return [
        {
            "date": item.get("showtime", ""),
            "close": item.get("closepx", ""),
            "change_pct": item.get("ratio", ""),
            "superNetIn": item.get("superNetIn", ""),
            "largeNetIn": item.get("largeNetIn", ""),
            "mediumNetIn": item.get("mediumNetIn", ""),
            "littleNetIn": item.get("littleNetIn", ""),
            "mainIn": item.get("extMainIn", ""),
        }
        for item in data.get("Result", {}).get("list", [])
    ]


def dragon_tiger_board(code: str, trade_date: str, look_back: int = 30, ak_module=None) -> dict:
    code = normalize_code(code)
    ak = ak_module
    if ak is None:
        import akshare as ak
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=look_back)
    records = []
    try:
        df = ak.stock_lhb_detail_em(start_date=start.strftime("%Y%m%d"), end_date=trade_date.replace("-", ""))
        if not df.empty:
            for _, row in df[df["代码"] == code].iterrows():
                records.append({
                    "date": str(row.get("日期", "")),
                    "reason": row.get("解读", ""),
                    "net_buy": row.get("龙虎榜净买额", 0),
                    "turnover": row.get("换手率", 0),
                })
    except Exception:
        pass
    return {"records": records, "seats": {"buy": [], "sell": []}, "institution": {}}


def lockup_expiry(code: str, trade_date: str, forward_days: int = 90, ak_module=None) -> dict:
    code = normalize_code(code)
    ak = ak_module
    if ak is None:
        import akshare as ak
    history = []
    try:
        df = ak.stock_restricted_release_queue_em(symbol=code)
        if not df.empty:
            for _, row in df.head(15).iterrows():
                history.append({
                    "date": str(row.get("解禁时间", "")),
                    "type": row.get("限售股类型", ""),
                    "shares": row.get("解禁数量", 0),
                    "ratio": row.get("实际解禁市值占总市值比例", 0),
                })
    except Exception:
        pass
    end_date = (datetime.strptime(trade_date, "%Y-%m-%d") + timedelta(days=forward_days)).strftime("%Y-%m-%d")
    upcoming_by_key = {}
    for date_value in iter_dates(trade_date, end_date):
        try:
            df = ak.stock_restricted_release_detail_em(date=date_value.replace("-", ""))
        except Exception:
            continue
        if getattr(df, "empty", True):
            continue
        for _, row in df[df["股票代码"] == code].iterrows():
            key = (str(row.get("解禁日期", "")), row.get("限售股类型", ""), str(row.get("解禁数量", "")))
            upcoming_by_key[key] = {
                "date": str(row.get("解禁日期", "")),
                "type": row.get("限售股类型", ""),
                "shares": row.get("解禁数量", 0),
                "float_ratio": row.get("占流通股比例", 0),
            }
    return {"history": history, "upcoming": list(upcoming_by_key.values())}


def industry_comparison(top_n: int = 20, ak_module=None) -> dict:
    ak = ak_module
    if ak is None:
        import akshare as ak
    df = ak.stock_board_industry_summary_ths()
    if df.empty:
        return {"top": [], "bottom": [], "total": 0}
    rows = []
    for index, row in df.iterrows():
        rows.append({
            "rank": index + 1,
            "name": row.get("板块", ""),
            "change_pct": row.get("涨跌幅", 0),
            "turnover_yi": row.get("总成交额", 0),
            "net_inflow_yi": row.get("净流入", None) if "净流入" in df.columns else None,
            "up_count": row.get("上涨家数", 0),
            "down_count": row.get("下跌家数", 0),
            "leader": row.get("领涨股", ""),
        })
    return {"top": rows[:top_n], "bottom": rows[-top_n:], "total": len(rows)}


def daily_dragon_tiger(trade_date: str | None = None, min_net_buy: float | None = None, http_get: Callable | None = None) -> dict:
    if trade_date is None:
        trade_date = datetime.now().strftime("%Y-%m-%d")
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
        "columns": "ALL",
        "filter": f"(TRADE_DATE>='{trade_date}')(TRADE_DATE<='{trade_date}')",
        "pageNumber": "1",
        "pageSize": "500",
        "sortTypes": "-1",
        "sortColumns": "BILLBOARD_NET_AMT",
        "source": "WEB",
        "client": "WEB",
    }
    data = (http_get or _requests_get)(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
    rows = data.get("result", {}).get("data", []) if data.get("success") else []
    stocks = []
    for row in rows:
        net_buy = (row.get("BILLBOARD_NET_AMT") or 0) / 10000
        if min_net_buy is not None and net_buy < min_net_buy:
            continue
        stocks.append({"code": row.get("SECURITY_CODE", ""), "name": row.get("SECURITY_NAME_ABBR", ""), "reason": row.get("EXPLANATION", ""), "net_buy_wan": round(net_buy, 1)})
    actual_date = rows[0].get("TRADE_DATE", "")[:10] if rows else trade_date
    return {"date": actual_date, "total_records": len(stocks), "stocks": stocks}


get_concept_blocks = baidu_concept_blocks
get_fund_flow = baidu_fund_flow_history
get_dragon_tiger_board = dragon_tiger_board
get_lockup_expiry = lockup_expiry
get_industry_comparison = industry_comparison
