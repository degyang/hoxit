# Trading Funder Interface Coverage

This document is the implementation-level coverage map for replacing ai-hedge-fund data APIs with hoxit A-share data sources. iWencai remains primary for fundamentals, valuation snapshots, announcements, and reports. hoxit `mootdx`/TDX is primary for OHLCV, quote, intraday, technical, and risk workflows.

## Coverage Grades

| Grade | Meaning | Implementation rule |
|---|---|---|
| A | Directly covered by the chosen hoxit A-share source | Use the named hoxit route as default. |
| B | Covered with field mapping, narrowed queries, or light canonicalization | Use the named source, document mapping in facts bundle. |
| C | Partially covered by A-share substitutes | Use substitute and lower confidence. |
| D | Not reliably covered | Mark missing, block dependent score, or add future data adapter. |

## Original API Function Coverage

| Original function | Used by | A-share replacement | Grade | Implementation |
|---|---|---|---:|---|
| `get_financial_metrics` | Buffett, Graham, Munger, Ackman, Cathie Wood, Burry, Pabrai, Jhunjhunwala, Damodaran, Fundamentals, Growth, Valuation, Taleb, Druckenmiller | `finance`, `market` | A/B | Query 5-10 years of profitability, growth, leverage, margins, valuation. Split broad queries. |
| `search_line_items` | Almost all fundamental/persona agents | `finance`, `business`, `management` | B | Translate line items to Chinese finance fields; use multiple narrow queries. |
| `get_market_cap` | Most valuation/persona agents | `basicinfo`, `market` | A | Use total market cap by date. |
| `get_prices` | Technicals, Risk Manager, Druckenmiller, Taleb, Backtesting | `hoxit market bars --adjust qfq` (`mootdx`/TDX) | A | Use row-wise adjusted OHLCV from `market bars`; compute indicators locally. iWencai OHLCV is fallback only. |
| `get_insider_trades` | Munger, Fisher, Lynch, Druckenmiller, Burry, Taleb, Sentiment, Growth | `management`, `event`, `announcement` | C | Replace with executive/shareholder holdings, reductions, buybacks, pledges, equity incentives. |
| `get_company_news` | Munger, Fisher, Lynch, Druckenmiller, Burry, Taleb, Sentiment, News Sentiment | `announcement`, `report`, `event` | C | Use official announcements and reports first; external Chinese news adapter is optional later. |
| `call_llm` | Persona agents, Damodaran, News Sentiment, Portfolio Manager | Claude Code reasoning | A | Preserve prompt/facts pattern, not LangChain runtime. |

## FinancialMetrics Field Map

