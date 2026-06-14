# PR 3A Validation: Quant Fundamentals + Price Normalizer

**Date**: 2026-06-02
**Samples**: 宁波银行 (002142.SZ, Bank), 贵州茅台 (600519.SH, Consumer), 比亚迪 (002594.SZ, High-Capex Industrial)
**Status**: ✅ Validated; price-normalizer implementation direction superseded by TDX/mootdx architecture update.

**Architecture update after validation**: This document remains useful as evidence that iWencai can return OHLCV, but Trading Funder no longer uses iWencai as the primary technical/risk price-series source. Use `tos-funder/commands/tos-funder-quant-price-series.md` and `tos-funder/references/price-series.md` for the current TDX/mootdx path. Treat the iWencai normalizer result here as fallback-only.

## Executive Summary

Both commands work correctly on live iWencai data. The 4-category quant scoring model produces sector-adjusted signals that align with expectations: 宁波银行 (bullish — cheap bank with decent fundamentals), 贵州茅台 (neutral — excellent profitability offset by growth stall and premium valuation), 比亚迪 (bearish — multiple compression + growth deceleration). The Price Normalizer successfully normalizes single-row OHLCV JSON for all 3 stocks.

| Stock | Sector | Quant Fundamentals | Price Normalizer |
|---|---|---|---|
| 宁波银行 | Bank | 2B/0B → **bullish** (50%) | ✅ good (242 dates, 6 fields) |
| 贵州茅台 | Consumer | 2B/2B → **neutral** (50%) | ✅ good (~250 dates, 6 fields) |
| 比亚迪 | High-Capex Industrial | 0B/2B → **bearish** (50%) | ✅ good (~250 dates, 6 fields) |

## Sample 1: 宁波银行 (002142.SZ) — Bank

### Routes Used
- `basicinfo`: ✅ Identity (银行→城商行, 总市值 ¥207.4B)
- `finance`: ✅ Profitability, income/growth, balance sheet, cash flow
- `market`: ✅ Valuation (PE 6.89, PB 0.89), OHLCV 250d ✅
- `management`: ✅ 分红/股本/股东人数

### Fields Returned
- ROE 5y: 14.59→14.56→13.85→12.49→12.21
- 销售净利率 5y: 37.16→39.97→41.58→40.85→41.03
- 营业收入同比增长率: 8.01%
- 归母净利润同比增长率: 8.13%
- 每股净资产环比增长率: 2.12%
- 资产负债率: 93.15%
- 产权比率: 13.67
- 经营活动CF: 5y (4/5 positive)
- PE 6.89, PB 0.89
- Bank-specific: NIM 1.73%, NPL 0.76%, Provision 369%, CAR 9.25%
- OHLCV: 242 dates, 6 fields/date ✅

### Fields Missing
- ROIC, ROA, 毛利率, 流动比率, 速动比率 (bank-sector expected)
- 企业自由现金流量 (bank CF structure)
- 成交额 (not returned in OHLCV query)
- PS (not returned, not meaningful for banks)
- 回购 (empty)

### Query Rewrites
- None needed — all queries returned data on first attempt.

### Quant Fundamentals Score

#### Profitability: 1/2 (bank max) → `neutral`

| # | Metric | Value | Bank Threshold | Pass |
|---|---|---|---|---|
| 1 | ROE | 12.21% | >12% | ✅ +1 |
| 2 | Net Margin → NIM | 1.73% | >2% | ❌ 0 |
| 3 | Op Margin | skip (bank) | — | — |

Details: ROE at bank-adequate level. NIM thin at 1.73% (below 2% threshold). Bank-adjusted scoring caps at 2.

#### Growth: 1/3 → `neutral`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | Revenue Growth | 8.01% | >5% (bank) | ✅ +1 |
| 2 | Earnings Growth | 8.13% | >10% | ❌ 0 |
| 3 | BVPS Growth | 2.12% | >10% | ❌ 0 |

Details: Revenue growth healthy for a mature bank. Earnings growth below 10% threshold. BVPS growth modest but positive.

#### Financial Health: 3/3 (bank-adjusted) → `bullish`

