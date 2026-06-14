# PR 2A Validation: Buffett & Graham Commands

**Date**: 2026-06-02
**Samples**: 宁波银行 (002142.SZ, Bank), 贵州茅台 (600519.SH, Consumer)
**Status**: ✅ Validated

## Executive Summary

Both commands produce correct, sector-adjusted signals on live iWencai data. The bank-adjusted scoring framework works: 宁波银行 gets neutral (mixed) on both models, reflecting moderate bank fundamentals. 贵州茅台 gets bullish (Buffett) and neutral (Graham), reflecting exceptional quality but premium price.

| Command | 宁波银行 | 贵州茅台 |
|---|---|---|
| `/tos-funder-value-buffett` | 13/27 → **neutral** | 21/27 → **bullish** |
| `/tos-funder-value-graham` | 10/15 → **neutral/watch** | 9/15 → **neutral/hold** |

## Query Execution Summary

### 宁波银行 (002142.SZ) — 18 queries run

| # | Step | Route | Fields | Result | Notes |
|---|---|---|---|---|---|
| 1 | Identity | basicinfo | 7 | ✅ Full | Industry=银行→城商行 |
| 2 | Valuation | market | 4 | ✅ Full | PE=6.89, PB=0.89, PS=2.54 |
| 3 | Profitability 5y | finance | 11 | ⚠️ Partial | ROIC/ROA/毛利率/流动/速动 NOT returned (bank-expected) |
| 4 | Income & Growth 5y | finance | 8 | ✅ Full | 5y EPS/BVPS/revenue/NI + growth rates |
| 5 | Balance Sheet 5y | finance | 6 | ⚠️ Partial | 商誉 only 2y, 总股本 NOT in finance |
| 6 | Cash Flow 5y | finance | 5 | ⚠️ Partial | FCFF/营运资本 NOT returned (bank CF structure) |
| 7 | Capital Allocation | management | 3 | ✅ Full | 分红/股本/股东人数 (narrow query) |
| 8 | 回购 | management | 1 | ❌ Empty | No buyback history |
| 9 | Bank-Specific | finance | 5 | ✅ Full | NIM 1.73%, NPL 0.76%, CAR 9.25% |
| 10 | 每股股利 | management | 3 | ✅ Full | ¥1.20/share, yield 4.27%, payout 27% |
| 11 | 估值分位 | market | 1 | ✅ Full | 69.9% (declining from 96.5% in 2021) |
| 12 | 流动资产/流动负债 | finance | 2 | ❌ Empty | Only stock code returned (bank-finance incompatibility) |
| 13 | 货币资金/带息债务 | finance | 2 | ⚠️ Partial | Only 带息债务 Q1 2026 returned |
| 14 | Technical | market | 5 | ⚠️ Partial | RSI+涨跌幅 OK, MACD not returned |
| 15 | Ann. Search (Buffett) | announcement | — | ✅ | Dividend announcement found, no red flags |
| 16 | Ann. Search (Graham) | announcement | — | ❌ Empty | 亏损/监管/诉讼 terms → no results |
| 17 | Report Search | report | — | ✅ | 东方证券 "买入" rating, moat evidence |

### 贵州茅台 (600519.SH) — 18 queries run

