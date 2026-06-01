#!/usr/bin/env python3
"""trading-table.py — hoxit JSON → Markdown 表格（零试错，一键输出）

用法:
  source scripts/trading-data.sh 2026-06-01
  q_indices | python3 scripts/trading-table.py indices
  q_broad | python3 scripts/trading-table.py broad
  q_sectors_top | python3 scripts/trading-table.py sectors
  q_leaders 10 | python3 scripts/trading-table.py leaders
  q_etf "软件" | python3 scripts/trading-table.py etf
  q_stocks "煤炭" | python3 scripts/trading-table.py stocks
"""
import json, sys
from datetime import datetime

DATE = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')
DATE_KEY = DATE.replace('-', '')
MODE = sys.argv[1] if len(sys.argv) > 1 else 'indices'

def read():
    try: return json.load(sys.stdin)
    except: return {'datas': []}

def arrow(v, t=0.1):
    if v is None: return '➡️'
    if v > t: return '🔺'
    if v < -t: return '🔻'
    return '➡️'

def amt(v):
    if v is None: return '—'
    v = float(v)
    if abs(v) >= 1e8: return f'{v/1e8:.0f}亿'
    if abs(v) >= 1e4: return f'{v/1e4:.0f}万'
    return f'{v:.0f}'

def pct(v):
    if v is None: return '—'
    return f'{float(v):+.2f}%'

def field(d, *keys):
    for k in keys:
        v = d.get(k)
        if v is not None: return v
    return None

# ── 输出模式 ──

def mode_indices():
    data = read()
    rows = []
    for i in data.get('datas',[]):
        if not i: continue
        nm = i.get('指数简称','?')
        px = i.get('最新价','?')
        c = field(i, f'涨跌幅[{DATE_KEY}]')
        a = field(i, f'成交额[{DATE_KEY}]')
        rows.append(f'| {nm} | {px} | {arrow(float(c) if c else 0)} **{pct(c)}** | {amt(a)} |')
    if not rows: return '⚠️ 暂无指数数据'
    return '| 指数 | 最新价 | 涨跌幅 | 成交额 |\n|------|--------|--------|--------|\n' + '\n'.join(rows)

def mode_broad():
    data = read()
    items = []
    for i in data.get('datas',[]):
        if not i: continue
        nm = i.get('指数简称','?')
        c = float(field(i, f'涨跌幅[{DATE_KEY}]') or 0)
        items.append((nm, c))
    if not items: return '⚠️ 暂无宽基数据'

    large = [x for x in items if x[0] in ('上证50','沪深300')]
    small = [x for x in items if x[0] in ('中证1000','科创50')]
    la = sum(x[1] for x in large)/len(large) if large else 0
    sa = sum(x[1] for x in small)/len(small) if small else 0
    spread = la - sa

    if spread > 0.3: style = '🔵 大盘防御占优'
    elif spread < -0.3: style = '🟠 小盘成长占优'
    else: style = '⚪ 大小盘均衡'

    rows = [f'| {nm} | {arrow(c)} **{c:+.2f}%** |' for nm, c in items]
    header = '| 指数 | 涨跌幅 |\n|------|--------|'
    return header + '\n' + '\n'.join(rows) + f'\n\n> 风格：{style}（差 {spread:+.2f}%）'

def mode_sectors():
    data = read()
    datas = [i for i in data.get('datas',[]) if i and i.get('指数简称')]
    if not datas: return '⚠️ 暂无板块数据'
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    top = datas[:top_n]
    rows = ['| 板块 | 涨跌幅 | 资金净流入 |', '|------|--------|------------|']
    for item in top:
        nm = item.get('指数简称','?')
        c = float(field(item, f'涨跌幅[{DATE_KEY}]') or 0)
        f_flow = field(item, f'资金净流入额[{DATE_KEY}]') or 0
        rows.append(f'| {nm} | {arrow(c)} **{c:+.2f}%** | {amt(f_flow)} |')
    return '\n'.join(rows)

def mode_leaders():
    data = read()
    datas = [i for i in data.get('datas',[]) if i and i.get('股票简称')]
    if not datas: return '⚠️ 暂无龙头数据'
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    top = datas[:top_n]
    up = sum(1 for i in top if float(field(i, f'涨跌幅[{DATE_KEY}]') or 0) > 0)
    health = '🟢 健康' if up >= top_n*0.7 else ('🟡 分化' if up >= top_n*0.4 else '🔴 恶化')
    rows = ['| 股票 | 成交额 | 涨跌幅 | 资金流向 |', '|------|--------|--------|----------|']
    for item in top:
        nm = item.get('股票简称','?')
        a = field(item, f'成交额[{DATE_KEY}]')
        c = float(field(item, f'涨跌幅[{DATE_KEY}]') or 0)
        f_flow = field(item, f'资金流向[{DATE_KEY}]', f'资金净流入额[{DATE_KEY}]') or 0
        c_str = '⚠️跌停' if c <= -9.9 else f'{arrow(c)} **{c:+.2f}%**'
        rows.append(f'| {nm} | {amt(a)} | {c_str} | {amt(f_flow)} |')
    return '\n'.join(rows) + f'\n\n> 🩺 健康度：{health}（{up}/{top_n} 上涨）'

def mode_etf():
    data = read()
    datas = data.get('datas',[])
    if not datas: return '⚠️ 暂无ETF数据'
    datas.sort(key=lambda x: float(field(x, f'涨跌幅[{DATE_KEY}]') or -999), reverse=True)
    rows = ['| ETF | 今日 | 成交额 | 量比 |', '|------|------|--------|------|']
    for i in datas[:15]:
        nm = i.get('基金简称','?')
        c = float(field(i, f'涨跌幅[{DATE_KEY}]') or 0)
        a = field(i, f'成交额[{DATE_KEY}]') or 0
        vr = field(i, f'量比[{DATE_KEY}]') or '—'
        rows.append(f'| {nm} | {arrow(c)} **{c:+.2f}%** | {amt(a)} | {vr} |')
    return '\n'.join(rows)

def mode_stocks():
    data = read()
    datas = [i for i in data.get('datas',[]) if i and i.get('股票简称')]
    if not datas: return '⚠️ 暂无个股数据'
    rows = ['| 股票 | 最新价 | 涨跌幅 | 换手 | 量比 | PE | 成交额 |',
            '|------|--------|--------|------|------|----|--------|']
    for i in datas[:15]:
        nm = i.get('股票简称','?')
        px = i.get('最新价','?')
        c = float(field(i, f'涨跌幅[{DATE_KEY}]') or 0)
        to = field(i, f'换手率[{DATE_KEY}]') or '—'
        vr = field(i, f'量比[{DATE_KEY}]') or '—'
        pe = i.get('市盈率','—')
        a = field(i, f'成交额[{DATE_KEY}]') or 0
        rows.append(f'| {nm} | {px} | {arrow(c)} **{c:+.2f}%** | {to} | {vr} | {pe} | {amt(a)} |')
    return '\n'.join(rows)

modes = {
    'indices': mode_indices, 'broad': mode_broad, 'sectors': mode_sectors,
    'leaders': mode_leaders, 'etf': mode_etf, 'stocks': mode_stocks,
}

if __name__ == '__main__':
    if MODE in modes:
        print(modes[MODE]())
    else:
        print(f'用法: trading-table.py <mode> [date]')
        print(f'可用: {", ".join(modes.keys())}')