| Original field | iWencai query fields | Route | Grade | Notes |
|---|---|---|---:|---|
| `market_cap` | 总市值、A股流通市值 | `basicinfo`, `market` | A | Use dated market cap if available. |
| `enterprise_value` | 企业价值、EV；or 市值 + 有息负债 - 现金 | `finance`, `market` | C | Often absent; compute only if debt/cash available. |
| `price_to_earnings_ratio` | PE、动态市盈率、市盈率 TTM | `market`, `basicinfo` | A | Prefer TTM PE. |
| `price_to_book_ratio` | PB、市净率 | `market`, `basicinfo` | A | Important for financials. |
| `price_to_sales_ratio` | PS、市销率 | `market` | B | Some A-share queries may require separate wording. |
| `enterprise_value_to_ebitda_ratio` | EV/EBITDA | `finance`, `market` | C | Compute if EV and EBITDA available. |
| `enterprise_value_to_revenue_ratio` | EV/营业收入 | `finance`, `market` | C | Compute if EV available. |
| `free_cash_flow_yield` | 自由现金流、市值 | `finance`, `market` | B | Compute FCF / market cap. |
| `peg_ratio` | PEG | `market`, `finance` | B | If absent, compute PE / earnings growth. |
| `gross_margin` | 毛利率 | `finance` | A/B | Banks may not expose meaningful gross margin. |
| `operating_margin` | 营业利润率、经营利润率 | `finance` | A | Use sector-adjusted interpretation. |
| `net_margin` | 销售净利率、净利率 | `finance` | A | Good coverage. |
| `return_on_equity` | ROE、净资产收益率、加权 ROE | `finance` | A | Use latest and multi-year trend. |
| `return_on_assets` | ROA、总资产收益率 | `finance` | A/B | Query separately if not returned. |
| `return_on_invested_capital` | ROIC、投入资本回报率 | `finance` | B | Not always returned; use ROE/ROA fallback when absent. |
| `asset_turnover` | 总资产周转率、资产周转率 | `finance` | A/B | Low by nature for banks. |
| `inventory_turnover` | 存货周转率 | `finance` | A/B | Not applicable to banks/financials. |
| `receivables_turnover` | 应收账款周转率 | `finance` | A/B | Sector dependent. |
| `days_sales_outstanding` | 应收账款周转天数 | `finance` | B | Query separately. |
| `operating_cycle` | 营业周期 | `finance` | B | Query separately. |
| `working_capital_turnover` | 营运资本周转率 | `finance` | B/C | May need compute. |
| `current_ratio` | 流动比率 | `finance` | B/C | **Downgraded: not returned for financials (bank sector nature).** Good for industrials. |
| `quick_ratio` | 速动比率 | `finance` | B/C | **Downgraded: not returned for financials.** Good for industrials; query separately. |
| `cash_ratio` | 现金比率 | `finance` | B | Query separately. |
| `operating_cash_flow_ratio` | 经营现金流/流动负债、经营现金流比率 | `finance` | C | Often compute. |
| `debt_to_equity` | 产权比率、债务权益比 | `finance` | A/B | For banks, use sector-adjusted treatment. |
| `debt_to_assets` | 资产负债率 | `finance` | A | Good coverage. |
| `interest_coverage` | 利息保障倍数 | `finance` | B/C | May not be available for financials. |
| `revenue_growth` | 营业收入同比增长率、营收增长率 | `finance` | A | Good coverage. |
| `earnings_growth` | 净利润同比增长率、归母净利润同比增长率、扣非净利润同比增长率 | `finance` | A | Prefer扣非 for quality. |
| `book_value_growth` | 每股净资产增长率、净资产增长率 | `finance` | A/B | Compute CAGR when needed. |
| `earnings_per_share_growth` | EPS 同比增长率、基本每股收益同比增长率 | `finance` | A | Good coverage. |
| `free_cash_flow_growth` | 自由现金流增长率 | `finance` | B/C | Often compute if FCF returned. |
| `operating_income_growth` | 营业利润同比增长率 | `finance` | A/B | Query separately. |
| `ebitda_growth` | EBITDA 增长率 | `finance` | C | Compute if EBITDA available. |
| `payout_ratio` | 股利支付率、现金分红比例 | `finance`, `management` | A | Good coverage. |
| `earnings_per_share` | EPS、基本每股收益 | `finance` | A | Good coverage. |
| `book_value_per_share` | 每股净资产、BVPS | `finance` | A | Good coverage. |
| `free_cash_flow_per_share` | 每股自由现金流 | `finance` | B/C | Compute from FCF and shares. |

## LineItem Field Map