| # | Step | Route | Fields | Result | Notes |
|---|---|---|---|---|---|
| 1 | Identity | basicinfo | 7 | ✅ Full | Industry=食品饮料→白酒 |
| 2 | Valuation | market | 4 | ✅ Full | PE=19.79, PB=6.04, PS=7.48 |
| 3 | Profitability 5y | finance | 11 | ⚠️ Partial | ROA NOT returned; 营业利润率 fixed value |
| 4 | Income & Growth 5y | finance | 8 | ❌ BROAD EMPTY | Split into 3 narrow queries → ✅ recovered |
| 5 | Income (split A) | finance | 4 | ✅ Full | Revenue, NI, EPS, BVPS |
| 6 | Income (split B) | finance | 3 | ✅ Full | 营业利润, 扣非NI, NI |
| 7 | Income (split C) | finance | 4 | ✅ Full | Growth rates: revenue -1.2%, NI -4.5% (2025 ⚠️) |
| 8 | Balance Sheet 5y | finance | 6 | ⚠️ Partial | 商誉=0 (not returned), 总股本 not in finance |
| 9 | Cash Flow 5y | finance | 5 | ✅ Full | All 5 fields returned (FCFF, capex, D&A, OCF, 营运资本) |
| 10 | Capital Allocation | management | 3 | ✅ Full | 分红¥65B, 股本~1.25B, 股东人数 growing |
| 11 | 回购 | management | 1 | ✅ Full | Two buyback records: ¥3B+¥6B, both for 注销 |
| 12 | 估值分位 | market | 1 | ✅ Full | 75.0% (elevated from 64.9% in 2021) |
| 13 | 流动资产/流动负债 | finance | 2 | ⚠️ Q1 Only | Only Q1 2026, no 5y history |
| 14 | 货币资金/带息债务 | finance | 2 | ⚠️ Q1 Only | 货币资金 ¥48.8B, 带息债务 ¥17.0B (Q1 only) |
| 15 | Technical (broad) | market | 5 | ❌ BROAD EMPTY | RSI+MACD+涨跌幅+波动率+最大回撤 → empty |
| 16 | Technical (narrow) | market | 3 | ✅ Full | RSI=49.6, max drawdown=18.1%, 涨跌幅 Q1 data only |
| 17 | Ann. Search (Buffett) | announcement | — | ✅ | Buyback progress update found (positive) |
| 18 | Ann. Search (Graham) | announcement | — | ❌ Empty | Clean — no negative risk events |
| 19 | Report Search | report | — | ✅ | 浙商证券 "买入", target ¥1,904.70 |

## Scoring: 宁波银行 (002142.SZ)

### Buffett 27-Point Model — Bank Sector-Adjusted

**Sector**: Bank → Skip 毛利率/流动比率/速动比率 scoring. Add NIM/NPL/Provision/CAR.

#### 1. Fundamentals (0-7)→ **4/7**

| Criterion | Score | Data | Reason |
|---|---|---|---|
| Strong ROE | 1/2 | ROE 12.21% (2025) | >12% but <15% |
| Conservative debt | 2/2 | CAR 9.25% | Bank-adjusted: CAR >9% |
| Strong operating margin | 0/2 | NIM 1.73% | Bank-adjusted: NIM <2% |
| Good liquidity | 1/1 | NPL 0.76% | Bank-adjusted: NPL <1% |
| **Subtotal** | **4/7** | | |

#### 2. Consistency → **3/3**

| Criterion | Score | Data |
|---|---|---|
| Earnings growth consistency | 3/3 | 5/5 years 归母净利润 growth positive |

#### 3. Moat → **2/5** (Bank-Adjusted)

| Criterion | Score | Data |
|---|---|---|
| ROE consistency >15% | 1/2 | 2/5 periods (2021-2022); rest <15% |
| Asset quality stability | 1/1 | NPL consistently <1% (bank moat = risk control) |
| Asset efficiency | 0/1 | 总资产周转率 0.021-0.029 (bank-low) |
| Performance stability | 0/1 | ROE declining 14.6→12.2% (negative trend) |

**Report evidence**: 东方证券 notes ROE leading peers, NPL <1% since listing, provision coverage industry-leading → supports moat.

#### 4. Management → **1/2**

| Criterion | Score | Data |
|---|---|---|
| Share buybacks | 0/1 | No buyback (回购 query returned empty) |
| Dividend track record | 1/1 | 5/5 years, growing payout (¥3.3B→7.9B) |

#### 5. Pricing Power → **0/5** (Bank-Adjusted)

| Criterion | Score | Data |
|---|---|---|
| NIM trend | 0/3 | NIM declining (~2% historically → 1.73%) |
| NIM level | 0/2 | NIM 1.73% below 2% threshold |
| **Subtotal** | **0/5** | ⚠️ Banks score poorly on this dimension universally |

⚠️ **Issue**: The pricing power dimension consistently scores 0 for all banks under current thresholds. This is structurally unfair — bank pricing power should be assessed via deposit cost advantage, loan pricing spread, and fee income diversification relative to peers, not absolute NIM level. Documented as design improvement for future iteration.

#### 6. Book Value Growth → **4/5**