| # | Metric | Value | Bank Threshold | Pass |
|---|---|---|---|---|
| 1 | Current Ratio → Bank metrics | NPL 0.76%, Prov 369% | NPL<1%, Prov>200% | ✅✅ +2 |
| 2 | D/E → CAR | 9.25% | >9% | ✅ +1 |
| 3 | FCF → OCF stability | 4/5 years positive | ≥4/5 | ✅ +1 |

Details: Excellent asset quality (NPL 0.76%, provision coverage 369%). CAR adequate at 9.25%. OCF stable (only 2021 negative).

#### Price Ratios: 0/2 ratios exceed → `bullish`

| # | Metric | Value | Bank Threshold | Exceeds? |
|---|---|---|---|---|
| 1 | PE | 6.89 | <10 | ❌ (cheap) |
| 2 | PB | 0.89 | <1.0 | ❌ (below book) |
| 3 | PS | N/A | skip | — |

Details: Trading below book value (PB 0.89). PE 6.89 is cheap for a bank with 12% ROE. PS skipped (bank sector).

#### Overall Signal

| Category | Signal |
|---|---|
| Profitability | neutral |
| Growth | neutral |
| Financial Health | bullish |
| Price Ratios | bullish |

**Bullish: 2, Bearish: 0 → `bullish` (confidence: 50%)**

Risk flags: None triggered (EPS positive, OCF mostly positive, bank leverage is sector-normal).

**Action**: `watch` (bullish signal but low confidence — thin NIM and declining ROE trend warrant monitoring).

#### Quant vs Value Divergence

The quant model is bullish on 宁波银行 while Buffett (13/27 neutral) and Graham (10/15 neutral) are neutral. This divergence is valid:

- **Quant model** sees: cheap price (PE 6.89, PB 0.89), adequate financial health (low NPL, high provision), modest growth.
- **Value models** add: moat concerns (ROE declining, NIM thin), management score (no buyback), and bank sector risks (systemic/regulatory) that the quant model doesn't capture.

The quant fundamentals signal serves as a baseline — persona agents layer on qualitative and sector-risk adjustments.

---

## Sample 2: 贵州茅台 (600519.SH) — Consumer

### Routes Used
- `basicinfo`: ✅ Identity (食品饮料→白酒, 总市值 ¥1,637B)
- `finance`: ✅ Profitability, income/growth (split into 3 narrow queries), balance sheet, cash flow
- `market`: ✅ Valuation (PE 19.79, PB 6.04, PS 7.48), OHLCV 250d ✅
- `management`: ✅ 分红/股本/股东人数, 回购

### Fields Returned
- ROE 5y: 29.90→32.41→36.18→38.43→34.46
- ROIC 5y: 27.44→29.40→33.49→35.19→31.50
- 销售净利率 5y: 52.47→52.68→52.49→52.27→50.53
- 销售毛利率 5y: 91.54→91.87→91.96→91.93→91.18
- 流动比率 5y: 3.81→4.41→4.62→4.45→5.09
- 速动比率 5y: ✅
- 营业收入同比增长率: -1.21%
- 归母净利润同比增长率: -4.53%
- 每股净资产环比增长率: 5.28% (computed)
- 产权比率: 0.20
- 资产负债率: 16.42%
- 企业自由现金流量 5y: all positive (30B→76B)
- 经营活动CF 5y: all positive
- PE 19.79, PB 6.04, PS 7.48
- OHLCV: ~250 dates, 6 fields/date ✅

### Fields Missing
- ROA (not in broad query)
- 营业利润率 → FIXED VALUE (71.45% all years) — NOT USED
- 成交额 (not returned in OHLCV query)

### Query Rewrites
1. Income 8-field broad query returned EMPTY → split into 3 narrow queries (revenue+NI+EPS+BVPS; operating profit+NI; growth rates) → all recovered.

### Quant Fundamentals Score

#### Profitability: 3/3 → `bullish`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | ROE | 34.46% | >15% | ✅ +1 |
| 2 | Net Margin | 50.53% | >20% | ✅ +1 |
| 3 | Op Margin (销售净利率) | 50.53% | >15% | ✅ +1 |

Details: Exceptional profitability. ROE 34.5%, net margin 50.5%. Both metrics far above thresholds.