| Original line item | iWencai query fields | Route | Grade | Notes |
|---|---|---|---:|---|
| `revenue` | 营业收入 | `finance` | A | Core field. |
| `gross_profit` | 毛利润 | `finance` | B | May not apply to banks. |
| `gross_margin` | 毛利率 | `finance` | A/B | Sector dependent. |
| `operating_income` | 营业利润、经营利润 | `finance` | A/B | Good for most industrials. |
| `operating_margin` | 营业利润率、经营利润率 | `finance` | B | **Downgraded from A: validation found 比亚迪 returns identical 营业利润率[20251231] for all 5 years (fixed latest-period value, not true annual series).** Use with multi-year sanity check. |
| `net_income` | 净利润、归母净利润、扣非归母净利润 | `finance` | A | Prefer归母/扣非 depending model. |
| `earnings_per_share` | EPS、基本每股收益 | `finance` | A | Good coverage. |
| `free_cash_flow` | 自由现金流 | `finance` | B | Query can return, but reliability varies. |
| `capital_expenditure` | 资本开支、购建固定资产等现金流出 | `finance` | A/B | Good enough for valuation. |
| `depreciation_and_amortization` | 当期计提折旧与摊销 | `finance` | B/C | **Corrected field name: use 当期计提折旧与摊销, not 折旧摊销.** Good for industrials/semis (比亚迪, 中芯国际 returned 5y). Not returned for financials (bank sector nature). |
| `working_capital` | 营运资本、流动资产-流动负债 | `finance` | C | Compute when current assets/liabilities available. |
| `current_assets` | 流动资产 | `finance` | A/B | Query separately. |
| `current_liabilities` | 流动负债 | `finance` | A/B | Query separately. |
| `total_assets` | 总资产 | `finance` | A | Good coverage. |
| `total_liabilities` | 总负债、负债 | `finance` | A | Good coverage. |
| `shareholders_equity` | 股东权益、净资产、归母权益 | `finance` | A | Good coverage. |
| `total_debt` | 有息负债、短期借款、长期借款、应付债券 | `finance` | C | **Downgraded: 带息债务 (absolute) only returned for 万科A (1/5 stocks).** Others return 有息负债率 (ratio) only. Requires narrowed query; financials need sector logic. |
| `cash_and_equivalents` | 货币资金、现金及现金等价物 | `finance` | C | **Downgraded: only returned for 1/5 validation stocks (万科A).** Must query separately; often absent. For banks, use 现金及存放中央银行款项 instead. |
| `interest_expense` | 利息费用、财务费用 | `finance` | B/C | Banks need net interest income logic. |
| `ebit` | EBIT、息税前利润 | `finance` | C | **Downgraded: only returned for 1/5 validation stocks (中芯国际).** Query or compute from EBITDA - D&A when available. |
| `ebitda` | EBITDA | `finance` | B/C | Query or compute. |
| `outstanding_shares` | 总股本、流通股本 | `finance`, `market`, `management` | B | **Downgraded: only current period returned; no 5y historical series.** Good for latest snapshot. |
| `dividends_and_other_cash_distributions` | 分红金额、现金分红、每股分红 | `finance`, `management` | A | Good coverage. |
| `issuance_or_purchase_of_equity_shares` | 回购、增发、股本变化、融资 | `management`, `announcement` | B/C | Use announcements for detail. |
| `research_and_development` | 研发费用、研发投入、研发费用率 | `finance`, `business` | A/B | Important for growth/Cathie/Fisher. |
| `goodwill_and_intangible_assets` | 商誉、无形资产 | `finance` | A/B | Query separately. |
| `operating_expense` | 销售费用、管理费用、研发费用、期间费用 | `finance` | B | Query separately. |

## Price Data Map

| Original Price field | Primary fields | Route | Grade | Required by |
|---|---|---|---:|---|
| `open` | `open` | `hoxit market bars` | A | Technicals, risk. |
| `close` | `close` | `hoxit market bars` | A | Most price calculations. |
| `high` | `high` | `hoxit market bars` | A | ATR, volatility. |
| `low` | `low` | `hoxit market bars` | A | ATR, volatility. |
| `volume` | `volume` or `vol` | `hoxit market bars` | A | Volume confirmation, anomaly. |
| `amount` | `amount` | `hoxit market bars` | A/B | Liquidity and turnover proxy. |
| `time` | `datetime`, `year/month/day` | `hoxit market bars` | A | Time series. |

Operational note: technical/risk workflows should not depend on iWencai's natural-language `market` route. hoxit `market bars` already returns a JSON array of OHLCV rows, including daily/weekly/monthly/minute categories. The only canonicalization needed is field cleanup and data-quality checks.

**Architecture update:** PR1/PR3A proved that iWencai can return OHLCV, but the shape is a fragile single-row wide table with `field_name[YYYYMMDD]` suffixes and unreliable broad technical fields. That is no longer the main implementation path. Use iWencai OHLCV only as `source: iwencai_fallback` when `mootdx` is unavailable.

## InsiderTrade Replacement Map

The US-style `InsiderTrade` model does not map directly to A shares.

| Original field | A-share substitute | Route | Grade | Notes |
|---|---|---|---:|---|
| `name`, `title` | 董监高姓名、职务 | `announcement` (search only) | D | **Downgraded: management route query returns empty for ALL 5 validation stocks.** Only available via announcement text mining. |
| `transaction_date`, `filing_date` | 公告日期、变动日期 | `announcement` (search) | B | Use official announcement `publish_date`. |
| `transaction_shares` | 增持/减持股数、回购股数 | `announcement` (search) | C | **Downgraded: only available in announcement body text, not as structured fields.** Need text extraction. |
| `transaction_value` | 增减持金额、回购金额 | `announcement` (search) | C | **Downgraded: only in announcement text.** Often partial. |
| `shares_owned_after_transaction` | 变动后持股数/比例 | `announcement` (search) | D | **Downgraded: not returnable as structured field.** Requires PDF parsing. |

Implementation rule: convert this into an `insider_proxy` score rather than pretending it is equivalent to US insider trades.

## CompanyNews Replacement Map

