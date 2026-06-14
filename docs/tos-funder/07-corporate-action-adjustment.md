# Corporate Action / Adjustment Verification Protocol

Protocol for verifying whether mootdx qfq-adjusted price series faithfully reflect corporate actions (dividends, stock splits, rights issues, reverse splits). This protocol exists to prevent risk metrics (especially max drawdown) from being distorted by incomplete adjustment, which would cause false hard vetoes.

## Problem Statement

mootdx/TDX `--adjust qfq` returns a `factor` field per bar. When working correctly, multiple distinct factor values appear in the series, reflecting the cumulative adjustment ratio. However:

1. **Factor = 1.0 for all rows does NOT mean no corporate action occurred** — it may mean the adjustment engine didn't capture the event (e.g., capital actions from 送转/转增 that mootdx doesn't factor in).
2. **Factor ≠ 1.0 does NOT guarantee complete adjustment** — the factor covers dividends but may not cover complex capital actions.
3. **A price series with factor=1.0 and extreme regime change** (e.g., close drops from 400 to 100 in one day) is almost certainly a corporate action artifact, not a genuine price collapse.

## Trigger Conditions

The adjustment verification protocol activates when ANY of these conditions are met:

| # | Condition | Threshold | Rationale |
|---|-----------|-----------|-----------|
| T1 | Max single-day absolute return | >20% | Above the daily limit for most A-shares and beyond the normal limit for many boards. For 科创板/创业板 edge cases, use this as a data-quality trigger and cross-check before final classification. |
| T2 | Max drawdown | >50% | A 50%+ DD in a 1-year window may be genuine (bear market) or an adjustment artifact. Needs verification. |
| T3 | Factor homogeneity | All factor values == 1.0 | If no factor variation is returned but price regime changes are large, the adjustment path may not be active. |
| T4 | Regime shift | Median 1st half / Median 2nd half differs by >30% | A major price level change between halves of the series suggests a capital action between the periods. |

T1 is the strongest signal. T3 + any other trigger compounds suspicion.

## Classification

### adjustment_status

| Status | Criteria | Meaning |
|--------|----------|---------|
| `verified` | Factor has ≥2 distinct values AND max single-day return ≤20% AND max DD ≤50% AND no price gaps >20% | Adjustment path confirmed active. Risk metrics valid. |
| `acceptable` | Factor has ≥2 distinct values AND no single-day jumps >20% AND max DD ≤50% BUT minor gaps (5-10% single-day moves) or moderate regime shift (<30%) present | Adjustment likely correct but minor anomalies exist. Risk metrics mostly valid — flag anomalies in warnings. |
| `suspect` | Factor all == 1.0 AND (single-day jump >20% OR max DD >50% OR regime shift >30%) | Evidence of uncaptured corporate action. Risk metrics potentially distorted. |
| `unknown` | Cannot verify (data insufficient, <120 rows, or all triggers absent but factor=1.0 and max DD >30%) | Unclear whether adjustment path is correct. Treat as suspect for risk purposes. |

### corporate_action_warning

| Value | Condition |
|-------|-----------|
| `true` | adjustment_status is `suspect` or `unknown`, OR verified/acceptable but with documented anomalies (single-day gaps 10-20%, moderate regime shift) |
| `false` | adjustment_status is `verified` with no anomalies |

### risk_metric_status

| Status | Condition | Which Metrics Affected |
|--------|-----------|----------------------|
| `valid` | adjustment_status = verified or acceptable, no anomalies | All metrics fully valid |
| `degraded` | adjustment_status = suspect or unknown | **Full-series metrics degraded**: max_dd, downside_vol, vol_percentile. **Recent-window metrics valid**: current_dd (120d), vol_20d, vol_60d, VaR 95%. Correlation uses aligned returns — if distortion window is early in series, recent-aligned returns may be valid. |
| `blocked` | adjustment_status = suspect AND single-day jump >50% AND <120 clean rows remain after excluding distortion window | All metrics blocked — insufficient clean data |

### manual_review_required

| Value | Condition |
|-------|-----------|
| `true` | adjustment_status is `suspect` or `unknown` |
| `false` | adjustment_status is `verified` or `acceptable` |

## Verification Steps

### Step A: Factor Analysis

```
Count unique factor values in the cleaned price series.
If unique_factors >= 2 → adjustment path is active (dividend-level).
If unique_factors == 1 → adjustment path may not be active.
```

Caveat: factor covers dividend adjustments. Stock splits (送转) may not be reflected in factor values even when qfq is requested.

### Step B: Single-Day Return Scan

```
For each consecutive day pair:
    daily_return = abs(close[i] / close[i-1] - 1) * 100
    if daily_return > 20%:
        flag as potential_corporate_action_event
        record date[i], close[i-1], close[i], return_pct
```