#### Growth: 0/3 → `bearish`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | Revenue Growth | -1.21% | >10% | ❌ 0 |
| 2 | Earnings Growth | -4.53% | >10% | ❌ 0 |
| 3 | BVPS Growth | 5.28% | >10% | ❌ 0 |

Details: **First revenue and earnings decline in 5 years** (2025). Revenue -1.2%, NI -4.5%, BVPS growth slowed to 5.3%. Growth dimension flags a stall — concerning for a premium-multiple stock.

#### Financial Health: 3/3 → `bullish`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | Current Ratio | 5.09 | >1.5 | ✅ +1 |
| 2 | D/E | 0.20 | <0.5 | ✅ +1 |
| 3 | FCF | ¥76.1B >0 | >0 | ✅ +1 |

Details: Impeccable balance sheet. Massive liquidity (CR 5.09), near-zero leverage (D/E 0.20), strong positive FCF (¥76.1B).

#### Price Ratios: 2/3 ratios exceed → `bearish`

| # | Metric | Value | Threshold | Exceeds? |
|---|---|---|---|---|
| 1 | PE | 19.79 | <25 | ❌ (reasonable) |
| 2 | PB | 6.04 | <3 | ✅ (expensive) |
| 3 | PS | 7.48 | <5 | ✅ (expensive) |

Details: PE reasonable at 19.8x. PB (6.04x) and PS (7.48x) both exceed thresholds — premium valuation. No high-growth relaxation (revenue growth -1.2%).

#### Overall Signal

| Category | Signal |
|---|---|
| Profitability | bullish |
| Growth | bearish |
| Financial Health | bullish |
| Price Ratios | bearish |

**Bullish: 2, Bearish: 2 → `neutral` (confidence: 50%)**

Risk flags: Growth bearish (revenue -1.2%, earnings -4.5%). EPS still positive (65.66) → no hard veto.

**Action**: `hold` — exceptional business (profitability + financial health are pristine) but growth stall + premium valuation offset. Wait for either growth recovery or price correction.

---

## Sample 3: 比亚迪 (002594.SZ) — High-Capex Industrial

### Routes Used
- `basicinfo`: ✅ Identity (汽车→乘用车, 总市值 ¥799.6B)
- `finance`: ✅ Profitability, income/growth, balance sheet, cash flow
- `market`: ✅ Valuation (PE 30.99, PB 3.68), OHLCV 250d ✅
- `management`: ✅ 分红/股本/股东人数, 回购

### Fields Returned
- ROE 5y: 4.01→16.13→24.05→24.84→15.12
- ROIC 5y: 3.90→12.06→17.72→18.64→10.81
- 销售毛利率 5y: 13.02→17.04→20.21→19.44→17.74
- 销售净利率 5y: 1.84→4.18→5.20→5.35→4.20
- 速动比率 5y: 0.65→0.42→0.44→0.47→0.38
- 总资产周转率 5y: 0.87→1.07→1.03→1.06→0.96
- 流动比率 (separate query): 0.82 (Q1 2026 only)
- 流动资产/流动负债/货币资金/带息债务: 5y history ✅
- 营业收入同比增长率: 3.46%
- 归母净利润同比增长率: -18.97%
- 每股净资产环比增长率: 3.49%
- 产权比率: 2.54
- 资产负债率: 70.74%
- 企业自由现金流量: Negative 3 of 5 years (-70.9B latest)
- 经营活动CF: Positive all 5 years
- PE 30.99, PB 3.68
- OHLCV: ~250 dates, 6 fields/date ✅

### Fields Missing
- 流动比率 NOT in broad ratio query → separate query returned Q1 2026 only (0.82), no 5y history
- 营业利润率 → FIXED VALUE (2.44% all years) — NOT USED
- PS → NOT RETURNED in market valuation query
- 成交额 → NOT returned in OHLCV query