| Original field | A-share substitute | Route | Grade | Notes |
|---|---|---|---:|---|
| `title` | 公告标题、研报标题 | `announcement` (search), `report` (search) | A/B | **Corrected: use search routes only; event query route is empty.** |
| `source` | 公告/研报来源 | `announcement`, `report` | A/B | Preserve source type from `extra.publish_source`. |
| `date` | 公告日期、研报日期 | `announcement`, `report` | A/B | Use `publish_date`. |
| `url` | 公告/研报链接 if returned | `announcement`, `report` | B | URL returned in search results (e.g. cninfo.com.cn PDF). **Upgraded from C: validation confirms URLs returned.** |
| `sentiment` | 规则/LLM 分类 | Claude Code | B/C | Must label as derived sentiment. |

Implementation rule: official announcements outrank generic news. Research reports are opinion evidence, not company facts.

**⚠️ CRITICAL: `event` route (query2data) returned empty for ALL 5 validation stocks.** The `event` query2data route only returns stock code — no structured event data (业绩预告, 解禁, 监管函, 诉讼) is retrievable. Use `announcement` and `report` search routes instead. The `event` route should be treated as **blocked (Grade D)** until the upstream data source is fixed or a replacement is found.

## Agent-Level Coverage

| Family | Agent | Coverage | Blocking gaps | Initial implementation status |
|---|---|---:|---|---|
| Value | Buffett | B | **Downgraded: business route empty; insider fields dead.** Bank ROE/ROA need separate query. | Sample command exists but needs query pack fixes. |
| Value | Graham | A/B | **ROIC not returned for financials; 营业利润率 may be fixed value.** | Ready after query pack corrections. |
| Value | Munger | C | **Insider proxy via management route is DEAD.** Need announcement search text mining. | Blocked until insider proxy redesigned. |
| Value | Pabrai | B | FCF命名 is 企业自由现金流量; 货币资金 only for some stocks. | Ready after field-name mapping. |
| Value | Burry | C | **Event route empty.** News/catalyst only from announcement/report search. | Requires announcement-based event proxy. |
| Growth | Fisher | C/D | **Business route empty; insider route dead; event route empty.** Three routes blocked. | Requires fundamental redesign of scuttlebutt proxy. |
| Growth | Lynch | B/C | PEG needs separate computation; insider dead. | Ready after PEG computation + insider proxy. |
| Growth | Cathie Wood | B/C | **Business route empty.** TAM/disruption from reports only. | Requires report/concept prompts. |
| Tactical | Ackman | B/C | **Event route empty.** Activism catalyst from announcements only. | Requires announcement/event adapter. |
| Tactical | Druckenmiller | C | TDX price series OK; **macro route untested.** News proxy needed. | Ready after technical/risk command uses `market bars`. |
| Tactical | Jhunjhunwala | B/C | **Business route empty.** Management story from reports only. | Requires report/event evidence. |
| Tactical | Taleb | C | TDX OHLCV can support volatility/tail-shape calculations. **Tail event data missing (event route empty).** | Price series OK; tail events blocked. |
| Quant | Damodaran | B/C | **带息债务 absolute only for 万科A.** WACC/CAPM beta needs compute. | Requires debt structure assumptions. |
| Quant | Valuation | B/C | EV/EBITDA computable from returned fields. **货币资金 missing for 4/5 stocks.** | Requires cash field fallback. |
| Quant | Fundamentals | B | **营业利润率 may be fixed value.** Sector thresholds needed. | Ready after field validation. |
| Quant | Growth | C | **Insider conviction DEAD — management route empty.** | Requires insider proxy redesign. |
| Quant | Technicals | B | Use `mootdx` OHLCV and compute RSI/MACD/ATR/MA locally. | Ready after `tos-funder-quant-price-series`. |
| Quant | Sentiment | C | News/insider proxy required. **Event route empty.** | Use announcement/report search + LLM. |
| Quant | News Sentiment | C | External news coverage not available. | Use announcements/reports first. |
| Portfolio | Risk Manager | B | TDX OHLCV supports returns, drawdown, volatility, correlation. | Ready after `tos-funder-quant-price-series`. |
| Portfolio | Portfolio Manager | A | No platform needed. | Can consume saved signals. |

## Practical Query Packs

Use these query packs as the starting point for CC implementation.

### Core Company Pack

