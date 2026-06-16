from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from . import iwencai
from .utils import em_get, normalize_code

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
    response = (http_get or em_get)(
        DATACENTER_URL,
        params=params,
        headers={"Referer": "https://data.eastmoney.com/"},
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


def eastmoney_concept_blocks(code: str, http_get: Callable | None = None) -> dict:
    """
    个股所属板块/概念归属（东财 slist spt=3，V3.2.2 替换百度PAE）。

    东财把行业/概念/地域混在一个列表返回，板块名自解释。
    使用 em_get 限流，返回空时不抛异常（防住宅 IP 间歇风控）。

    返回: {total, boards: [{name, code(BK码), change_pct, lead_stock}], concept_tags: [板块名...]}
    """
    code = normalize_code(code)
    market_code = 1 if code.startswith("6") else 0
    params = {
        "fltt": "2", "invt": "2",
        "secid": f"{market_code}.{code}",
        "spt": "3", "pi": "0", "pz": "200", "po": "1",
        "fields": "f12,f14,f3,f128",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        d = (http_get or em_get)(
            "https://push2.eastmoney.com/api/qt/slist/get",
            params=params, headers=headers, timeout=15,
        ).json()
    except Exception:
        return {"total": 0, "boards": [], "concept_tags": []}
    diff = (d.get("data") or {}).get("diff") or {}
    items = diff.values() if isinstance(diff, dict) else diff
    boards = []
    for it in items:
        boards.append({
            "name": it.get("f14", ""),
            "code": it.get("f12", ""),
            "change_pct": it.get("f3", ""),
            "lead_stock": it.get("f128", ""),
        })
    return {
        "total": len(boards),
        "boards": boards,
        "concept_tags": [b["name"] for b in boards],
    }


# 向后兼容别名
baidu_concept_blocks = eastmoney_concept_blocks


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
            data = (http_get or em_get)(url, params=params, headers=headers, timeout=10).json()
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
            data = (http_get or em_get)(url, params=params, headers=headers, timeout=15).json()
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
    """行业横向对比 — 使用 iwencai 同花顺行业指数排名。

    当 iwencai 查询失败时回退到 eastmoney push2 API。
    """
    date_str = datetime.now().strftime("%Y%m%d")
    try:
        from . import iwencai

        top_rows = iwencai.query_rows(
            "industry",
            "同花顺行业指数 今日涨幅排名 上涨家数 下跌家数 领涨股 领涨股简称",
            limit=str(max(top_n, 30)),
        )
        bottom_rows = iwencai.query_rows(
            "industry",
            "同花顺行业指数 今日涨跌幅 从小到大 排名 上涨家数 下跌家数 领涨股 领涨股简称",
            limit=str(top_n),
        )
        if top_rows:
            def _build(row: dict, rank: int) -> dict:
                change_pct = row.get("涨跌幅[20260602]") or row.get("最新涨跌幅:前复权", 0)
                up_count = row.get(f"上涨家数[{date_str}]") or row.get("上涨家数", 0)
                down_count = row.get(f"下跌家数[{date_str}]") or row.get("下跌家数", 0)
                leader = row.get(f"领涨股简称[{date_str}]") or row.get("领涨股", "")
                code = row.get("指数代码", "")
                if code.endswith(".TI"):
                    code = code[:-3]
                return {
                    "rank": rank,
                    "name": row.get("指数简称", ""),
                    "change_pct": round(float(change_pct), 4) if change_pct else 0,
                    "code": code,
                    "up_count": int(up_count) if up_count else 0,
                    "down_count": int(down_count) if down_count else 0,
                    "leader": leader,
                }
            top_result = [_build(r, i + 1) for i, r in enumerate(top_rows[:top_n])]
            bottom_result = [_build(r, i + 1) for i, r in enumerate(bottom_rows[:top_n])]
            return {"top": top_result, "bottom": bottom_result, "total": len(top_rows)}
    except Exception:
        pass

    # Fallback: eastmoney push2 API (may fail under some network conditions)
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "fltt": "2", "invt": "2", "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    try:
        data = (http_get or em_get)(url, params=params, headers={"User-Agent": UA}, timeout=15).json()
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
    except Exception:
        return {"top": [], "bottom": [], "total": 0, "error": "行业数据获取失败（东财 push2 API 不可达）"}


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


# ── 资金面 / 筹码层（V3.0 新增，基于 eastmoney_datacenter） ──────────


def margin_trading(code: str, page_size: int = 30, http_get: Callable | None = None) -> list[dict]:
    """融资融券明细（日级）。
    返回: [{date, rzye(融资余额), rzmre(融资买入), rqye(融券余额), ...}]
    """
    data = eastmoney_datacenter(
        "RPTA_WEB_RZRQ_GGMX",
        filter_str=f'(SCODE="{normalize_code(code)}")',
        page_size=page_size,
        sort_columns="DATE", sort_types="-1",
        http_get=http_get,
    )
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("DATE", ""))[:10],
            "rzye": row.get("RZYE", 0),
            "rzmre": row.get("RZMRE", 0),
            "rzche": row.get("RZCHE", 0),
            "rqye": row.get("RQYE", 0),
            "rqmcl": row.get("RQMCL", 0),
            "rqchl": row.get("RQCHL", 0),
            "rzrqye": row.get("RZRQYE", 0),
        })
    return rows


