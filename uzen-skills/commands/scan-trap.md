# scan-trap

Run trap and manipulation-risk checks.

## Execution Path

```bash
hoxit uzen scan-trap <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls 8 providers:
- quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger

## Mode Profile

- depth: `focused`
- primary_section: `trap_risk`

## Current Behavior

First-version market risk detection using hoxit quantitative signals.

### Data Inputs

- Block trades from `hoxit.signals.block_trade`
- Margin trading from `hoxit.signals.margin_trading`
- Holder changes from `hoxit.signals.holder_num_change`
- Fund flow from `hoxit.signals.baidu_fund_flow_history`
- Concept heat from `hoxit.signals.baidu_concept_blocks`
- Dragon-tiger from `hoxit.signals.dragon_tiger_board`
- Lockup expiry from `hoxit.signals.lockup_expiry`

### Risk Scoring Rules

- Base: no flags → `low`
- 1-2 flags → `medium`
- 3+ flags → `high`

### Output

- `<code>-scan-trap.json` — Structured risk data
- `<code>-scan-trap.md` — Markdown summary

### JSON Schema (Current)

```json
{
  "level": "low",
  "flags": ["..."]
}
```

- `level`: `"low"`, `"medium"`, or `"high"`
- `flags`: List of risk flag strings

## Limitations

This detects **market risk signals only**, not social/manipulation traps.

### What This Does

- Identifies observable quantitative risk indicators
- Reports data availability and gaps
- Computes risk level from available signals

### What This Does Not Do

- Detect social sentiment or coordinated promotion
- Identify manipulation patterns or fake news
- Analyze forum activity or influencer behavior
- Provide evidence URLs for trap allegations

See `uzen-skills/skills/trap-detector/SKILL.md` for:
- Full risk category distinction
- Deferred UZI-style trap evidence
- Evidence URL and keyword requirements
- No-fabrication rules for social claims