```bash
hoxit iwc query -r basicinfo -q "<TARGET> 公司简介 主营业务 行业 概念 总市值 股票代码" --limit 5
# ⚠️ business route returned EMPTY for ALL 5 validation stocks (宁波银行, 贵州茅台, 比亚迪, 中芯国际, 万科A).
# Fallback: use basicinfo 公司简介 + 主营产品 fields instead.
# hoxit iwc query -r business -q "<TARGET> 主营业务 产品 客户 供应商 子公司 竞争优势" --limit 10  # BLOCKED
```

### Core Finance Pack

```bash
hoxit iwc query -r finance -q "<TARGET> 最近5年 ROE ROIC ROA 资产负债率 产权比率 营业利润率 毛利率 净利率 流动比率 速动比率 总资产周转率" --limit 10
hoxit iwc query -r finance -q "<TARGET> 最近5年 营业收入 营业利润 净利润 归母净利润 扣非归母净利润 每股收益 每股净资产 增长率" --limit 10
hoxit iwc query -r finance -q "<TARGET> 最近5年 总资产 总负债 股东权益 总股本 货币资金 有息负债 商誉 无形资产" --limit 10
```

### Cash Flow / Valuation Pack

```bash
# Core cash flow (use 企业自由现金流量 not 自由现金流; 当期计提折旧与摊销 not 折旧摊销)
hoxit iwc query -r finance -q "<TARGET> 最近5年 经营现金流 企业自由现金流量 资本开支 当期计提折旧与摊销 营运资本 EBITDA 息税前利润 利息费用" --limit 10
# Valuation snapshot — keep field count ≤4 to avoid empty results
hoxit iwc query -r market -q "<TARGET> 最新价 总市值 PE PB PS PEG" --limit 10
# Valuation percentile — query SEPARATELY (mixing with other fields causes failure)
hoxit iwc query -r market -q "<TARGET> 近5年估值分位" --limit 5
# Bank-specific supplemental
hoxit iwc query -r finance -q "<TARGET> 净息差 不良贷款率 拨备覆盖率 总资产净利率" --limit 5
```

### Capital Allocation / Insider Proxy Pack

```bash
# ⚠️ Broad management query (>3 fields) returns EMPTY. Split into narrow queries:
hoxit iwc query -r management -q "<TARGET> 最近5年 分红 股本 股东人数" --limit 10
hoxit iwc query -r management -q "<TARGET> 回购 增发" --limit 10
# ⚠️ Insider fields are DEAD — management route returns empty for ALL 5 stocks:
# 高管持股, 股权激励, 质押, 减持 → always empty. Use announcement search instead:
hoxit iwc search -r announcement -q "<TARGET> 最近一年 回购 分红 增持 减持 质押 股权激励 定增"
```

### Event / Sentiment Pack

```bash
# ⚠️ event route (query2data) returned EMPTY for ALL 5 stocks — no structured event data.
# Use announcement + report SEARCH routes only:
hoxit iwc search -r announcement -q "<TARGET> 最近一年 业绩预告 监管函 诉讼 仲裁 重大风险"
hoxit iwc search -r report -q "<TARGET> 护城河 盈利能力 增长空间 估值 目标价 风险 研报"
# For structured event data (业绩预告 dates, 解禁 schedules): BLOCKED until upstream fix.
```

### Price / Technical Pack

```bash
# Daily OHLCV 250 bars — primary technical/risk source
.venv/bin/hoxit market bars <CODE> --category 4 --offset 250 --adjust qfq
# Weekly/monthly context
.venv/bin/hoxit market bars <CODE> --category 5 --offset 120 --adjust qfq
.venv/bin/hoxit market bars <CODE> --category 6 --offset 60 --adjust qfq
# Intraday context for kanpan/tactical workflows
.venv/bin/hoxit market bars <CODE> --category 9 --offset 160 --adjust raw
.venv/bin/hoxit market quote <CODE> --format json
```

Compute RSI, MACD, moving averages, ATR, Bollinger bands, volatility, drawdown, and correlation locally from `market bars`. Use iWencai technical fields only as cross-checks or fallback evidence.

## Verification Protocol

Each adapter implementation must be tested on at least these A-share cases:

| Case | Purpose |
|---|---|
| 宁波银行 | Bank sector-adjusted valuation. |
| 贵州茅台 | High-quality consumer moat, standard financial coverage. |
| 比亚迪 | Growth/manufacturing, R&D and capex. |
| 中芯国际 | R&D, cyclicality, high capex, policy/technology narrative. |
| 万科A | Real estate sector-adjusted balance sheet risk. |

For each case, capture:

```text
routes_used:
fields_returned:
fields_missing:
fallbacks:
score_impact:
final_data_quality:
```