A single-day return >20% on a non-科创板/创业板 stock is not explainable by normal trading limits alone. Treat it as a corporate-action/data-quality trigger and cross-check with dividend, split, rights, suspension, or relisting history before using full-series risk metrics.

### Step C: Regime Shift Detection

```
Split the cleaned close series into first half and second half.
median_1h = median(closes[:len//2])
median_2h = median(closes[len//2:])
regime_shift_pct = abs(median_2h / median_1h - 1) * 100
```

### Step D: Cross-Reference with Dividend History

When adjustment is `suspect`, query the dividend/corporate-action history:

```bash
.venv/bin/hoxit signals dividend <CODE> --page-size 10
```

Search for events within the price-series date range:
- `transfer_ratio` (转增比例): 每10股转增X股 → expect price ~divided by (1 + X/10)
- `bonus_ratio` (送股比例): 每10股送X股 → same effect as transfer
- `bonus_rmb` (每股派息): cash dividend → mild price adjustment (handled by factor)

**Cross-check rule**: If dividend history shows a 送转/转增 event within the price series window, and the price series shows a large single-day jump, AND factor=1.0 → this is a confirmed corporate action distortion, NOT a genuine price collapse.

### Step E: Determine Adjustment Status

Apply the decision tree:

```
if unique_factors >= 2 AND max_single_day_return <= 20 AND max_dd <= 50:
    adjustment_status = "verified"
    corporate_action_warning = false
elif unique_factors >= 2 AND max_single_day_return > 20:
    # Factors present but extreme jump — possible split factor not covered
    adjustment_status = "suspect"
    corporate_action_warning = true
elif unique_factors == 1 AND max_single_day_return <= 20 AND max_dd <= 50:
    # No adjustment evidence, but also no extreme moves — may be fine
    adjustment_status = "acceptable"  # if regime_shift < 30%
    adjustment_status = "unknown"     # if regime_shift >= 30%
    corporate_action_warning = (adjustment_status == "unknown")
elif unique_factors == 1 AND (max_single_day_return > 20 OR max_dd > 50):
    adjustment_status = "suspect"
    corporate_action_warning = true
else:
    adjustment_status = "unknown"
    corporate_action_warning = true
```

## Risk Metric Tier System

When `risk_metric_status` is `degraded`, apply the following tier rules:

### Tier 1: Valid (usable without restriction)

| Metric | Window | Reason |
|--------|--------|--------|
| vol_20d, vol_60d | Recent 20/60 days | Short-term vol unaffected by old adjustment events |
| current_dd | Recent 120 days | Peak/trough in recent window — adjustment artifact likely outside window |
| VaR 95% | Recent 20 days | Parametric VaR from recent returns |
| liquidity (amount/volume) | Recent 20 days | Unaffected by price adjustment |
| correlation (if aligned returns exclude distortion window) | Ex-distortion | If the extreme jump dates are excluded from aligned returns |

### Tier 2: Degraded (usable with warning, confidence reduction)

| Metric | Reason |
|--------|--------|
| max_dd | Peak/trough may span distortion event — value is upper bound, not accurate |
| downside_vol | Extreme negative returns from adjustment artifact inflate this metric |
| vol_percentile | Rolling window includes distorted returns — percentile may be mis-ranked |

### Tier 3: Blocked (do not use)

| Metric | Reason |
|--------|--------|
| max_dd (for hard veto) | Cannot veto on a metric that may be corporate-action artifact |

## Action Constraint Effects

| adjustment_status | risk_metric_status | Hard Vetoes | Position Sizing | Action Ceiling |
|---|---|---|---|---|
| verified | valid | All vetoes active | Standard formula | No ceiling |
| acceptable | valid | All vetoes active | Standard formula | No ceiling |
| suspect | degraded | max_dd veto → manual_review_required; current_dd veto still active | Use only Tier 1 metrics (recent-window vol, cur_dd) | `watch` (new), `reduce` (existing max) |
| unknown | degraded | All vetoes → manual_review_required | Conservative: cap at 50% of standard limit | `watch` (new), `reduce` (existing max) |
| suspect + <120 clean rows | blocked | All vetoes blocked | Blocked | `blocked` |

## Integration Points

| File | Integration |
|------|-------------|
| `tos-funder/references/price-series.md` | Add adjustment verification appendix summarizing this protocol |
| `tos-funder/commands/tos-funder-quant-price-series.md` | Add Step 6: Adjustment Verification Check, producing `adjustment_check` in output |
| `tos-funder/commands/tos-funder-risk-manager.md` | Add Step 2a: Adjustment Verification, replacing auto-veto with conditional tier system |
| `tos-funder/references/portfolio-synthesis.md` | Add data-quality veto category, distinguished from risk veto; degraded stocks → watch/reduce |
