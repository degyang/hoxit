# PR10B Instruction: Portfolio / Decision Synthesizer

Created: 2026-06-03 11:40:06 Asia/Shanghai

## Context

PR10A Macro / Top-Down Proxy has been accepted.

The next step is PR10B: upgrade the existing `/tos-funder-portfolio` command and `portfolio-synthesis.md` reference so they consume the full set of current `tos-funder` signal schemas:

- value: Buffett / Graham
- growth: Fisher / Lynch / aggregate growth
- quant: fundamentals / technicals / sentiment / risk-manager
- tactical: catalyst / tail-risk / tactical synthesis
- macro: macro/top-down
- portfolio: final A-share action and position sizing

This PR should not create a new command. It should modernize the already existing:

- `tos-funder/commands/tos-funder-portfolio.md`
- `tos-funder/references/portfolio-synthesis.md`

## Objective

Make `/tos-funder-portfolio` the only command that produces final portfolio actions.

All upstream commands may produce analyst, tactical, macro, risk, or synthesis signals, but they must not produce portfolio actions. PR10B should enforce that boundary and make the final decision layer explicit.

## Non-Negotiable Architecture Boundary

### Upstream Commands

These commands provide evidence and signal context:

- `/tos-funder-value-buffett`
- `/tos-funder-value-graham`
- `/tos-funder-growth`
- `/tos-funder-quant-fundamentals`
- `/tos-funder-quant-technicals`
- `/tos-funder-quant-sentiment`
- `/tos-funder-risk-manager`
- `/tos-funder-tactical`
- `/tos-funder-macro-topdown`

They may output:

- `signal`
- `strength`
- `confidence`
- `confidence_calculation`
- `risk_level`
- `tail_risk_level`
- `market_regime`
- `coverage_status`
- `manual_review_required`
- `hard_gates`
- `data_quality`
- `missing_context`
- `degraded_context`

They must not be treated as producing final portfolio actions.

### Portfolio Command

Only `/tos-funder-portfolio` may produce:

- `allowed_actions`
- `final_actions`
- `position_sizing`
- `cash_allocation`
- `portfolio_level_constraints`
- final A-share action: `buy | hold | sell | reduce | watch | reject | blocked`

Do not introduce `strong_buy`, `weak_sell`, `trim`, `avoid`, `manual_review`, `short`, or `cover` as action enums.

## Required Files To Update

Update these files:

1. `tos-funder/commands/tos-funder-portfolio.md`
2. `tos-funder/references/portfolio-synthesis.md`
3. `tos-funder/references/output-schema-examples.md`
4. `tos-funder/references/skill-workflow.md`
5. `tos-funder/references/agent-taxonomy.md`
6. `tos-funder/commands/tos-funder-analyze.md`
7. `tos-funder/SKILL.md`
8. `docs/tos-funder/quick-guide.md`

Create:

9. `docs/tos-funder/validation-pr10b.md`

Do not create a new command unless the existing command cannot be repaired. The expected path remains:

- `tos-funder/commands/tos-funder-portfolio.md`

## Main Design Requirements

### 1. Replace Legacy Input Model

The current portfolio command mainly consumes:

- quant fundamentals
- technicals
- Buffett / Graham
- risk manager

PR10B must update this to consume the current schema set:

| Layer | Command | Schema |
|---|---|---|
| Value | `/tos-funder-value-buffett` | value analyst signal |
| Value | `/tos-funder-value-graham` | value analyst signal |
| Growth | `/tos-funder-growth` | `growth_aggregate_signal` |
| Quant | `/tos-funder-quant-fundamentals` | fundamentals signal |
| Quant | `/tos-funder-quant-technicals` | technical signal |
| Sentiment | `/tos-funder-quant-sentiment` | sentiment/event proxy |
| Risk | `/tos-funder-risk-manager` | risk metrics and position limits |
| Tactical | `/tos-funder-tactical` | `tactical_synthesis_signal` |
| Macro | `/tos-funder-macro-topdown` | `macro_topdown_signal` |

Do not require every layer for every run. Portfolio must support degraded-but-usable operation.

### 2. Define Required vs Optional Inputs

Use this minimum rule:

- Required for final portfolio action:
  - at least one directional analyst layer: value OR growth OR quant fundamentals
  - `/tos-funder-risk-manager`

- Optional but recommended:
  - technicals
  - sentiment
  - tactical
  - macro

- If risk-manager is missing:
  - output may still summarize signals
  - `final_actions[].action` must be `blocked`
  - reason: missing risk-manager prevents position sizing and hard risk vetoes