def block_trade(code: str, page_size: int = 20, http_get: Callable | None = None) -> list[dict]:
    """大宗交易记录。
    返回: [{date, price, vol, amount, buyer, seller, premium_pct}]
    """
    data = eastmoney_datacenter(
        "RPT_DATA_BLOCKTRADE",
        filter_str=f'(SECURITY_CODE="{normalize_code(code)}")',
        page_size=page_size,
        sort_columns="TRADE_DATE", sort_types="-1",
        http_get=http_get,
    )
    rows = []
    for row in data:
        close = row.get("CLOSE_PRICE") or 0
        deal_price = row.get("DEAL_PRICE") or 0
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": row.get("DEAL_VOLUME", 0),
            "amount": row.get("DEAL_AMT", 0),
            "buyer": row.get("BUYER_NAME", ""),
            "seller": row.get("SELLER_NAME", ""),
        })
    return rows


def holder_num_change(code: str, page_size: int = 10, http_get: Callable | None = None) -> list[dict]:
    """股东户数变化（季度级）。
    返回: [{date, holder_num, change_num, change_ratio, avg_shares}]
    """
    data = eastmoney_datacenter(
        "RPT_HOLDERNUMLATEST",
        filter_str=f'(SECURITY_CODE="{normalize_code(code)}")',
        page_size=page_size,
        sort_columns="END_DATE", sort_types="-1",
        http_get=http_get,
    )
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("END_DATE", ""))[:10],
            "holder_num": row.get("HOLDER_NUM", 0),
            "change_num": row.get("HOLDER_NUM_CHANGE", 0),
            "change_ratio": row.get("HOLDER_NUM_RATIO", 0),
            "avg_shares": row.get("AVG_FREE_SHARES", 0),
        })
    return rows


def dividend_history(code: str, page_size: int = 20, http_get: Callable | None = None) -> list[dict]:
    """分红送转历史。
    返回: [{date, bonus_rmb(每股派息), transfer_ratio(转增比例), bonus_ratio(送股比例)}]
    """
    data = eastmoney_datacenter(
        "RPT_SHAREBONUS_DET",
        filter_str=f'(SECURITY_CODE="{normalize_code(code)}")',
        page_size=page_size,
        sort_columns="EX_DIVIDEND_DATE", sort_types="-1",
        http_get=http_get,
    )
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("EX_DIVIDEND_DATE", ""))[:10],
            "bonus_rmb": row.get("PRETAX_BONUS_RMB", 0),
            "transfer_ratio": row.get("TRANSFER_RATIO", 0),
            "bonus_ratio": row.get("BONUS_RATIO", 0),
            "plan": row.get("ASSIGN_PROGRESS", ""),
        })
    return rows


