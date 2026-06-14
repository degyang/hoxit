# PR10A Instruction — Macro / Top-Down Proxy

Created: 2026-06-03 10:34:39 Asia/Shanghai
Owner: CC implementation
Reviewer: Codex architecture/review
Status: Ready for CC

## Objective

Implement a lightweight A-share macro/top-down proxy for `tos-funder`.

This PR should enrich tactical analysis with market-regime context using only data that can be verified through current hoxit sources. It must **not** implement a full Druckenmiller strategy and must **not** claim true macro forecasting.

The goal is to produce a deterministic `macro_topdown_signal` from:

- index trend
- sector/industry relative strength
- market breadth proxy
- style rotation proxy
- risk-appetite proxy

If a data source is unavailable, document the gap and degrade the output. Do not fabricate macro data.

## Must Read First

Read these files before editing:

1. `docs/tos-funder/01-interface-coverage.md`
2. `tos-funder/references/iwencai-adapter.md`
3. `tos-funder/references/price-series.md`
4. `tos-funder/commands/tos-funder-quant-price-series.md`
5. `tos-funder/commands/tos-funder-quant-technicals.md`
6. `tos-funder/commands/tos-funder-risk-manager.md`
7. `tos-funder/commands/tos-funder-tactical.md`
8. `tos-funder/references/tactical-synthesis.md`
9. `tos-funder/references/output-schema-examples.md`
10. `tos-funder/references/skill-workflow.md`
11. `tos-funder/references/command-template.md`
12. `docs/tos-funder/validation-pr9b.md`
13. `docs/tos-funder/audit/pr9b-tactical-synthesizer-review-20260603-102419.md`

## Files To Create

1. `tos-funder/references/macro-topdown.md`
2. `tos-funder/commands/tos-funder-macro-topdown.md`
3. `docs/tos-funder/validation-pr10a.md`

## Files To Update

1. `tos-funder/SKILL.md`
2. `tos-funder/commands/tos-funder-analyze.md`
3. `tos-funder/references/agent-taxonomy.md`
4. `tos-funder/references/output-schema-examples.md`
5. `tos-funder/references/skill-workflow.md`
6. `docs/tos-funder/quick-guide.md`

Do not modify portfolio final-action logic in PR10A.

## Command

```text
/tos-funder-macro-topdown <股票代码或名称|指数代码|行业名称> [日期YYYY-MM-DD]
```

For a single stock, the command should:

1. identify the stock's industry/sector from existing basicinfo or upstream outputs
2. evaluate broad market regime
3. evaluate sector/industry relative context if data is available
4. produce a top-down context signal consumable by `/tos-funder-analyze` and tactical workflows

## Mandatory Data Coverage Probe

Before implementing the final command logic, create a validation section in `docs/tos-funder/validation-pr10a.md` called:

```text
## Data Coverage Probe
```

Probe and document whether each data source is available:

### A. Index Price Series

Test whether hoxit market can retrieve major A-share index bars:

```bash
.venv/bin/python -m hoxit.cli market bars 000001 --category 4 --offset 120 --adjust qfq
.venv/bin/python -m hoxit.cli market bars 399001 --category 4 --offset 120 --adjust qfq
.venv/bin/python -m hoxit.cli market bars 399006 --category 4 --offset 120 --adjust qfq
```

If these fail due to market/code handling, try documented alternatives only if already supported by hoxit. Do not add a new external data source in PR10A unless the command can document the fallback.

### B. Sector / Industry Context

Probe whether iWencai can return target industry and concept tags:

```bash
.venv/bin/python -m hoxit.cli iwc query -r basicinfo -q "<TARGET> 所属同花顺行业 概念 总市值 股票代码" --limit 5
```

Probe whether iWencai can return industry/sector strength in a stable form:

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 行业板块 涨跌幅 成交额 领涨行业 领跌行业" --limit 20
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 行业板块 涨跌幅 排名 A股" --limit 20
```

If these are unstable or empty, mark sector strength as `degraded` and use only target stock industry tags, not a fake relative-strength score.

### C. Market Breadth Proxy

Probe whether iWencai can return breadth-like fields:

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 A股 上涨家数 下跌家数 涨停家数 跌停家数" --limit 10
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 沪深京A股 上涨家数 下跌家数 成交额" --limit 10
```

If not available, do not compute breadth. Mark as missing.

### D. Style Rotation Proxy