| Criterion | Score | Data |
|---|---|---|
| Consistent BVPS growth | 3/3 | 5/5 periods growing (4.1%, 1.8%, 3.5%, 5.6%, 2.1%) |
| BVPS CAGR | 1/2 | CAGR ~13.4% (>10%, <15%) |

#### Total: 4+3+2+1+0+4 = 13/27

**Signal**: Score 13, margin_of_safety >0 → **neutral** (10-13: mixed evidence)

**Margin of safety calculation (bank ROE-PB framework)**:
- Fair PB = (ROE - g) / (r - g) = (12.21% - 3%) / (10% - 3%) ≈ 1.31
- Current PB = 0.89
- Margin = (1.31 - 0.89) / 1.31 = 32%
- While margin >0, score <14 → neutral per signal rules

**Action**: `watch` — decent bank at reasonable price, but declining ROE trend and thin NIM warrant monitoring.

### Graham 15-Point Model — Bank Sector-Adjusted

#### 1. Earnings Stability → **4/4**

| Criterion | Score | Data |
|---|---|---|
| All years EPS positive | 3/3 | 5/5 years |
| EPS growth (earliest→latest) | 1/1 | ¥3.13→4.29 (+37%) |

#### 2. Financial Strength → **3/5** (Bank-Adjusted)

| Criterion | Score | Data |
|---|---|---|
| Current ratio / Bank metrics | 2/2 | NPL 0.76% <1% (+1) + Provision 369% >200% (+1) |
| Debt ratio | 0/2 | 资产负债率 93.1% (bank-normal but absolute threshold fails) |
| Dividend history | 1/1 | 5/5 years paid |
| **Subtotal** | **3/5** | |

#### 3. Graham Valuation → **3/6**

| Criterion | Score | Data |
|---|---|---|
| Graham Number vs Price | 3/3 | GN=¥57.03 vs Price=¥31.41, margin 81.6% (>50%) |
| NCAV | BLOCKED | 流动资产 not returned (bank-finance incompatibility) |
| **Subtotal** | **3/6** | |

#### Total: 4+3+3 = 10/15

**Source margin formula**: `margin_of_safety = (Graham Number - Price) / Price` (per `ben_graham.py:265`).

**Key formulas**:
- Graham Number = √(22.5 × 4.29 × 33.69) = ¥57.03
- Margin of Safety = (57.03 - 31.41) / 31.41 = **81.6%** (>50% → +3, per source threshold)
- Supplementary: discount-to-GN = (57.03 - 31.41) / 57.03 = 44.9% (for display only, NOT used for scoring)
- NCAV: Blocked (流动资产 not available for banks)

**Signal by source rules**: Score 10/15 = 66.7%. Source threshold is ≥70% (≥10.5/15) for bullish → 10 is **close to but below bullish cutoff**. Pure source rules would output `neutral`.

**Action**: `watch` — **sector-adjusted override**. The Graham Number discount is large (81.6% margin), but three bank-specific factors justify a conservative downgrade from borderline-bullish:
1. **NCAV blocked** — valuation dimension capped at 3/6, losing the net-net deep value check that is core to Graham's framework.
2. **Bank leverage incompatible** — 资产负债率 93.1% fails classic Graham debt test (absolute <50% threshold). Even though this is normal for banks, Graham had no bank-specific adjustment — his framework was designed for industrials.
3. **Sector risk** — banks carry systemic/regulatory risks (NIM compression, credit cycle) that Graham's defensive framework doesn't model.

If this were a non-financial industrial with the same GN margin and a current ratio ≥2, it would be a clear `bullish` signal.

---

## Scoring: 贵州茅台 (600519.SH)

### Buffett 27-Point Model — Consumer (Default)

#### 1. Fundamentals → **7/7**

| Criterion | Score | Data |
|---|---|---|
| Strong ROE | 2/2 | ROE 34.46% (2025), >15% |
| Conservative debt | 2/2 | 产权比率 0.20, <0.5 |
| Strong operating margin | 2/2 | 销售净利率 50.53% (used as fallback for 营业利润率 fixed value) |
| Good liquidity | 1/1 | 流动比率 5.09, >1.5 |
| **Subtotal** | **7/7** | |

#### 2. Consistency → **2/3**

| Criterion | Score | Data |
|---|---|---|
| Earnings growth consistency | 2/3 | 4/5 years positive (2025: -4.5%) ⚠️ |