### Notable Observations
1. **Stock split in 2025**: 总股本 jumped from 2.91B→3.04B→5.49B→9.12B. EPS dropped from 13.84→3.58. Per-share metrics distorted. Using total 归母净利润 growth for earnings check.
2. **Growth deceleration**: Revenue growth from 96%→42%→29%→3.5%. Massive slowdown.
3. **Earnings contraction**: 归母净利润 from ¥40.3B→¥32.6B (-19%). First decline since 2021.
4. **Heavy capex**: 资本性支出 ¥157B in 2025 (vs ¥97B in 2024). FCFF deeply negative (-¥70.9B).
5. **Buyback history**: Two buyback records (¥1.81B for ESOP, ¥400M for cancellation).

### Query Rewrites
1. 流动比率 not in broad ratio query → separate narrow query → returned Q1 2026 only.
2. Income 7-field query succeeded on first attempt (no split needed — unlike 贵州茅台).

### Quant Fundamentals Score

#### Profitability: 1/3 → `neutral`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | ROE | 15.12% | >15% | ✅ +1 |
| 2 | Net Margin | 4.20% | >20% | ❌ 0 |
| 3 | Op Margin (销售净利率) | 4.20% | >15% | ❌ 0 |

Details: ROE just above 15% threshold. Margins thin at 4.2% net — typical for auto manufacturing (high revenue, low margin).

#### Growth: 0/3 → `bearish`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | Revenue Growth | 3.46% | >10% | ❌ 0 |
| 2 | Earnings Growth (total NI) | -18.97% | >10% | ❌ 0 |
| 3 | BVPS Growth | 3.49% | >10% | ❌ 0 |

Details: All growth metrics below threshold. Revenue growth collapsed from 96% to 3.5%. Earnings contracted 19%. Stock split partially distorts per-share metrics but total NI also declined.

#### Financial Health: 1/3 (high-capex adjusted) → `neutral`

| # | Metric | Value | Threshold | Pass |
|---|---|---|---|---|
| 1 | Current Ratio | 0.82 (Q1 2026) | >1.5 | ❌ 0 |
| 2 | D/E | 2.54 | <0.5 | ❌ 0 |
| 3 | FCF → OCF proxy | OCF/NI = 1.81 | >0.8 | ✅ +1 |

Details: Current ratio below 1.0 (but >0.5, no hard veto). High leverage (D/E 2.54, debt ratio 70.7%) — typical for capex-heavy auto. OCF conversion is strong (1.81× NI). FCFF negative due to massive investment (¥157B capex).

#### Price Ratios: 2/2 ratios exceed → `bearish`

| # | Metric | Value | Threshold | Exceeds? |
|---|---|---|---|---|
| 1 | PE | 30.99 | <25 (no growth relaxation) | ✅ (expensive) |
| 2 | PB | 3.68 | <3 | ✅ (expensive) |
| 3 | PS | N/A | — | blocked |

Details: Both PE and PB above thresholds. Revenue growth 3.5% does not qualify for high-growth PE relaxation (<50 threshold requires >30% growth). PS not returned → blocked.

#### Overall Signal

| Category | Signal |
|---|---|
| Profitability | neutral |
| Growth | bearish |
| Financial Health | neutral |
| Price Ratios | bearish |

**Bullish: 0, Bearish: 2 → `bearish` (confidence: 50%)**

Risk flags:
- Soft veto: OCF healthy (5/5 positive) — no OCF-triggered downgrade
- Current ratio 0.82 <1.0 but >0.5 → no hard veto
- D/E 2.54 high but <3.0 for industrial → no hard veto
- EPS positive (3.58) → no earnings veto

**Action**: `reduce` — bearish signal driven by growth deceleration, margin compression, and above-threshold valuation. The stock split adjustment dampens per-share metrics, but total NI decline confirms weakening fundamentals.

⚠️ **Stock split caveat**: The 2025 送转/stock split distorts per-share comparisons. Using total NI growth (-19%) instead of EPS growth (-22%) for the earnings check partially mitigates this, but BVPS growth remains distorted. A split-adjusted restatement would improve accuracy.

---

## Price Normalizer Validation

### Data Format Confirmation

All 3 stocks confirmed the same field name behavior:

| Query Term | Returned Field | Pattern |
|---|---|---|
| 前复权开盘价 | `开盘价[YYYYMMDD]` | Drops "前复权" prefix |
| 前复权最高价 | `最高价[YYYYMMDD]` | Drops "前复权" prefix |
| 前复权最低价 | `最低价[YYYYMMDD]` | Drops "前复权" prefix |
| 前复权收盘价 | `收盘价[YYYYMMDD]` | Drops "前复权" prefix |
| 成交量 | `成交量[YYYYMMDD]` | Direct |
| 换手率 | `换手率[YYYYMMDD]` | Direct |
| 成交额 | NOT RETURNED | ⚠️ Missing for all 3 |

### Coverage Summary

| Stock | Dates | Fields/Date | Missing Fields | Status |
|---|---|---|---|---|
| 宁波银行 | 242 | 6 (OHLCV+T) | 成交额 | `good` |
| 贵州茅台 | ~250 | 6 (OHLCV+T) | 成交额 | `good` |
| 比亚迪 | ~250 | 6 (OHLCV+T) | 成交额 | `good` |

**T = turnover_rate (换手率)**

All 3 stocks pass the `good` threshold (≥200 dates, ≥4 OHLC fields for ≥95%). The only consistently missing field is `成交额`.

### Normalizer Process Validated

The algorithm described in `price-series.md` correctly handles:
1. ✅ Field name regex matching: `开盘价[20260601]` → field=开盘价, date=20260601
2. ✅ Non-date fields filtered: 股票代码, 股票简称, 最新价, 最新涨跌幅
3. ✅ Date grouping: ~250 dates aggregated correctly
4. ✅ Field mapping: 开盘→open, 最高→high, 最低→low, 收盘→close, 成交量→volume, 换手率→turnover
5. ✅ Date sorting: ascending order
6. ✅ Data quality: 成交额 consistently flagged as missing

### Normalizer Output Sample (宁波银行, first 3 records)

```json
{
  "series": [
    {"date": "2025-06-02", "open": 31.26, "high": 31.50, "low": 30.78, "close": 31.41, "volume": 15230000, "turnover_rate": 0.85, "amount": null},
    {"date": "2025-06-03", "open": 31.50, "high": 31.72, "low": 31.20, "close": 31.65, "volume": 18900000, "turnover_rate": 1.02, "amount": null},
    {"date": "2025-06-04", "open": 31.70, "high": 32.10, "low": 31.55, "close": 31.80, "volume": 22100000, "turnover_rate": 1.18, "amount": null}
  ],
  "data_quality": {
    "total_dates": 242,
    "expected_dates": 250,
    "first_date": "2025-06-02",
    "last_date": "2026-06-01",
    "fields_per_date": {"open": 242, "high": 242, "low": 242, "close": 242, "volume": 242, "turnover_rate": 242, "amount": 0},
    "dates_missing": 8,
    "incomplete_records": 0,
    "status": "good"
  }
}
```

---

## Cross-Sample Analysis

### 营业利润率 Fixed Value: Confirmed in ALL 3 Samples

| Stock | 营业利润率 (all 5 years) | Actual Margin (销售净利率) |
|---|---|---|
| 宁波银行 | 39.44% | 37-41% |
| 贵州茅台 | 71.45% | 50-52% |
| 比亚迪 | 2.44% | 1.8-5.4% |

The 营业利润率 field returns a single fixed value for all 5 years in every stock. This is a systematic iWencai bug. The command correctly uses 销售净利率 as fallback — **this is permanently necessary**.

### 流动比率 Availability

| Stock | In Broad Query | Separate Query | Notes |
|---|---|---|---|
| 宁波银行 | ❌ | ❌ | Bank-nature — expected |
| 贵州茅台 | ✅ (5y) | — | Consumer standard |
| 比亚迪 | ❌ | ✅ (Q1 only) | Broad query dropped it; separate returns single period |

**Recommendation**: Always run a separate `流动比率` narrow query when the broad ratio query doesn't return it AND the stock is non-financial.

### PS Availability

| Stock | PS Returned |
|---|---|
| 宁波银行 | ❌ (bank, not meaningful) |
| 贵州茅台 | ✅ (7.48) |
| 比亚迪 | ❌ (missing from market route) |

PS is inconsistently returned. The command handles this by marking PS as `blocked` when missing.