Probe whether iWencai can return style/index proxy data:

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 大盘成长 大盘价值 小盘成长 小盘价值 涨跌幅" --limit 20
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 沪深300 中证500 中证1000 创业板指 涨跌幅" --limit 20
```

If unavailable, use index price-series returns only if index bars are verified.

### E. Risk Appetite Proxy

Probe:

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 A股 成交额 北向资金 融资余额 涨停家数 跌停家数" --limit 10
```

If northbound/funding data is unavailable, use only verified price/breadth/turnover proxies.

## Core Rules

1. No final_action.
2. No portfolio actions.
   - Do not output `buy/sell/hold/reduce/reject`.
3. No new primary signal enums.
   - Use `signal: bullish | neutral | bearish | blocked`.
   - Use `strength: strong | weak | flat`.
4. Add a separate regime field:
   - `market_regime: risk_on | neutral | risk_off | mixed | unknown`
5. Add a separate coverage field:
   - `coverage_status: verified | partial | degraded | blocked`
6. Do not claim causality.
   - Use “proxy suggests” language in reasoning.
7. Do not use external macro data by default.
   - No rates, CPI, PMI, FX, futures, options, or offshore data unless hoxit already supports and validation documents it.
8. Index/sector/breadth/style proxies are context, not final trading decisions.
9. If data is missing, output `signal=blocked` only when the missing field is essential. Otherwise output `neutral` with `coverage_status=partial/degraded`.
10. If only broad index data is available, do not pretend sector/breadth/style was validated.

## Output Schema

Add `macro_topdown_signal` to `output-schema-examples.md`.

Required fields:

- `target`
- `signal_type: "macro_topdown"`
- `coverage_status`
- `data_quality_summary`
- `data_sources`
- `market_context`
- `index_trend_context`
- `sector_context`
- `breadth_context`
- `style_rotation_context`
- `risk_appetite_context`
- `macro_scoring`
- `hard_gates`
- `market_regime`
- `signal`
- `strength`
- `confidence`
- `confidence_calculation`
- `risks`
- `opportunities`
- `next_steps`

Suggested shape:

```json
{
  "target": {
    "code": "002594",
    "name": "比亚迪",
    "industry": "汽车整车",
    "date": "2026-06-03"
  },
  "signal_type": "macro_topdown",
  "coverage_status": "partial",
  "market_regime": "neutral",
  "data_quality_summary": {
    "status": "partial",
    "missing_context": ["market_breadth", "style_rotation"],
    "degraded_context": ["sector_strength"],
    "warnings": []
  },
  "data_sources": {
    "index_bars": {"status": "verified", "source": "hoxit market bars"},
    "industry_basicinfo": {"status": "verified", "source": "iwc basicinfo"},
    "sector_strength": {"status": "degraded", "source": "iwc market query"},
    "breadth": {"status": "missing", "source": "iwc market query"},
    "style_rotation": {"status": "missing", "source": "iwc market query"}
  },
  "market_context": {},
  "index_trend_context": {},
  "sector_context": {},
  "breadth_context": {},
  "style_rotation_context": {},
  "risk_appetite_context": {},
  "macro_scoring": {
    "dimensions": {},
    "total_score": 0,
    "score_interpretation": ""
  },
  "hard_gates": {},
  "signal": "neutral",
  "strength": "flat",
  "confidence": 0,
  "confidence_calculation": {
    "base_confidence": 0,
    "caps_applied": [],
    "final_confidence": 0
  },
  "risks": [],
  "opportunities": [],
  "next_steps": []
}
```

## Scoring Model

Keep scoring simple and deterministic.

Only score dimensions with verified or acceptable data.

Recommended weights if all dimensions are available:

| Dimension | Weight |
|---|---|
| Index trend | 35% |
| Sector relative strength | 25% |
| Market breadth | 20% |
| Style/risk appetite | 20% |

If a dimension is missing, remove it from denominator and record this in `coverage_status`.

### Index Trend

Use verified index bars only.

Compute:

- 20d return
- 60d return
- MA20/MA60 relation
- volatility regime if available

Suggested score:

```text
+2 if major index close > MA20 and MA60
+1 if 20d return > 0
+1 if 60d return > 0
-2 if close < MA20 and MA60
-1 if 20d return < -3%
-1 if 60d return < -8%
```

Map to:

- positive index trend
- neutral index trend
- negative index trend

### Sector Relative Strength

Use only if sector/industry performance can be verified.

Do not infer sector strength from the target stock alone.

