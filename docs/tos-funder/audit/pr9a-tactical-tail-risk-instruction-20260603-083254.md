# PR9A Instruction — Tactical Tail-Risk Proxy

Created: 2026-06-03 08:32:54 Asia/Shanghai
Owner: CC implementation
Reviewer: Codex architecture/review
Status: Ready for CC

## Objective

Implement `/tos-funder-tactical-tail-risk` in `tos-funder`.

PR8A `/tos-funder-tactical-catalyst` covers opportunity/catalyst classification. PR9A covers downside risk and tail-risk classification. This command must identify risk evidence, risk strength, hard gates, and follow-up checks. It must not produce `final_action`.

## Must Read First

Before editing, read:

1. `tos-funder/commands/tos-funder-tactical-catalyst.md`
2. `tos-funder/references/tactical-catalyst.md`
3. `tos-funder/commands/tos-funder-risk-manager.md`
4. `tos-funder/commands/tos-funder-quant-price-series.md`
5. `tos-funder/references/price-series.md`
6. `tos-funder/references/output-schema-examples.md`
7. `tos-funder/references/skill-workflow.md`
8. `docs/tos-funder/validation-pr8a.md`
9. `docs/tos-funder/audit/pr8a-tactical-catalyst-review-20260603-002834.md`

## Files To Create

1. `tos-funder/references/tactical-tail-risk.md`
2. `tos-funder/commands/tos-funder-tactical-tail-risk.md`
3. `docs/tos-funder/validation-pr9a.md`

## Files To Update

1. `tos-funder/SKILL.md`
2. `tos-funder/commands/tos-funder-analyze.md`
3. `tos-funder/references/agent-taxonomy.md`
4. `tos-funder/references/output-schema-examples.md`
5. `tos-funder/references/skill-workflow.md`

## Core Rules

1. Tail-risk is a risk proxy, not investment advice.
2. Do not output `final_action`.
3. Use only validated or explainable sources:
   - mootdx/TDX price series
   - `/tos-funder-risk-manager`
   - `/tos-funder-quant-technicals`
   - `/tos-funder-tactical-catalyst`
   - iWencai announcement/report search
4. Do not use confirmed dead routes:
   - `query2data event`
   - `business`
   - `management`
5. Data-quality anomalies are not real negative risk events.
   - `adjustment_status=suspect/unknown` goes into `data_quality_summary`.
   - degraded `max_dd/downside_vol` must not be used as true tail-risk evidence.
6. `confidence` must remain integer `0-100`.
   - Put derivation into `confidence_calculation`.
7. Do not introduce new signal/action enums.
   - `signal`: `bullish | neutral | bearish | blocked`
   - no `weak_bullish`, `strong_bearish`, `weak_sell`, `strong_buy`

## Command

```text
/tos-funder-tactical-tail-risk <股票代码或名称> [日期YYYY-MM-DD]
```

## Output Schema

Add `tail_risk_signal` to `output-schema-examples.md`.

Required fields:

- `target`
- `signal_type: "tail_risk"`
- `data_quality_summary`
- `consumed_signals`
- `risk_facts`
- `event_risk_context`
- `price_risk_context`
- `liquidity_context`
- `technical_breakdown_context`
- `tail_risk_scoring`
- `hard_gates`
- `signal`
- `strength`
- `confidence`
- `confidence_calculation`
- `risks`
- `opportunities`
- `next_steps`

## Risk Taxonomy

### Event Risk

Include:

- 监管函、问询函、处罚、立案
- 诉讼、仲裁
- 大股东减持
- 质押风险
- 财报暴雷、业绩预告大幅下修

### Price Risk

Include:

- 放量下跌
- 跌破关键均线
- 20d/60d 大幅回撤
- 波动率异常抬升
- 价格趋势与基本面/催化剂背离

### Liquidity Risk

Include:

- 成交额不足
- 流动性快速萎缩
- 小市值或低换手导致无法有效退出

### Data Quality Risk

Include:

- `adjustment_status=suspect/unknown`
- corporate-action adjustment anomaly
- degraded/blocked metrics

Important: data quality risk can cap confidence or block metric usage, but cannot be treated as a real market risk event.

## Hard Gates

### Gate 1: Data Quality

If `adjustment_status=suspect/unknown`:

- mark risk metrics as degraded
- do not use degraded metrics as true tail-risk evidence
- cap confidence if needed, but explain the cap

### Gate 2: Major Event

If announcement/report search finds regulatory action, litigation, penalty, investigation, major reduction, or pledge crisis:

- signal cannot be `bullish`
- if event is severe and recent, signal should be `bearish`

### Gate 3: Technical Breakdown

If price breaks below MA20/MA60 with volume expansion, or 20d return is materially negative:

- signal should be at most `neutral`
- may be `bearish` if confirmed by risk-manager and liquidity context

### Gate 4: Liquidity

If liquidity tier is low or turnover/amount is insufficient:

- cap confidence
- surface exit-risk warning

### Gate 5: Stale Evidence

If all risk evidence is older than 180 days and no fresh evidence exists:

- do not overstate risk
- cap confidence

## Validation Samples

Create `docs/tos-funder/validation-pr9a.md`.

Use at least 3 main samples plus 1 true negative-risk sample:

1. `002594 比亚迪`
   - Validate that adjustment anomaly is only data-quality risk.
   - It must not become real negative tail risk.

2. `600519 贵州茅台`
   - Validate growth slowdown/report positivity.
   - Tail risk should not be exaggerated without true event risk.

3. `002142 宁波银行`
   - Validate bank-specific risks:
     - NIM
     - asset quality
     - capital adequacy
     - systemic/banking-cycle risk

4. One real negative-risk sample
   - Use iWencai announcement search to find a stock with regulatory letter, litigation, penalty, major reduction, or pledge crisis.
   - If no suitable sample can be verified, write `规则定义，未实测`; do not pretend validation passed.

## Acceptance Checks

Run and record:

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-tactical-tail-risk.md tos-funder/references/output-schema-examples.md
rg -n "final_action" tos-funder/commands/tos-funder-tactical-tail-risk.md
rg -n "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-tactical-tail-risk.md
rg -n "polarity.*negative.*adjustment_anomaly|max_dd.*negative catalyst|downside_vol.*negative catalyst" tos-funder/commands/tos-funder-tactical-tail-risk.md tos-funder/references/output-schema-examples.md
```

Expected:

- no new signal/action enum
- no `final_action`
- no dead routes
- no degraded metric abuse

## CC Delivery Summary Format

After completion, reply with:

1. Modified file list
2. `tail_risk_signal` schema summary
3. Four validation sample conclusions
4. Data gaps found
5. Exact `rg` self-check results

## Architect Notes

This PR is not about smarter trading judgment. It exists to close the risk-side gap left by PR8A.

The key principle: data-quality anomaly is not a risk event; a risk proxy is not a buy/sell decision.