def event_summary(code: str, http_post=None) -> dict:
    """事件催化摘要 — 使用 iwencai event route。

    返回 dict 包含：近期事件、催化因子等字段。
    数据不足时返回空值结构，不抛异常。
    """
    code = normalize_code(code)
    try:
        rows = iwencai.query_rows(
            "event",
            f"{code} 近期事件 催化剂 公告 利好 利空",
            limit="10",
            http_post=http_post,
        )
    except Exception:
        rows = []

    if not rows:
        return {
            "code": code,
            "events": [],
            "catalysts": [],
            "positive_count": 0,
            "negative_count": 0,
            "status": "data_needed",
            "warnings": ["事件数据不足"],
        }

    events = _extract_events(rows)
    catalysts = _extract_catalysts(rows)
    positive = sum(1 for e in events if e.get("sentiment") == "positive")
    negative = sum(1 for e in events if e.get("sentiment") == "negative")

    return {
        "code": rows[0].get("股票代码", code),
        "events": events,
        "catalysts": catalysts,
        "positive_count": positive,
        "negative_count": negative,
        "status": "computed",
        "warnings": [],
    }


def _extract_events(rows: list[dict]) -> list[dict]:
    """Extract event records from iwencai rows."""
    events = []
    for row in rows[:10]:
        title = (
            row.get("事件标题")
            or row.get("公告标题")
            or row.get("事件内容")
            or row.get("标题")
            or ""
        )
        if not title:
            # Try to find any string value that looks like an event
            for key, value in row.items():
                if isinstance(value, str) and len(value) > 5 and "事件" not in key:
                    title = value
                    break
        if not title:
            continue

        date = (
            row.get("事件日期")
            or row.get("公告日期")
            or row.get("日期")
            or ""
        )
        sentiment = _classify_event_sentiment(title, row)
        events.append({
            "title": str(title)[:200],
            "date": str(date)[:10] if date else "",
            "type": str(row.get("事件类型") or row.get("类型") or ""),
            "sentiment": sentiment,
        })
    return events


def _extract_catalysts(rows: list[dict]) -> list[str]:
    """Extract catalyst keywords from iwencai rows."""
    catalysts = []
    for row in rows[:5]:
        catalyst = row.get("催化剂") or row.get("催化因素") or ""
        if catalyst and isinstance(catalyst, str):
            catalysts.append(catalyst)
        elif catalyst and isinstance(catalyst, list):
            catalysts.extend(str(c) for c in catalyst[:3])
    return list(dict.fromkeys(catalysts))[:5]  # dedupe, preserve order


def _classify_event_sentiment(title: str, row: dict) -> str:
    """Classify event sentiment based on keywords."""
    positive_keywords = ("利好", "增长", "突破", "创新高", "涨停", "增持", "回购", "中标", "签约", "合作")
    negative_keywords = ("利空", "下跌", "减持", "质押", "违规", "处罚", "亏损", "暴跌", "退市", "风险")

    # Check explicit sentiment field first
    explicit = row.get("情感") or row.get("sentiment") or ""
    if explicit in ("positive", "negative", "neutral"):
        return explicit

    title_lower = str(title).lower()
    if any(kw in title_lower for kw in positive_keywords):
        return "positive"
    if any(kw in title_lower for kw in negative_keywords):
        return "negative"
    return "neutral"


# ── 向后兼容别名 ──

get_concept_blocks = eastmoney_concept_blocks
get_fund_flow = baidu_fund_flow_history
get_dragon_tiger_board = dragon_tiger_board
get_lockup_expiry = lockup_expiry
get_industry_comparison = industry_comparison