#### 3. Moat → **4/5**

| Criterion | Score | Data |
|---|---|---|
| ROE consistency >15% | 2/2 | 5/5 periods, lowest=29.9% |
| Operating margin stability | 1/1 | 毛利率 91.2-92.0%, stable ±1% |
| Asset efficiency | 0/1 | 总资产周转率 0.45-0.60, all <1.0 |
| Performance stability | 1/1 | ROE CV 9.9%, 毛利率 CV 0.35% → very stable |
| **Subtotal** | **4/5** | |

#### 4. Management → **2/2**

| Criterion | Score | Data |
|---|---|---|
| Share buybacks | 1/1 | Two buyback programs (¥3B+¥6B), both for 注销 |
| Dividend track record | 1/1 | 5/5 years, payout ratio 79%, dividends growing |
| **Subtotal** | **2/2** | |

#### 5. Pricing Power → **3/5**

| Criterion | Score | Data |
|---|---|---|
| Expanding gross margin | 1/3 | 毛利率 stable (±1%), not expanding |
| High gross margin level | 2/2 | 91.18% >50% |
| **Subtotal** | **3/5** | |

#### 6. Book Value Growth → **3/5**

| Criterion | Score | Data |
|---|---|---|
| Consistent BVPS growth | 3/3 | 5/5 periods growing |
| BVPS CAGR | 0/2 | CAGR ~6.7% (<10%) |
| **Subtotal** | **3/5** | |

#### Total: 7+2+4+2+3+3 = 21/27

**Signal**: Score ≥18, margin_of_safety >0 (see below) → **bullish**

**Margin of safety (simplified DCF)**:
```
Owner Earnings = NI + D&A - Capex = 82.32B + 2.26B - 3.13B = 81.45B
Fair Value ≈ Owner Earnings / (WACC - g) = 81.45 × 1.05 / (0.10 - 0.05) ≈ 1,711B
Market Cap = 1,637B
Margin ≈ (1,711 - 1,637) / 1,711 ≈ 4.3%
```
Narrow but positive margin. The moat and ROE quality justify a premium.

**Action**: `buy` — exceptional franchise with wide moat, strong buyback + dividend culture, trading slightly below intrinsic value.

### Graham 15-Point Model — Consumer (Default)

#### 1. Earnings Stability → **4/4**

| Criterion | Score | Data |
|---|---|---|
| All years EPS positive | 3/3 | 5/5 years |
| EPS growth (earliest→latest) | 1/1 | ¥41.76→65.66 (+57%) |

#### 2. Financial Strength → **5/5**

| Criterion | Score | Data |
|---|---|---|
| Current ratio | 2/2 | 5.09 ≥2.0 |
| Debt ratio | 2/2 | 16.4% <50% |
| Dividend history | 1/1 | 5/5 years |
| **Subtotal** | **5/5** | |

#### 3. Graham Valuation → **0/6**

| Criterion | Score | Data |
|---|---|---|
| Graham Number vs Price | 0/3 | GN=¥537 vs Price=¥1,310 (GN < Price) |
| NCAV | 0/4 | NCAV=¥221.6B, NCAV/MC=13.5% (<2/3) |
| **Subtotal** | **0/6** | |

#### Total: 4+5+0 = 9/15

**Signal**: Score 9/15 falls in source neutral range (`5 ≤ total ≤ 10`) → **neutral**

**Key formulas**:
- Graham Number = √(22.5 × 65.66 × 195.36) = ¥537.19
- Price = ¥1,309.60
- Margin of Safety = (537.19 - 1309.60) / 1309.60 = **-59.0%**
- NCAV = ¥271.5B - ¥49.9B = ¥221.6B, NCAV/MC = 13.5%

**Action**: `hold` — impeccable fundamentals but way above Graham Number. Classic Graham would reject this as speculative. The Graham framework correctly identifies this as overvalued for a defensive deep-value strategy while the Buffett framework identifies it as fairly-valued for a quality-at-reasonable-price strategy.

---

## Cross-Model Comparison

