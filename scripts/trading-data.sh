#!/bin/bash
# trading-data.sh — hoxit 查询函数库（已验证字段名，无需每次试错）
# 用法: source trading-data.sh 2026-06-01 && q_indices | python3 scripts/trading-table.py indices
set -euo pipefail

HOXIT="${HOXIT:-$HOME/Projects/hoxit/.venv/bin/hoxit}"
TMPDIR="${TMPDIR:-/tmp/hoxit-data}"
mkdir -p "$TMPDIR"

DATE="${1:-$(TZ=Asia/Shanghai date '+%Y-%m-%d')}"
DATE_KEY="${DATE//-/}"

# ── 已验证字段名 ──
# 当日:  涨跌幅[$DATE_KEY]  成交额[$DATE_KEY]  资金净流入额[$DATE_KEY]  换手率[$DATE_KEY]  量比[$DATE_KEY]
# 日内:  开盘价_前复权[$DATE_KEY]  最高价_前复权[$DATE_KEY]  最低价_前复权[$DATE_KEY]
# ⚠️ 概念板块必须用 "概念板块" 关键词，不能用 "板块"（后者返回行业指数无数据字段）
# ⚠️ ETF 用 -r market 路由，返回字段是 基金简称/基金代码

# ── 指数 ──
q_indices() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r zhishu \
        -q "上证指数 深证成指 创业板指 涨跌幅 最新价 成交额 日期$DATE" \
        --limit "${1:-4}"
}

q_broad() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r zhishu \
        -q "上证50 沪深300 中证500 中证1000 科创50 涨跌幅 日期$DATE" \
        --limit "${1:-6}"
}

# ── 板块 ──
q_sectors_top() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r sector \
        -q "概念板块 涨跌幅 资金净流入 涨幅排名 日期$DATE" \
        --limit "${1:-10}"
}

q_sectors_down() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r sector \
        -q "概念板块 跌幅排名 涨跌幅 资金净流入 日期$DATE" \
        --limit "${1:-8}"
}

# ── 龙头/个股 ──
q_leaders() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r market \
        -q "成交额TOP${1:-10} 涨跌幅 资金流向 日期$DATE" \
        --limit "${1:-10}"
}

q_limit_down() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r market \
        -q "跌停 非ST 日期$DATE" \
        --limit 5 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('code_count',0))"
}

q_stocks() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r astock \
        -q "$1 最新价 涨跌幅 换手率 量比 市盈率 成交额 日期$DATE" \
        --limit "${2:-10}"
}

# ── ETF ──
q_etf() {
    TMPDIR="$TMPDIR" "$HOXIT" iwc query -r market \
        -q "ETF $1 涨跌幅 成交额 量比 日期$DATE" \
        --limit "${2:-15}"
}