If only industry tag is available:

```text
sector_context.status = "tag_only"
sector score = neutral
```

### Market Breadth

Use verified rising/falling counts or limit-up/limit-down counts.

If unavailable:

```text
breadth_context.status = "missing"
do not score breadth
```

### Style / Risk Appetite

Use verified style index returns or large-cap/small-cap/growth/value proxy.

If unavailable:

```text
style_rotation_context.status = "missing"
do not score style
```

## Hard Gates

### Gate 1: Coverage Gate

If fewer than two dimensions are verified:

```text
coverage_status = degraded
signal = neutral or blocked
confidence <= 50
```

If no index trend data:

```text
signal = blocked
market_regime = unknown
```

### Gate 2: Risk-Off Gate

If verified index trend is negative and breadth is negative:

```text
market_regime = risk_off
signal cannot be bullish
```

### Gate 3: Sector Missing Gate

For single-stock target, if industry tag is missing:

```text
sector_context.status = missing
confidence cap 60
```

### Gate 4: Overclaim Gate

If sector, breadth, and style are missing:

```text
Do not output "market supports the stock"
Only output broad index context.
```

## Signal Mapping

```text
positive total score + at least 3 verified dimensions:
  signal = bullish, market_regime = risk_on or neutral, strength = weak/strong

negative total score + at least 2 verified dimensions:
  signal = bearish, market_regime = risk_off or mixed, strength = weak/strong

mixed or partial:
  signal = neutral, market_regime = mixed/neutral/unknown

insufficient index data:
  signal = blocked, market_regime = unknown
```

## Confidence Calculation

```text
base_confidence = 40
+15 if index bars verified
+10 if sector strength verified
+10 if breadth verified
+10 if style/risk-appetite verified
+5  if target industry tag verified

caps:
  fewer than 2 verified dimensions → cap 50
  no sector context for stock target → cap 60
  stale market data → cap 50

final_confidence = clamp(20, 90, confidence)
```

## Validation Samples

Create `docs/tos-funder/validation-pr10a.md`.

Validation must include:

1. `002594 比亚迪`
   - single-stock target
   - industry tag expected
   - verify whether auto/EV sector context is available
   - output should not overclaim if sector strength is unavailable

2. `600519 贵州茅台`
   - consumer/白酒 context
   - verify whether sector strength data is available
   - check if broad index context affects signal but does not override stock fundamentals

3. `002142 宁波银行`
   - bank sector
   - verify financial-sector context if available
   - if sector strength unavailable, keep top-down signal neutral/partial

4. One index target
   - e.g. `000001` 上证指数 or verified alternative
   - validates index-only mode
   - sector_context may be N/A

5. One negative/partial coverage scenario
   - simulate or document a case where index bars are unavailable or breadth/style missing
   - expected: `coverage_status=degraded/blocked`, no overclaim

Each sample must label `source_status`:

- `live_verified`
- `accepted_existing`
- `degraded`
- `missing`
- `assumed_fixture`

Assumed fixtures cannot be used as proof of new data coverage.

## Acceptance Checks

Run and record:

```bash
rg -n "final_action|\"action\"|\"stance\": \"buy\"|\"stance\": \"sell\"|\"signal\": \"buy\"|\"signal\": \"sell\"" tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10a.md

rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/output-schema-examples.md

rg -n "PMI|CPI|利率|汇率|期货|期权|美债|美元|FOMC|macro forecast|预测宏观" tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md docs/tos-funder/validation-pr10a.md

rg -n "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-macro-topdown.md

rg -n "sector.*verified|breadth.*verified|style.*verified|coverage_status|market_regime" tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10a.md
```

Important:

- Matches for `PMI/CPI/利率` are acceptable only if they appear in "out of scope / do not use" sections.
- Matches for `action` are acceptable only in constraint text, not as output fields.
- Record exact results and explain acceptable matches.

## Delivery Summary Required

After implementation, reply with:

1. Modified file list
2. Data Coverage Probe results
3. `macro_topdown_signal` schema summary
4. Validation sample outcomes
5. Missing/degraded data sources
6. Exact `rg` self-check results

## Architect Notes

PR10A must be conservative.

This PR exists to answer:

```text
What is the broad A-share top-down context around this target?
```

It does not answer:

```text
What will macro policy do?
What is the full Druckenmiller trade?
Should the portfolio buy or sell?
```

Do not let proxy language drift into macro prediction.
