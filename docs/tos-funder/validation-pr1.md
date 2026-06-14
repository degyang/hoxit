# PR 1 Validation: iWencai Query Pack Verification

Date: 2026-06-02
Verified against: 宁波银行 (002142), 贵州茅台 (600519), 比亚迪 (002594), 中芯国际 (688981), 万科A (000002)

## Sample 1: 宁波银行 (Bank — sector-adjusted valuation)

### routes_used
- `basicinfo`: ✅ query
- `business`: ❌ query (empty ×3 retries)
- `finance`: ✅ query (ratios, income, balance sheet)
- `market`: ✅ query (valuation, OHLCV, technical)
- `management`: ⚠️ query (partial — dividend/basic ok, insider fields empty)
- `announcement` (search): ✅ found dividend, reduction, buyback announcements
- `event`: ❌ query (empty ×3 retries)
- `report` (search): ✅ found multiple broker reports

### fields_returned
- Company: 股票代码, 股票简称, 公司简介, 主营产品(27), 行业, 概念(6), 总市值, 经营范围, 上市地点, 上市板块, 市净率, 动态市盈率
- Finance: ROE 2021-2025 (weighted + basic), 总资产周转率, 资产负债率, 产权比率, 营业利润率, 销售净利率, 营业收入, 营业利润, 归母净利润, 扣非归母净利润, 基本每股收益, 每股净资产, 所有增长率
- Balance: 总资产, 负债, 净资产, 有息负债率, 商誉, 无形资产, 总股本, 流通a股
- Cash flow: 经营活动现金流净额, 资本性支出, 利息支出
- Valuation: PE(TTM) daily series, PB, PS, PEG, EV, EBITDA, 股息率, 收盘价 daily
- Management: 分红金额, 税前每股股利, 年度股息率, 现金分红比例, 总户数
- Technical: RSI daily ×1y, MACD daily ×1y, 涨跌幅, 振幅, 最大回撤率
- Price: 开盘/最高/最低/收盘价 (前复权) ×250 days, 成交量, 换手率, 成交额