- If no directional analyst layer is available:
  - `final_actions[].action` must be `blocked`
  - reason: no investable thesis layer

### 3. Introduce A Deterministic Layer Model

Update `portfolio-synthesis.md` around a five-layer decision model:

1. Thesis layer: value + growth + quant fundamentals
2. Timing layer: technicals + sentiment
3. Tactical context layer: tactical synthesis
4. Macro context layer: macro/top-down
5. Risk and portfolio constraints layer: risk-manager + cash/position state

Decision direction comes from the thesis layer.

Timing can delay or cap entries.

Tactical can boost, cap, or block based on catalyst/tail-risk conflict.

Macro can cap sizing and confidence, but should not independently create a buy/sell decision.

Risk-manager controls position sizing and applies vetoes.

### 4. Signal Mapping

Use only canonical directional signals:

```text
bullish
neutral
bearish
blocked
```

Map upstream signals to scores:

| Signal | Score |
|---|---|
| bullish | +1.0 |
| neutral | 0.0 |
| bearish | -1.0 |
| blocked | excluded, but counted in missing/degraded coverage |

For strength:

| Strength | Multiplier |
|---|---|
| strong | 1.0 |
| medium | 0.75 |
| weak | 0.5 |
| flat | 0.0 |

If a command does not provide strength, use 1.0 for bullish/bearish and 0.0 for neutral.

Do not introduce `weak_bullish` or `strong_bearish` as signal enums.

### 5. Layer Weights

Use initial deterministic weights:

| Layer | Weight | Notes |
|---|---:|---|
| Buffett | 1.2 | quality/value thesis |
| Graham | 1.0 | margin-of-safety thesis |
| Growth aggregate | 1.1 | consolidated growth thesis |
| Quant fundamentals | 1.0 | objective baseline |
| Technicals | 0.6 | timing, not primary thesis |
| Sentiment | 0.4 | event/report context |
| Tactical synthesis | 0.6 | opportunity vs tail-risk context |
| Macro top-down | 0.5 | context/cap only |

Portfolio command should compute:

- `thesis_score`
- `timing_score`
- `context_score`
- `net_score`
- `consensus`
- `coverage_status`

### 6. Conflict Resolution

Use deterministic conflict rules:

1. **Risk hard veto wins**:
   - genuine risk veto may force `reject`, `sell`, or `reduce`
   - data-quality veto caps action but must not be treated as financial deterioration

2. **Critical tail risk caps all bullish action**:
   - if `tail_risk_level=critical` or tactical synthesis uses `risk_only_critical_override`
   - new position: max action `reject` or `watch`
   - existing position: max action `reduce`; `sell` only if thesis layer is also bearish

3. **Bearish thesis wins over bullish timing**:
   - bearish thesis + bullish technicals/sentiment = `reject` for new position, `reduce/sell` for existing depending risk

4. **Bullish thesis + bearish timing delays entry**:
   - new position: `watch`
   - existing position: `hold` unless risk/tail-risk says reduce

5. **Macro cannot create a buy**:
   - bullish macro may increase confidence/sizing only when thesis is bullish
   - bearish macro caps new buy to `watch` unless thesis is very strong and risk is low

6. **Data-quality gates cap confidence and action**:
   - upstream `manual_review_required=true` should flow into `manual_review_queue`
   - if key source is degraded, cap confidence according to reference rules

### 7. Confidence Rules

Keep top-level `confidence` as integer `0-100`.

Also include:

```json
"confidence_calculation": {
  "base_confidence": 68,
  "adjustments": [],
  "caps_applied": [],
  "final_confidence": 62
}
```

`confidence_calculation.final_confidence` must equal top-level `confidence`.

Suggested rules:

- Base confidence from weighted average of consumed source confidences.
- Consensus strong: +8.
- Consensus divergent: -12.
- Missing optional layer: no penalty by itself.
- Missing required layer: `blocked`, confidence <= 30.
- Data quality cap: <= 60.
- Risk-manager degraded: <= 55.
- Macro coverage degraded: <= 70.
- Tactical missing: no cap, but note in `missing_context`.
- Critical tail-risk: confidence should describe confidence in the final risk-capped action, not confidence in bullishness.

### 8. Output Schema

Update `output-schema-examples.md#portfolio_output` so the canonical schema includes:

```json
{
  "signal_type": "portfolio_decision",
  "portfolio_summary": {},
  "consumed_signals": {
    "value": {},
    "growth": {},
    "quant": {},
    "sentiment": {},
    "risk": {},
    "tactical": {},
    "macro": {}
  },
  "layer_scores": {
    "thesis_score": 0.42,
    "timing_score": -0.20,
    "context_score": 0.10,
    "net_score": 0.26
  },
  "conflict_resolution": [],
  "risk_constraints": {},
  "data_quality_vetoes": [],
  "risk_vetoes": [],
  "manual_review_queue": [],
  "allowed_actions": {},
  "final_actions": [
    {
      "code": "002142",
      "name": "宁波银行",
      "action": "hold",
      "confidence": 62,
      "confidence_calculation": {
        "base_confidence": 68,
        "adjustments": [],
        "caps_applied": [],
        "final_confidence": 62
      },
      "position_sizing": {},
      "reasoning": "",
      "missing_data": [],
      "manual_review_required": false
    }
  ],
  "next_steps": []
}
```

Do not make `confidence` an object.

### 9. Validation Requirements

Create `docs/tos-funder/validation-pr10b.md` with at least 4 samples:

1. **宁波银行 held position**
   - value/growth/quant mixed but not broken
   - risk acceptable
   - expected: `hold` or cautious `buy` only if sizing allows
   - macro/tactical should affect confidence/sizing, not create action alone

2. **贵州茅台 watchlist**
   - Buffett quality positive, Graham neutral/expensive, growth slowing
   - expected: likely `watch` unless thesis aggregate is strongly bullish
   - macro cannot force buy

3. **比亚迪 watchlist or held position**
   - growth/tactical conflicts plus known data-quality issues
   - expected: no sell/reject based only on degraded price metrics
   - if new position: likely `watch`
   - if held: `hold` or `reduce` only with independent confirmation

4. **Negative/tail-risk sample**
   - can reuse `000820 *ST节能` from PR9A if available
   - expected: `reject` for new position, or `reduce/sell` for existing only when thesis/risk both confirm

Each sample must include:

- `source_status`
- `consumed_signal_status`
- `required_inputs_present`
- `layer_scores`
- `conflict_resolution`
- `confidence_calculation`
- expected action and reason

Separate:

- accepted prior validation
- assumed fixture
- live query result

Do not mix assumed data with live validation without labeling it.

## Required `rg` Checks

Run and include results in the validation document:

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|avoid|manual_review\"" tos-funder docs/tos-funder
rg -n "\"confidence\"\\s*:\\s*\\{" tos-funder/commands/tos-funder-portfolio.md tos-funder/references/portfolio-synthesis.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10b.md
rg -n "final_action" tos-funder/commands/tos-funder-value-buffett.md tos-funder/commands/tos-funder-value-graham.md tos-funder/commands/tos-funder-growth.md tos-funder/commands/tos-funder-tactical.md tos-funder/commands/tos-funder-macro-topdown.md
rg -n "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-portfolio.md tos-funder/references/portfolio-synthesis.md
rg -n "macro.*force.*buy|macro.*create.*buy|tail_risk.*sell.*degraded|max_dd.*sell.*degraded" tos-funder/commands/tos-funder-portfolio.md tos-funder/references/portfolio-synthesis.md
```

Expected:

- No new enum drift.
- No object-valued top-level confidence.
- Upstream commands should not produce final portfolio action.
- Portfolio should not use dead iWencai routes.
- Macro must not independently force buy.
- Degraded tail-risk/max-dd must not independently force sell/reject.

## Acceptance Criteria

PR10B is acceptable only if:

1. `/tos-funder-portfolio` consumes all current major signal families.
2. The portfolio layer is clearly the only final action layer.
3. `portfolio-synthesis.md` documents deterministic layer scoring, conflict resolution, and confidence caps.
4. `output-schema-examples.md#portfolio_output` reflects the updated schema.
5. `tos-funder-analyze.md`, `SKILL.md`, `skill-workflow.md`, and `agent-taxonomy.md` route portfolio correctly.
6. Validation samples are internally consistent with the command rules.
7. `confidence` remains int 0-100 everywhere.
8. Data-quality veto and risk veto remain separate.
9. Macro/top-down and tactical context influence caps, confidence, and sizing, but do not bypass thesis/risk logic.
10. No dead iWencai routes are introduced.

## CC Delivery Summary Required

When finished, reply with:

```text
PR10B 完成。

修改文件：
- ...

核心变更：
- ...

验证结果：
- ...

关键样例结果：
- 宁波银行: action=..., confidence=...
- 贵州茅台: action=..., confidence=...
- 比亚迪: action=..., confidence=...
- 000820/*ST sample: action=..., confidence=...

已确认：
- confidence remains int
- no new signal/action enum
- no dead iWencai routes
- macro cannot force buy
- degraded risk metrics cannot force sell/reject alone
```
