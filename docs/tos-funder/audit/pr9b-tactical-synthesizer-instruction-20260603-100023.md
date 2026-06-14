# PR9B Instruction — Tactical Synthesizer

Created: 2026-06-03 10:00:23 Asia/Shanghai
Owner: CC implementation
Reviewer: Codex architecture/review
Status: Ready for CC

## Objective

Implement a tactical-layer synthesizer for `tos-funder`.

PR8A created `/tos-funder-tactical-catalyst`, which identifies tactical opportunity/catalyst evidence.

PR9A created `/tos-funder-tactical-tail-risk`, which identifies downside/tail-risk evidence.

PR9B must combine these two accepted tactical proxy outputs into one tactical synthesis command. It should resolve opportunity-vs-risk conflicts, produce a tactical stance, identify current risks and opportunities, and provide next-step prompts.

It must **not** produce final portfolio action. Final action remains the responsibility of `/tos-funder-analyze` and `/tos-funder-portfolio`.

## Must Read First

Read these files before editing:

1. `tos-funder/commands/tos-funder-tactical-catalyst.md`
2. `tos-funder/references/tactical-catalyst.md`
3. `docs/tos-funder/validation-pr8a.md`
4. `docs/tos-funder/audit/pr8a-tactical-catalyst-review-20260603-002834.md`
5. `tos-funder/commands/tos-funder-tactical-tail-risk.md`
6. `tos-funder/references/tactical-tail-risk.md`
7. `docs/tos-funder/validation-pr9a.md`
8. `docs/tos-funder/audit/pr9a-tactical-tail-risk-review-20260603-084817.md`
9. `tos-funder/references/output-schema-examples.md`
10. `tos-funder/references/skill-workflow.md`
11. `tos-funder/references/command-template.md`
12. `tos-funder/commands/tos-funder-analyze.md`

## Files To Create

1. `tos-funder/references/tactical-synthesis.md`
2. `tos-funder/commands/tos-funder-tactical.md`
3. `docs/tos-funder/validation-pr9b.md`

## Files To Update

1. `tos-funder/SKILL.md`
2. `tos-funder/commands/tos-funder-analyze.md`
3. `tos-funder/references/agent-taxonomy.md`
4. `tos-funder/references/output-schema-examples.md`
5. `tos-funder/references/skill-workflow.md`
6. `docs/tos-funder/quick-guide.md`

## Command

```text
/tos-funder-tactical <股票代码或名称> [日期YYYY-MM-DD]
```

## Scope

This command consumes:

- `/tos-funder-tactical-catalyst` output: `tactical_catalyst_signal`
- `/tos-funder-tactical-tail-risk` output: `tail_risk_signal`

It may also read already-produced contextual outputs when available:

- `/tos-funder-quant-price-series`
- `/tos-funder-quant-technicals`
- `/tos-funder-risk-manager`
- `/tos-funder-quant-sentiment`

But PR9B should not duplicate data collection if accepted catalyst/tail-risk outputs are already present. Prefer consuming structured outputs.

## Core Rules

1. No `final_action`.
2. No new primary signal enums.
   - Use `signal: bullish | neutral | bearish | blocked`.
   - Use `strength: strong | weak | flat`.
   - Do not create `weak_bullish`, `strong_bearish`, `buy`, `sell`, etc.
3. `confidence` must be `int 0-100`.
   - Put derivation into `confidence_calculation`.
4. Data quality must remain separate from real market signal.
   - If catalyst or tail-risk says data is degraded, carry it into `data_quality_summary`.
   - Do not turn data-quality anomaly into bearish tactical stance.
5. Tail-risk has veto priority over catalyst opportunity.
   - A critical tail-risk event must cap or override positive catalyst stance.
   - A low tail-risk state does not make tactical stance bullish by itself.
6. Catalyst report polarization must not become positive evidence.
   - If catalyst signal is capped by report-polarization gate, tactical synthesis must carry that cap.
7. The command is a tactical synthesis layer, not a macro strategy.
   - Do not implement Druckenmiller or macro prediction here.
   - Do not add index/sector macro data unless already available and explicitly marked as contextual.

## Output Schema

Add `tactical_synthesis_signal` to `output-schema-examples.md`.

Required fields:

- `target`
- `signal_type: "tactical_synthesis"`
- `data_quality_summary`
- `consumed_signals`
- `opportunity_context`
- `risk_context`
- `conflict_resolution`
- `hard_gates`
- `tactical_stance`
- `signal`
- `strength`
- `confidence`
- `confidence_calculation`
- `risks`
- `opportunities`
- `next_steps`

Suggested field details:

```json
{
  "signal_type": "tactical_synthesis",
  "consumed_signals": {
    "catalyst": {
      "signal_type": "tactical_catalyst",
      "signal": "neutral",
      "strength": "flat",
      "confidence": 55,
      "hard_gates": {}
    },
    "tail_risk": {
      "signal_type": "tail_risk",
      "signal": "neutral",
      "tail_risk_level": "low",
      "confidence": 60,
      "hard_gates": {}
    }
  },
  "opportunity_context": {
    "material_catalysts": [],
    "price_confirmation": {},
    "opportunity_score": 0.0,
    "opportunity_quality": "low | moderate | high | unknown"
  },
  "risk_context": {
    "tail_risk_level": "low | moderate | high | critical | unknown",
    "major_events": [],
    "data_quality_modifier": {},
    "risk_score": 0.0,
    "risk_pressure": "low | moderate | high | critical | unknown"
  },
  "conflict_resolution": {
    "state": "aligned | opportunity_without_confirmation | risk_overrides_opportunity | blocked_by_data_quality | mixed",
    "rules_applied": [],
    "winning_side": "opportunity | risk | neutral | blocked"
  },
  "hard_gates": {
    "critical_tail_risk": {},
    "data_quality": {},
    "report_polarization": {},
    "price_confirmation": {}
  },
  "tactical_stance": {
    "stance": "favorable | watch | cautious | avoid | blocked",
    "time_horizon": "near_term | swing | medium_term",
    "explanation": ""
  },
  "signal": "bullish | neutral | bearish | blocked",
  "strength": "strong | weak | flat",
  "confidence": 0,
  "confidence_calculation": {
    "base_confidence": 0,
    "caps_applied": [],
    "final_confidence": 0
  }
}
```

Note:

- `tactical_stance.stance` is not a trade action.
- Do not output `buy`, `sell`, `hold`, `reduce`, `reject`, or `final_action`.

## Synthesis Rules

### Rule 1: Critical Risk Overrides Opportunity

If `tail_risk.tail_risk_level = critical` OR `tail_risk.hard_gates.major_event.status = triggered` with critical severity:

```text
signal = bearish
strength = strong
tactical_stance.stance = avoid
conflict_resolution.state = risk_overrides_opportunity
```

Confidence should follow tail-risk confidence, capped by data quality if needed.

### Rule 2: High Risk Caps Catalyst

If `tail_risk_level = high`:

```text
signal cannot be bullish
tactical_stance.stance = cautious or avoid
```

If catalyst is bullish, record:

```text
conflict_resolution.state = risk_overrides_opportunity
```

### Rule 3: Catalyst Needs Material Evidence

If catalyst signal is positive only because of reports and `hard_gates.report_polarization.status = triggered`:

```text
signal cannot be bullish
tactical_stance.stance = watch
```

Use PR8A's Gate 2 logic:

- routine earnings/dividends do not count as material tactical catalysts
- material catalysts include buyback, share increase, equity incentive, large order, restructuring, major capital raise, dividend bonus with size, litigation/regulatory/reduction events

### Rule 4: Low Tail Risk Does Not Create Bullish Signal

If tail-risk is low but catalyst is neutral:

```text
signal = neutral
tactical_stance.stance = watch
```

Low risk is a condition, not an opportunity.

### Rule 5: Favorable Tactical Setup

Signal can be bullish only if all are true:

- catalyst has material positive evidence
- catalyst price confirmation is not blocked
- tail-risk level is low or moderate
- no critical/high event risk
- data quality does not block the relevant price/risk evidence

Then:

```text
signal = bullish
strength = weak or strong depending on catalyst strength + price confirmation
tactical_stance.stance = favorable
```

### Rule 6: Data Quality Blocks Overclaiming

If either input has `adjustment_status=suspect/unknown` or key risk metrics blocked:

- keep the warning in `data_quality_summary`
- cap confidence according to the stricter upstream cap
- do not produce strong bullish or strong bearish based only on degraded price/risk metrics
- real event risk can still drive bearish

### Rule 7: Missing Input Handling

If catalyst output is missing:

```text
signal = blocked
tactical_stance.stance = blocked
missing_data includes catalyst
```

If tail-risk output is missing:

```text
signal = blocked
tactical_stance.stance = blocked
missing_data includes tail_risk
```

Do not synthesize from only one side unless explicitly marked as partial and `signal=blocked`.

## Confidence Calculation

Suggested deterministic formula:

```text
base_confidence = round((catalyst.confidence + tail_risk.confidence) / 2)

adjustments:
  +5 if catalyst and tail-risk are aligned
  -10 if opportunity/risk conflict
  -10 if report_polarization gate triggered
  -10 if price_confirmation gate triggered

caps:
  critical risk with data unknown → min(confidence, tail_risk.confidence)
  data quality suspect/unknown    → min(confidence, strictest upstream cap)
  missing input                   → confidence <= 30 and signal=blocked

final_confidence = clamp(20, 95, confidence)
```

Keep `confidence` as int and mirror it in `confidence_calculation.final_confidence`.

## Validation Samples

Create `docs/tos-funder/validation-pr9b.md`.

Use at least these four samples:

1. `002594 比亚迪`
   - PR8A: catalyst neutral, data-quality adjustment anomaly, factual positive catalysts.
   - PR9A: tail-risk neutral + low, data-quality cap.
   - Expected: `signal=neutral`, stance `watch`, confidence capped by data quality.
   - Must not treat adjustment anomaly as bearish risk.

2. `600519 贵州茅台`
   - PR8A: catalyst neutral due to report polarization.
   - PR9A: tail-risk neutral + low.
   - Expected: `signal=neutral`, stance `watch`.
   - Must not convert low risk + positive reports into bullish.

3. `002142 宁波银行`
   - PR8A: catalyst neutral due to report polarization.
   - PR9A: tail-risk neutral + low/moderate.
   - Expected: `signal=neutral`, stance `watch`.
   - Must respect report-polarization cap.

4. `000820 *ST节能`
   - PR9A: tail-risk critical, Gate 2 major event triggered.
   - PR8A catalyst may be missing or negative/blocked.
   - Expected: `signal=bearish`, stance `avoid`, conflict state `risk_overrides_opportunity` or `blocked_by_missing_catalyst` depending available catalyst input.
   - Must not soften critical event risk merely because price/liquidity data are unavailable.

If any upstream sample output is assumed rather than rerun, label `source_status` clearly:

- `accepted_pr8a`
- `accepted_pr9a`
- `assumed_fixture`
- `live_verified`

Assumed fixtures must not be used as proof for new behavior unless they directly inherit accepted validation.

## Acceptance Checks

Run and record:

```bash
rg -n "final_action|buy|sell|hold|reduce|reject" tos-funder/commands/tos-funder-tactical.md tos-funder/references/tactical-synthesis.md tos-funder/references/output-schema-examples.md
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-tactical.md tos-funder/references/output-schema-examples.md
rg -n "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-tactical.md
rg -n "tail_risk_level.*low.*signal.*bullish|low tail risk.*bullish|report_polarization.*bullish" tos-funder/commands/tos-funder-tactical.md tos-funder/references/tactical-synthesis.md docs/tos-funder/validation-pr9b.md
rg -n '"confidence": [0-9]+.*"confidence_calculation"' tos-funder/references/output-schema-examples.md
```

Important:

- The first `rg` may match explanatory text saying "do not output buy/sell". That is acceptable only if there is no output schema field or example using those as tactical results.
- Record exact results and explain acceptable matches.

## Delivery Summary Required

After implementation, reply with:

1. Modified file list
2. `tactical_synthesis_signal` schema summary
3. Four validation sample outcomes
4. Conflict-resolution rules summary
5. Data gaps or assumptions
6. Exact `rg` self-check results

## Architect Notes

PR9B is a synthesis PR, not a new data-source PR.

The biggest risk is semantic drift:

- low risk is not bullish
- report positivity is not a catalyst by itself
- data-quality anomaly is not bearish
- tactical stance is not portfolio action

Keep those four boundaries explicit.