### 成交额 in OHLCV

**ALL 3 stocks**: 成交额 NOT returned. This is a systematic gap in the iWencai market route. The normalizer correctly marks `amount` as null for all records.

### Sector Adjustments Applied

| Stock | Sector | Adjustments |
|---|---|---|
| 宁波银行 | Bank | Profitability: NIM replaces net margin. Financial Health: NPL+Provision replaces CR, CAR replaces D/E, OCF stability replaces FCF. Price: PE<10, PB<1.0, PS skipped. |
| 贵州茅台 | Consumer | None (default thresholds) |
| 比亚迪 | High-Capex Industrial | Financial Health: OCF margin replaces FCF (FCFF negative during investment phase). |

---

## Unresolved Issues for Architecture Review

### 1. Stock Split Distortion (比亚迪)
**Issue**: 比亚迪's 2025 送转 inflated 总股本 from 2.91B to 9.12B, causing per-share metrics (EPS, BVPS) to drop 70%+. The command uses total NI growth as a workaround, but BVPS growth remains distorted.
**Severity**: Medium. Affects any stock that had a stock split in the 5-year window.
**Proposed fix**: Detect split via 总股本 change >30% YoY, flag in data_quality, and compute split-adjusted per-share metrics using current 总股本 as the base.

### 2. 流动比率 Only Single-Period (Non-Financials)
**Issue**: For 比亚迪, 流动比率 was only returned for Q1 2026 (latest period), not 5-year history. Multi-year trend analysis for liquidity is blocked.
**Severity**: Low-Medium. Single-period CR is sufficient for the threshold check, but trend analysis (which the Graham command needs) is lost.
**Proposed fix**: Compute CR manually from 流动资产/流动负债 5y history (both were returned for 比亚迪). Update the command to prefer computed CR when available.

### 3. 成交额 Systematically Missing
**Issue**: 成交额 not returned in OHLCV queries for any of the 3 stocks.
**Severity**: Low. Volume × close can proxy for amount. However, for VWAP calculations and anomaly detection, actual 成交额 is preferred.
**Proposed fix**: Compute `amount_estimated = volume × close` in the normalizer and flag as `estimated`. Add a note in the downstream consumer that amount is estimated.

### 4. PS Not Consistently Returned
**Issue**: PS returned for 贵州茅台 but not 比亚迪. The market route's PS coverage is inconsistent.
**Severity**: Low. PS is the least critical of the three price ratios. The command handles missing PS by marking it `blocked`.

### 5. Bank Quant vs Value Divergence
**Issue**: The quant model outputs `bullish` on 宁波银行 while both Buffett and Graham output `neutral`. This divergence could confuse users if they see conflicting signals.
**Severity**: Low (design feature, not bug). The quant model is intentionally a simpler baseline. Documentation should explain that quant signals are raw factor assessments; persona agents add qualitative overlays.
**Proposed fix**: Add a note in the quant output: "This is a baseline factor signal. Persona agents (Buffett, Graham, etc.) may adjust based on moat, management quality, and sector risk considerations."

### 6. 营业利润率 Fixed Value (Systematic)
**Issue**: Confirmed on all 3 stocks (and all 5 PR1 stocks). This field is permanently unusable.
**Severity**: High for any command that unknowingly uses it. Mitigated by the permanent 销售净利率 fallback.
**Proposed fix**: Add 营业利润率 to a global "DO NOT USE" list in `iwencai-adapter.md`.

---

## Deliverable Summary

| File | Status | Description |
|---|---|---|
| `tos-funder/commands/tos-funder-quant-fundamentals.md` | ✅ Created | 4-category deterministic scoring with sector adjustments |
| `tos-funder/commands/tos-funder-quant-price-series.md` | ✅ Replaced | TDX/mootdx OHLCV collection, canonical schema, data quality |
| `tos-funder/references/quant-systematic.md` | ✅ Created | Shared query packs, field matrix, sector rules, output schema |
| `tos-funder/references/price-series.md` | ✅ Created | Raw format doc, normalizer algorithm, consumer interface |
| `docs/tos-funder/validation-pr3a.md` | ✅ Created | 3-sample validation with scores, normalizer test, issues |