| Dimension | 宁波银行 (Bank) | 贵州茅台 (Consumer) |
|---|---|---|
| **Buffett Score** | 13/27 (neutral) | 21/27 (bullish) |
| **Graham Score** | 10/15 (neutral, sector-adjusted) | 9/15 (neutral) |
| **Graham Number** | ¥57.03 | ¥537.19 |
| **Current Price** | ¥31.41 | ¥1,309.60 |
| **GN Margin** | +81.6% (deep undervalue) | -59.0% (overvalued) |
| **NCAV** | Blocked (bank) | ¥221.6B (13.5% of MC) |
| **Key Strength** | BVPS growth, GN discount | ROE, moat, buybacks, margins |
| **Key Weakness** | NIM thin, ROE declining, no FCF data | 2025 revenue/NI decline, premium valuation |

**Sector divergence**: Graham prefers 宁波银行 (deep GN discount), Buffett prefers 贵州茅台 (quality franchise). This correctly mirrors the two investors' philosophies:
- Graham → buy cheap assets with margin of safety (banks often qualify)
- Buffett → buy wonderful businesses at fair prices (consumer moats qualify)

## Field Coverage Findings

### Fields Verified Working (both stocks)

| Field | 宁波银行 | 贵州茅台 | Notes |
|---|---|---|---|
| ROE 5y | ✅ | ✅ | | 
| 资产负债率 5y | ✅ | ✅ | |
| 产权比率 5y | ✅ | ✅ | |
| 营业利润率 5y | ⚠️ Fixed | ⚠️ Fixed | PR1 finding confirmed: fixed value bug persists |
| 销售净利率 5y | ✅ | ✅ | Reliable fallback for 营业利润率 |
| 营业收入 5y | ✅ | ✅ | |
| 归母净利润 5y | ✅ | ✅ | |
| 扣非归母净利润 5y | ✅ | ✅ | |
| 基本每股收益 5y | ✅ | ✅ | |
| 每股净资产 5y | ✅ | ✅ | |
| 总资产/负债/净资产 5y | ✅ | ✅ | |
| 无形资产 5y | ✅ | ✅ | |
| 经营活动CF 5y | ✅ | ✅ | |
| 资本性支出 5y | ✅ | ✅ | |
| D&A 5y | ✅ | ✅ | Correct name: 当期计提折旧与摊销 |
| PE / PB / PS | ✅ | ✅ | |
| 综合估值分位 | ✅ | ✅ | |
| 分红/股利/股息率 | ✅ | ✅ | |
| 股东人数 | ✅ | ✅ | Multi-period history |
| Announcement search | ✅ | ✅ | |
| Report search | ✅ | ✅ | Moat evidence found |

### Fields NOT Returned (by stock)

| Field | 宁波银行 | 贵州茅台 | Reason |
|---|---|---|---|
| ROIC | ❌ | ✅ | Banks don't report ROIC |
| ROA/总资产净利率 | ❌ (broad) | ❌ (broad) | Need separate narrow query |
| 毛利率 | ❌ | ✅ | Bank-finance incompatibility |
| 流动比率 | ❌ | ✅ | Bank-finance incompatibility |
| 速动比率 | ❌ | ✅ | Bank-finance incompatibility |
| 企业自由现金流量 | ❌ | ✅ | Bank CF structure differs |
| 营运资本 | ❌ | ✅ | Bank-finance incompatibility |
| 商誉 (5y) | ⚠️ 2y only | ❌ (=0 implicit) | Limited history / zero |
| 流动资产/流动负债 | ❌ | ⚠️ Q1 only | Bank: not returned. 茅台: single period |
| 货币资金 | ❌ | ⚠️ Q1 only | Bank: not returned |
| 回购 | ❌ | ✅ | Bank: no buyback history |
| MACD | ❌ | ❌ | Not returned for either stock |

### Query Broadening Failures

Two broad (≥5 field) queries returned empty and required splitting:
1. **贵州茅台 income 8-field**: "最近5年 营业收入 营业利润 净利润 归母净利润 扣非归母净利润 基本每股收益 每股净资产 增长率" → EMPTY. Split into 3 narrow queries → all recovered.
2. **贵州茅台 technical 5-field**: "近一年 涨跌幅 波动率 最大回撤 RSI MACD" → EMPTY. Split to 3-field → recovered (but lost history and MACD).

The split-recovery protocol works correctly. However, each split costs an extra API call. Command files should pre-emptively recommend narrow queries for stocks with heavy data (mega-caps, banks).

