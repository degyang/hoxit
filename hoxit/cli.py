from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime

from . import __version__


def _print_json(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _rows_from_output(data) -> list[dict]:
    if isinstance(data, dict):
        values = list(data.values())
        return [row for row in values if isinstance(row, dict)]
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def _print_csv(data) -> None:
    rows = _rows_from_output(data)
    if not rows:
        return
    excluded = {"raw"}
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key in excluded:
                continue
            if key not in fields:
                fields.append(key)
    writer = csv.DictWriter(sys.stdout, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)


def _positive_int_string(value: str) -> str:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("必须是正整数") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("必须是正整数")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hoxit", description="A-share data toolkit")
    parser.add_argument("--version", action="version", version=f"hoxit {__version__}")
    subparsers = parser.add_subparsers(dest="layer", required=True)

    market = subparsers.add_parser("market", help="行情层")
    market_sub = market.add_subparsers(dest="action", required=True)
    quote = market_sub.add_parser("quote", help="mootdx 实时行情，腾讯仅作 fallback")
    quote.add_argument("codes", nargs="+")
    quote.add_argument("--format", choices=["csv", "json"], default="csv")
    metrics = market_sub.add_parser("metrics", help="腾讯估值指标 PE/PB/市值/换手率/涨跌停")
    metrics.add_argument("codes", nargs="+")
    bars = market_sub.add_parser("bars", help="mootdx K线")
    bars.add_argument("code")
    bars.add_argument("--category", type=int, default=4)
    bars.add_argument("--offset", type=int, default=10)
    bars.add_argument("--adjust", choices=["raw", "qfq", "hfq"], default="raw", help="复权口径：raw=不复权，qfq=前复权，hfq=后复权")
    transactions = market_sub.add_parser("transactions", help="mootdx 逐笔成交")
    transactions.add_argument("code")
    transactions.add_argument("--date", required=True)

    reports = subparsers.add_parser("reports", help="研报层")
    reports_sub = reports.add_subparsers(dest="action", required=True)
    em = reports_sub.add_parser("eastmoney", help="东财研报列表")
    em.add_argument("code")
    em.add_argument("--max-pages", type=int, default=5)
    iw = reports_sub.add_parser("iwencai", help="iwencai 语义搜索")
    iw.add_argument("query")
    iw.add_argument("--channel", default="report")
    iw.add_argument("--size", type=int, default=50)

    news = subparsers.add_parser("news", help="新闻层")
    news_sub = news.add_subparsers(dest="action", required=True)
    ns = news_sub.add_parser("stock", help="个股新闻")
    ns.add_argument("code")
    news_sub.add_parser("cls", help="财联社快讯（新版签名接口）")
    news_sub.add_parser("global", help="东财全球资讯")

    fundamentals = subparsers.add_parser("fundamentals", help="基础数据层")
    fundamentals_sub = fundamentals.add_subparsers(dest="action", required=True)
    info = fundamentals_sub.add_parser("info", help="个股基本面")
    info.add_argument("code")
    finance = fundamentals_sub.add_parser("finance", help="mootdx 财务快照")
    finance.add_argument("code")
    f10_parser = fundamentals_sub.add_parser("f10", help="mootdx F10")
    f10_parser.add_argument("code")

    filings = subparsers.add_parser("filings", help="公告层")
    filings_sub = filings.add_subparsers(dest="action", required=True)
    cninfo = filings_sub.add_parser("cninfo", help="巨潮公告")
    cninfo.add_argument("code")
    cninfo.add_argument("--start-date", required=True)
    cninfo.add_argument("--end-date", required=True)

    signals = subparsers.add_parser("signals", help="信号层")
    signals_sub = signals.add_subparsers(dest="action", required=True)
    hot = signals_sub.add_parser("hot", help="同花顺热点")
    hot.add_argument("--date")
    hot.add_argument("--exclude-st", action="store_true", help="过滤 ST/*ST 股票")
    north = signals_sub.add_parser("northbound", help="北向实时")
    north.add_argument("--cache-dir")
    north.add_argument("--date")
    concept = signals_sub.add_parser("concept", help="东财概念板块")
    concept.add_argument("code")
    flow = signals_sub.add_parser("fund-flow", help="东财 push2his 个股资金流历史")
    flow.add_argument("code")
    flow.add_argument("--days", type=int, default=20)
    dt = signals_sub.add_parser("dragon-tiger", help="个股龙虎榜")
    dt.add_argument("code")
    dt.add_argument("--trade-date", required=True)
    lockup = signals_sub.add_parser("lockup", help="限售解禁")
    lockup.add_argument("code")
    lockup.add_argument("--trade-date", required=True)
    lockup.add_argument("--forward-days", type=int, default=90)
    industry = signals_sub.add_parser("industry", help="行业横向对比")
    industry.add_argument("--top-n", type=int, default=20)
    daily = signals_sub.add_parser("daily-dragon-tiger", help="全市场龙虎榜")
    daily.add_argument("--trade-date")
    daily.add_argument("--min-net-buy", type=float)
    margin = signals_sub.add_parser("margin-trading", help="融资融券明细")
    margin.add_argument("code")
    margin.add_argument("--page-size", type=int, default=30)
    bt = signals_sub.add_parser("block-trade", help="大宗交易")
    bt.add_argument("code")
    bt.add_argument("--page-size", type=int, default=20)
    hnc = signals_sub.add_parser("holder-num", help="股东户数变化")
    hnc.add_argument("code")
    hnc.add_argument("--page-size", type=int, default=10)
    dh = signals_sub.add_parser("dividend", help="分红送转历史")
    dh.add_argument("code")
    dh.add_argument("--page-size", type=int, default=20)

    valuation = subparsers.add_parser("valuation", help="估值流程")
    valuation_sub = valuation.add_subparsers(dest="action", required=True)
    full = valuation_sub.add_parser("full", help="单票完整估值")
    full.add_argument("code")

    iwc = subparsers.add_parser("iwc", help="iwencai 统一查询接口")
    iwc_sub = iwc.add_subparsers(dest="action", required=True)

    iwc_routes = iwc_sub.add_parser("routes", help="列出可用 iwencai routes")
    iwc_routes.add_argument("--kind", choices=["query2data", "comprehensive_search"], help="按接口类型过滤")

    iwc_query = iwc_sub.add_parser("query", help="query2data 条件查询（17 条 route）")
    iwc_query.add_argument("--route", "-r", required=True, help="route 名称（如 market/basicinfo/finance 等）")
    iwc_query.add_argument("--query", "-q", required=True, help="自然语言查询条件")
    iwc_query.add_argument("--page", default="1", type=_positive_int_string, help="页码（默认 1）")
    iwc_query.add_argument("--limit", default="10", type=_positive_int_string, help="每页条数（默认 10）")
    iwc_query.add_argument("--api-key", help="API key（默认取 $IWENCAI_API_KEY）")
    iwc_query.add_argument("--call-type", choices=["normal", "retry"], default="normal")
    iwc_query.add_argument("--timeout", type=int, default=30)
    iwc_query.add_argument("--raw", action="store_true", help="直接输出 gateway 原始响应")

    iwc_search = iwc_sub.add_parser("search", help="公告/研报语义搜索（2 条 route）")
    iwc_search.add_argument("--route", "-r", required=True, help="route 名称（announcement/report）")
    iwc_search.add_argument("--query", "-q", required=True, help="搜索关键词")
    iwc_search.add_argument("--api-key", help="API key（默认取 $IWENCAI_API_KEY）")
    iwc_search.add_argument("--call-type", choices=["normal", "retry"], default="normal")
    iwc_search.add_argument("--timeout", type=int, default=30)

    return parser


def run(args: argparse.Namespace):
    if args.layer == "market" and args.action == "quote":
        from .market import mootdx_quote

        return mootdx_quote(args.codes)
    if args.layer == "market" and args.action == "metrics":
        from .market import tencent_metrics

        return tencent_metrics(args.codes)
    if args.layer == "market" and args.action == "bars":
        from .market import mootdx_bars

        return mootdx_bars(args.code, category=args.category, offset=args.offset, adjust=args.adjust)
    if args.layer == "market" and args.action == "transactions":
        from .market import mootdx_transactions

        return mootdx_transactions(args.code, date=args.date)
    if args.layer == "reports" and args.action == "eastmoney":
        from .reports import eastmoney_reports

        return eastmoney_reports(args.code, max_pages=args.max_pages)
    if args.layer == "reports" and args.action == "iwencai":
        from .reports import iwencai_search

        return iwencai_search(args.query, channel=args.channel, size=args.size)
    if args.layer == "news":
        from . import news

        return {"stock": news.stock_news, "cls": news.cls_flash, "global": news.global_news}[args.action](
            *([args.code] if args.action == "stock" else [])
        )
    if args.layer == "fundamentals":
        from . import fundamentals

        return {"info": fundamentals.individual_info, "finance": fundamentals.finance_snapshot, "f10": fundamentals.f10}[args.action](args.code)
    if args.layer == "filings" and args.action == "cninfo":
        from .filings import cninfo_reports

        return cninfo_reports(args.code, start_date=args.start_date, end_date=args.end_date)
    if args.layer == "signals":
        from . import signals

        if args.action == "hot":
            return signals.ths_hot_reason(args.date, exclude_st=args.exclude_st)
        if args.action == "northbound":
            rows = signals.hsgt_realtime()
            if args.cache_dir and rows:
                last = next((row for row in reversed(rows) if row["hgt_yi"] is not None and row["sgt_yi"] is not None), None)
                if last:
                    snapshot_date = args.date or datetime.now().strftime("%Y-%m-%d")
                    signals.save_northbound_snapshot(snapshot_date, last["hgt_yi"], last["sgt_yi"], args.cache_dir)
            return rows
        if args.action == "concept":
            return signals.baidu_concept_blocks(args.code)
        if args.action == "fund-flow":
            return signals.baidu_fund_flow_history(args.code, days=args.days)
        if args.action == "dragon-tiger":
            return signals.dragon_tiger_board(args.code, args.trade_date)
        if args.action == "lockup":
            return signals.lockup_expiry(args.code, args.trade_date, forward_days=args.forward_days)
        if args.action == "industry":
            return signals.industry_comparison(args.top_n)
        if args.action == "daily-dragon-tiger":
            return signals.daily_dragon_tiger(args.trade_date, args.min_net_buy)
        if args.action == "margin-trading":
            return signals.margin_trading(args.code, page_size=args.page_size)
        if args.action == "block-trade":
            return signals.block_trade(args.code, page_size=args.page_size)
        if args.action == "holder-num":
            return signals.holder_num_change(args.code, page_size=args.page_size)
        if args.action == "dividend":
            return signals.dividend_history(args.code, page_size=args.page_size)
    if args.layer == "iwc":
        from . import iwencai

        if args.action == "routes":
            routes = iwencai.load_routes()
            result = []
            for key, route in sorted(routes.items()):
                if args.kind and route.kind != args.kind:
                    continue
                result.append({
                    "route": key,
                    "kind": route.kind,
                    "skill_id": route.skill_id,
                    "version": route.version,
                    "channels": list(route.channels),
                    "description": route.description,
                })
            return result

        route = iwencai.get_route(args.route)

        if args.action == "query":
            if route.kind != "query2data":
                raise SystemExit(f"--route {args.route!r} 是 {route.kind}，不是 query2data")
            response = iwencai.query2data(
                route=route,
                query=args.query,
                page=args.page,
                limit=args.limit,
                api_key=args.api_key,
                call_type=args.call_type,
                timeout=args.timeout,
            )
            if args.raw:
                return response
            return iwencai.summarize_query2data_response(
                response, query=args.query, page=args.page, limit=args.limit
            )

        if args.action == "search":
            if route.kind != "comprehensive_search":
                raise SystemExit(f"--route {args.route!r} 是 {route.kind}，不是 comprehensive_search")
            return iwencai.comprehensive_search(
                route=route,
                query=args.query,
                api_key=args.api_key,
                call_type=args.call_type,
                timeout=args.timeout,
            )

        raise SystemExit(f"不支持的命令: iwc {args.action}")
    if args.layer == "valuation" and args.action == "full":
        from .valuation import full_valuation

        return full_valuation(args.code)
    raise SystemExit("unsupported command")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
        if args.layer == "market" and args.action == "quote" and args.format == "csv":
            _print_csv(result)
        else:
            _print_json(result)
    except Exception as exc:
        print(f"hoxit: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