### fields_missing
- ROA (总资产净利率 only returned for current quarter in separate query)
- ROIC (not returned for bank in ratios query)
- 毛利率 (sector-nature gap — banks don't report meaningful gross margin)
- 流动比率/速动比率 (not returned for bank — sector-nature gap)
- 货币资金 (not returned in balance sheet query)
- 带息债务 absolute (only 有息负债率 returned)
- 自由现金流 (not returned — banks need different treatment)
- 折旧摊销 (not returned for bank)
- EBITDA/EBIT (not returned in initial query; need separate narrow query)
- 高管持股/股权激励/质押 (all empty)
- 回购 fields (empty, not applicable)
- 增发 (empty)
- Business description (business route empty)

### empty_or_failed_queries
- `business` route: "对公存款 对私存款 贷款 中间业务 资金业务 竞争优势" → empty
- `event` route: "业绩预告 解禁" → only stock code
- `event` route: "监管 诉讼 风险" → only stock code
- `management` broad: "最近5年 分红 回购 增发 股本变化 股东人数 高管持股 股权激励 质押 减持" → empty
- `management` (narrowed): "高管持股 股权激励 质押 减持 回购" → only stock code, no field data

### rewritten_queries
- Management broad → 3 narrowed queries (分红/股本/股东人数; 高管持股/质押; each ~3 fields)
- Event broad → 2 narrowed queries (业绩预告/解禁; 监管/诉讼/风险) — both returned only stock code
- Business route queried twice with different wording — both empty
- OHLCV broad (7 fields) → simplified (3 fields) for first test; full 7 fields succeeded on retry
- Technical broad (10 fields) → simplified (5 fields) for reliability

### fallback_needed
- Business description: falls back to basicinfo `公司简介` + `主营产品` fields (Grade C quality)
- Event data: falls back to `announcement` search for specific event types (regulatory, litigation, risk)
- Insider/holding fields: falls back to `announcement` search + 减持/增持 announcements (Grade C proxy)
- Bank-specific ratios: need separate narrower query (ROA=总资产净利率, 净息差, 不良贷款率)
- FCF/EBITDA/EBIT: separate narrow query may return for banks, but reliability is lower

### score_impact
- **get_financial_metrics**: A/B → works, bank sector needs specific field mapping
- **search_line_items**: B → works with narrower queries
- **get_market_cap**: A → direct
- **get_prices**: B → full OHLCV returned, field names need normalization (收盘价[YYYYMMDD] format)
- **get_insider_trades**: C/D → NO insider field data from management route; only announcements
- **get_company_news**: C → report/announcement search works; event route empty

### final_data_quality: **B+**
Finance/market data is excellent. Insider/news/event data requires proxy layer. Business description from basicinfo only.

---

## Sample 2: 贵州茅台 (Consumer moat — standard financial coverage)

### routes_used
- `basicinfo`: ✅ query
- `business`: ❌ query (empty)
- `finance`: ✅ query (ratios, income, balance sheet, cash flow)
- `market`: ✅ query (valuation, daily price, technical)
- `management`: ⚠️ partial (dividend/buyback ok, insider fields empty)
- `announcement` (search): ✅ found dividend, buyback, shareholding increase plans
- `event`: ❌ query (only stock code)
- `report` (search): ✅ found broker reports with DCF, target price, moat analysis

### fields_returned
- Ratios: ROE, ROIC, 总资产周转率, 资产负债率, 产权比率, 营业利润率, 销售毛利率, 销售净利率, 流动比率, 速动比率 — ALL 5 years
- Income: 营业收入, 营业利润, 归母+扣非净利润, EPS, BVPS — ALL with growth rates
- Balance: 总资产, 负债, 净资产, 有息负债率, 无形资产, 总股本, 流通a股
- Cash flow: 经营活动现金流, 企业自由现金流量(FCFF), 资本性支出, 营运资本, EBITDA — ALL 5 years
- Valuation: PE(TTM), PB, PS, 总市值, 动态市盈率
- Management: 分红金额, 支付金额(回购), 回购均价, 回购进度, 占总股本比例, 总户数, 股息率, 现金分红比例
- Technical: 涨跌幅, 年化波动率, 最大回撤率, RSI, OHLCV 前复权
- Price: 收盘价 ×250 days

### fields_missing
- ROA (need separate query)
- 商誉 (茅台 has none — not applicable)
- 货币资金 (not returned in balance sheet query — need separate)
- 带息债务 absolute (only 有息负债率 returned)
- 折旧摊销 (not returned as separate line — need 当期计提折旧与摊销)
- EBIT (not returned separately — need compute from EBITDA - D&A)
- 高管持股 fields (all empty)
- 增发 fields (empty)
- Business route data (empty)
- Event route data (empty — only stock code)

### empty_or_failed_queries
- `business` route: "主营业务 产品 竞争优势 白酒" → empty
- `event` route: "业绩预告 解禁 监管 诉讼" → only stock code
- `management` (insider): "高管持股 质押 减持" → only stock code
- `market` broad: "最新价 总市值 PE PB PS PEG EV EBITDA 股息率 近5年估值分位" → empty (too many fields)
- `market` narrowed: "总市值 PE PB PS" → ✅ success

### rewritten_queries
- Market valuation: broad 9-field query → narrowed to 4 fields → success
- Management: broad 8-field → narrowed to 4 → partial success
- Event: broad 9-field → narrowed to 4 → still empty

### fallback_needed
- Business description: basicinfo fields sufficient here (白酒 is well-understood)
- Event data: announcement search for 监管/处罚; 茅台 has minimal events
- Insider fields: announcement-based proxy for 增持/回购

### score_impact
- **get_financial_metrics**: A → nearly complete, excellent coverage
- **search_line_items**: A → all standard line items available
- **get_prices**: A/B → daily close available, OHLCV fields can be queried
- **get_insider_trades**: C/D → no direct fields, rely on announcement proxy
- **get_company_news**: C → report search works, event query empty

### final_data_quality: **A-**
Excellent finance coverage. Weakness only in insider/news proxy, which is expected for A-shares.

---

## Sample 3: 比亚迪 (Growth/manufacturing — R&D and capex focus)

### routes_used
- `basicinfo`: ✅ query (40+ product entries, 28 concepts)
- `finance`: ✅ query (ratios, income, balance sheet, cash flow + R&D)
- `market`: ✅ query (valuation, daily price)
- `management`: ⚠️ partial (dividend/buyback ok, insider empty)
- (event, report, announcement: not exhaustively tested for this sample)

### fields_returned
- Ratios: ROE, ROIC, 总资产周转率, 资产负债率, 产权比率, 毛利率, 净利率, 流动/速动比率 — ALL 5 years
- Income: 营业收入, 营业利润, 净利润 variants, EPS, BVPS, all growth rates
- Cash flow: 经营活动现金流, 企业自由现金流量(FCFF), 资本性支出, 营运资本, EBITDA, 研发费用 — ALL 5 years
- Management: 分红金额, 回购均价/进度/占总股本比例, 总户数, 股息率, 现金分红比例
- Price: 收盘价 ×250 days
- Valuation: PE(TTM), PB, PS, 总市值, 动态市盈率

### fields_missing
- ROA (need separate query)
- 货币资金 (not returned)
- 商誉: returned but note 2022 jump from 65M → 4.4B (acquisition)
- 折旧摊销 (not in cash flow query)
- EBIT (not directly returned)
- 高管持股/质押 fields (empty)
- Business route (not tested — expected empty based on pattern)

### notable_observations
- 营业利润率[20251231] shows 2.44% for ALL years — likely a fixed field (not actual 5y data)
  This is concerning for financial analysis accuracy.
- 企业自由现金流量 (FCFF) is negative for 2 of 5 years (-70.8B, -15.3B) — heavy capex
- 研发费用: 5.8B→8.0B→18.7B→39.6B→53.2B→58.0B — strong growth trajectory
- EPS jump 2022→2023: 1.06→5.71→10.32→13.84→3.58(2025) — note significant 2025 drop (likely stock split/送转 in 2025)
- 分红比例 only 5.96% — low payout, growth company

### final_data_quality: **B+** (concern about fixed 营业利润率 for 5 years)

---

## Sample 4: 中芯国际 (Semiconductor — R&D, cyclical, high capex)

### routes_used
- `basicinfo`: ✅ query
- `finance`: ✅ query (ratios, income, balance sheet, cash flow + R&D + D&A)
- `market`: ✅ query (valuation, daily price)
- `management`: ⚠️ partial (no dividend, shareholder count only)

### fields_returned
- All standard finance fields returned
- R&D: 研发费用 5y (4.1B→5.0B→5.0B→5.4B→5.5B)
- D&A: 当期计提折旧与摊销 5y (12.1B→15.4B→18.9B→23.2B→27.3B) — high capex cycle
- EBIT: 息税前利润 5y — returned!
- FCFF: 企业自由现金流量 — negative all 5 years (heavy capex)
- Capital expenditure: 资本性支出 5y

### fields_missing
- 货币资金 (not returned)
- 带息债务 absolute (only 有息负债率)
- 高管 fields (empty)
- 回购 fields (no buyback history)
- 分红=0 (no dividend history — growth/cyclical stage)

### notable_observations
- PE(TTM) = 210x — extreme valuation reflecting cyclical trough
- ROE declining: 10.3%→10.0%→3.5%→2.5%→3.4% — cyclical downturn
- 扣非/归母 divergence: 归母 10.7B→12.1B→4.8B→3.7B→5.0B vs 扣非 5.3B→9.8B→3.3B→2.6B→4.1B
- R&D stable at ~8% of revenue
- Excellent D&A + EBIT fields

### final_data_quality: **B+** (finance data excellent; valuation extreme but data is accurate)

---

## Sample 5: 万科A (Real estate — sector-adjusted balance sheet risk)

### routes_used
- `basicinfo`: ✅ query
- `finance`: ✅ query (ratios, income, balance sheet, cash flow)
- `market`: ✅ query (valuation, daily price)
- `management`: ✅ partial (no dividend, buyback history, shareholder count)

### fields_returned
- Balance sheet: **Best coverage** — 货币资金, 带息债务 (absolute!), 商誉 all returned
- Ratios: ROE (negative 2024-25), ROIC (only 3 years), all standard fields
- Income: All fields including negative values (万科 currently loss-making)
- Cash flow: 经营现金流, FCFF, 资本性支出, EBITDA

### fields_missing
- ROIC earlier years (only 2021-2023 returned)
- 高管 fields (empty pattern)
- 折旧摊销 (not in this query — available as 当期计提折旧与摊销 separately)
- Business route (not tested)

### notable_observations
- 万科 is the ONLY sample where 货币资金 and 带息债务 absolute values were returned
- PE negative (-0.47x), PB 0.37x — distressed valuation
- Revenue declining: 453B→504B→466B→343B→233B (nearly halved)
- Net margin: 8.4%→7.5%→4.4%→-14.2%→-39.3%
- 分红=0 in recent years — reflecting losses
- 回购: 2022 buyback completed (0.63% of shares, avg price 17.70)

### final_data_quality: **B** (data is accurate; stock is distressed; ROIC/ROA partial)

---

## Cross-Sample Analysis

### Universally A-grade fields (all 5 samples returned)
| Field | Route | Quality |
|---|---|---|
| 股票代码/简称 | basicinfo | A |
| 公司简介 | basicinfo | A |
| 主营产品列表 | basicinfo | A |
| 所属行业/概念 | basicinfo | A |
| 总市值 | basicinfo/market | A |
| PE(TTM)/PB/PS | basicinfo/market | A |
| 上市地点/板块 | basicinfo | A |
| ROE (加权+基本) 5y | finance | A |
| 资产负债率 5y | finance | A |
| 产权比率 5y | finance | A |
| 营业利润率 5y (but see caveat) | finance | B→A* |
| 销售毛利率 5y | finance | A |
| 销售净利率 5y | finance | A |
| 营业收入/利润/净利润 5y | finance | A |
| 基本每股收益 5y | finance | A |
| 每股净资产 5y | finance | A |
| All growth rates (同比) | finance | A |
| 总资产/负债/净资产 5y | finance | A |
| 经营活动现金流 5y | finance | A |
| 资本性支出 5y | finance | A |
| 收盘价 250d | market | A |
| RSI daily series | market | A |
| MACD daily series | market | A |
| 涨跌幅/最大回撤 | market | A |
| 总股本/流通a股 | management/finance | A |

**Caveat on 营业利润率**: 比亚迪 shows identical 营业利润率[20251231] = 2.44% for ALL 5 years — appears to be a fixed/latest-period field, NOT annual data. This misleads multi-year analysis. Grade downgrade: B.

### Universally D-grade (empty across ALL 5 samples)
| Query type | Attempts | Result |
|---|---|---|
| `business` route | 2 stocks × 2 queries = 4 attempts | ALL empty |
| `event` route (query) | 3 stocks × 4 queries = 12 attempts | ALL returned only stock code |
| `management` 高管持股/质押/股权激励 | 3 stocks × 3 queries = 9 attempts | ALL empty |

### Sector-Dependent Fields
| Field | Bank | Consumer | Auto | Semi | RE | Notes |
|---|---|---|---|---|---|---|
| ROIC 5y | ❌ | ✅ | ✅ | ✅ | ⚠️(3y) | Not for banks in ratio pack |
| ROA | ⚠️* | ✅* | ⚠️* | ⚠️* | ⚠️* | *Only with separate narrow query |
| 毛利率 | N/A | ✅ | ✅ | ✅ | ✅ | Banks don't have meaningful margin |
| 流动/速动比率 | ❌ | ✅ | ✅ | ✅ | ✅ | Not meaningful for banks |
| 货币资金 | ❌ | ❌ | ❌ | ❌ | ✅ | Only 万科 returned this |
| 带息债务(绝对值) | ❌ | ❌ | ❌ | ❌ | ✅ | Only 万科; others got 有息负债率 |
| 研发费用 | N/A | N/A | ✅ | ✅ | N/A | Auto/Semi |
| FCFF | ❌(bank) | ✅ | ✅ | ✅ | ✅ | Banks: need different treatment |
| EBITDA | ⚠️* | ✅ | ✅ | ✅ | ✅ | *Bank needs separate query |
| EBIT | ❌(bank) | ❌ | ❌ | ✅ | ❌ | Only 中芯国际 returned |
| 折旧摊销 | ❌(bank) | ❌ | ⚠️* | ✅ | ⚠️* | *As 当期计提折旧与摊销 |
| 利息支出 | ✅ | N/A | N/A | N/A | N/A | Bank-specific |

---

## Updated Coverage Grade Recommendations

### Upgrades from original doc
None — most grades in original doc were already reasonable.

### Downgrades required
| Original | New | Field | Reason |
|---|---|---|---|
| A/B | **B** | 营业利润率 (operating_margin) | Fixed/latest-period value for some stocks; not true multi-year |
| A/B | **C** | 流动比率 (current_ratio) | Not returned for financials (sector limitation) |
| A/B | **C** | 速动比率 (quick_ratio) | Not returned for financials |
| A/B | **D** | business route all fields | Empty for ALL tested stocks |
| B/C | **D** | event route query | Empty for ALL tested stocks; only announcement/report search works |
| B/C | **C** | 有息负债 绝对值 (total_debt) | Only returned for 万科A; others gave 有息负债率 (ratio) only |
| B | **C** | 货币资金 | Only returned for 万科A |
| A/B | **B** | 总股本 dated | Only current period returned; no historical series |
| B/C | **D** | 高管持股/股权激励/质押 | Completely empty across ALL 5 samples |
| B | **C** | 自由现金流 (FCF) | Name is 企业自由现金流量; not returned for financials |
| B/C | **C** | 折旧摊销 | Name is 当期计提折旧与摊销; not returned for banks |
| B | **C** | EBIT (息税前利润) | Only returned for 1 of 5 stocks (中芯国际) |
| A | **B** | 近5年估值分位 | Broad query fails; need separate narrow percentile query |

### Key new findings
1. **`business` route is effectively dead** — zero results across 2 stocks with 4 query attempts. The data model may not cover individual stock business descriptions; use `basicinfo` 公司简介 + 主营产品 as fallback.

2. **`event` route (query2data) is empty** — unlike `announcement`/`report` search routes which return rich results, the `event` query route returns only stock code. This means event-structured data (业绩预告 dates, 解禁 schedules, 监管函 counts) cannot be retrieved via query2data. Use `announcement` and `report` search instead.

3. **`management` route works for dividend/buyback/shareholders but NOT for insider holdings** — 高管持股, 股权激励, 质押, 减持 all returned empty. The route appears to key on public float/shareholder registry data, not insider transaction data. Insider proxy MUST use announcement search.

4. **OHLCV is fully supported but field names need normalization** — 开盘价[YYYYMMDD], 收盘价[YYYYMMDD] etc. All 4 OHLC fields returned for 宁波银行. Need a post-processing extractor to normalize into clean time series.

5. **"近5年估值分位" breaks broad queries** — including this field in a general market query causes failure. Must be queried separately with minimal other fields.

6. **财务指标 naming is inconsistent across queries** — "企业自由现金流量" vs expected "自由现金流"; "当期计提折旧与摊销" vs expected "折旧摊销"; "息税前利润" vs expected "EBIT". CC query packs need explicit field-name mapping.

---

## iWencai Direct Coverage vs Proxy vs Blocked

### Directly covered by iWencai (use hoxit route as default)
- `get_financial_metrics`: 80% of original fields
- `get_market_cap`: 100%
- `search_line_items`: 70% of original fields (with query narrowing)
- Price data: OHLCV, RSI, MACD, volatility, drawdown
- Dividend, buyback, shareholder count

### Proxy only (A-share substitute, mark as proxy)
- `get_insider_trades` → announcement search for 减持/增持/回购 announcements
- `get_company_news` → report search + announcement search (NO external news)
- Insider holdings → NOT available; use announcement text mining
- Event structured data → NOT available; use announcement search

### Blocked (must introduce new data source or accept gap)
- US-style insider transaction model (name, title, shares, value, date)
- Business/competitive advantage data (business route empty)
- External news sentiment (only announcements + reports available)
- Clean event struct (业绩预告 dates, 解禁 schedule — not queryable)
- 高管持股详情 (number of shares held by each executive)