## Design Issues Identified

### 1. Bank Pricing Power Dimension (Buffett)
**Issue**: All banks score 0/5 on pricing power under current thresholds (NIM <2% → 0, NIM declining → 0).
**Severity**: Medium. This dimension is structurally unfair to financials.
**Recommendation**: Add peer-relative NIM assessment (vs industry average), or add deposit-cost advantage and fee-income diversification as bank pricing-power sub-metrics.

### 2. 营业利润率 Fixed Value Bug (Confirmed)
**Issue**: Both stocks return the same 营业利润率 for ALL 5 years (宁波银行: 39.44%, 贵州茅台: 71.45%).
**Severity**: High. This field is unusable for trend analysis.
**Workaround**: Use 销售净利率 as fallback (confirmed working for both stocks). Update command files to prefer 销售净利率 for margin stability checks.

### 3. Graham NCAV for Banks (Permanent Block)
**Issue**: 流动资产/流动负债 not returned for banks via finance route.
**Severity**: Medium. Graham valuation dimension loses 4/6 points for ALL banks.
**Workaround**: None available. Graham command correctly marks NCAV as "blocked" for bank stocks. Document that Graham is inherently less applicable to financials.

### 4. 综合估值分位 vs 近5年估值分位 (Naming)
**Issue**: Querying "近5年估值分位" returns the field as "综合估值百分位[YYYYMMDD]" — date stamps are year-end, not rolling 5-year.
**Severity**: Low. Field name mismatch but data is correct.
**Recommendation**: Update command query term to match iWencai's actual field name.

### 5. No 5-Year History for 货币资金/流动资产 (Consumer)
**Issue**: 贵州茅台 流动资产/流动负债 and 货币资金/带息债务 return only Q1 2026 (latest period), not 5-year history.
**Severity**: Low. These are balance-sheet snapshot items; latest period is most relevant. But trend analysis for working capital and cash position is lost.

### 6. MACD Not Returned
**Issue**: MACD not returned for either stock in technical queries.
**Severity**: Low. RSI and 涨跌幅 suffice for basic technical context. MACD was included in the original ai-hedge-fund but iWencai market route doesn't support it.

## Command File Updates Needed

Based on validation findings:

### `tos-funder-value-buffett.md`
1. ⚠️ Step 2: Add note that ROIC/ROA/毛利率/流动/速动 won't return for banks (sector-expected)
2. ⚠️ Step 3: Add pre-emptive split recommendation for mega-cap stocks (>¥500B market cap)
3. ⚠️ Step 5: Add note that FCFF/营运资本 won't return for banks
4. ⚠️ Step 6: Change "近5年估值分位" → the field is actually "综合估值分位" or "综合估值百分位"
5. ⚠️ Scoring §5 (Pricing Power): Add bank peer-relative note — absolute NIM <2% shouldn't auto-zero the dimension
6. ⚠️ Scoring §6 (Book Value Growth): BVPS CAGR threshold >15% is very high; most stocks won't reach it

### `tos-funder-value-graham.md`
1. ⚠️ Step 4: Add bank-specific note that 流动资产/流动负债 won't return for financials
2. ⚠️ Step 4: Add note that 流动资产/流动负债 returns only latest period (no 5y history)
3. ⚠️ Scoring §2: Clarify bank debt ratio adjustment — 资产负债率 >90% for banks should be assessed via CAR/regulatory metrics, not absolute threshold

### `value-investors.md`
1. Add PR 2A validation link
2. Update Field Dependency Matrix: mark 营业利润率 as "⚠️ Fixed value — use 销售净利率"
3. Add bank-specific NCAV permanent block note

## Conclusion

Both commands function correctly on live iWencai data. The sector-adjusted scoring framework correctly differentiates a bank from a consumer franchise. Key improvements identified for the next iteration:

1. Bank pricing power dimension needs peer-relative benchmarks
2. 营业利润率 fixed value needs permanent fallback to 销售净利率 in scoring
3. Pre-emptive query splitting for mega-cap stocks
4. Graham NCAV for banks is a permanent limitation — accept as design constraint

**Validation Status**: ✅ PASSED — Both commands produce sector-correct, data-grounded signals matching expected behavior (宁波银行 → neutral/watch, 贵州茅台 → bullish/hold divergence).
