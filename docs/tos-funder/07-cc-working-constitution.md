# CC Working Constitution

This constitution is mandatory for every Claude Code PR in Trading Funder. Read it before implementation and use it again as the final self-review checklist.

## Core Principles

### 1. Evidence Before Conclusion

Do not turn a sample observation into a universal claim.

Allowed:
- "Validated on these samples."
- "The path is executable."
- "This metric is usable with caveats."

Not allowed:
- "Fully reliable."
- "Correctness confirmed."
- "This proves qfq is correct."

When unsure, write the uncertainty explicitly and define the next verification step.

### 2. Schema Continuity

Every PR must consume the latest accepted schema, not the schema from the PR you started with.

Before editing, check:
- `tos-funder/SKILL.md`
- the command you consume
- the reference that defines the output schema
- the latest validation document for that family

Current signal schema:

```text
signal: bullish | neutral | bearish | blocked
strength: strong | weak | flat
confidence: 0-100
action: buy | hold | sell | reduce | watch | reject | blocked
```

Do not invent new primary signal enums such as `weak_bullish` or `weak_bearish`. Use `strength` instead.

### 3. Metrics Are Not Judgments

Separate these layers in every output:

```text
facts
computed_metrics
data_quality_warnings
interpretation
action_constraints
final_action
```

Examples:
- Max drawdown is a metric.
- "Corporate-action distortion possible" is a data-quality warning.
- "No new buy until verified" is an action constraint.
- `reject` is a final action and needs stronger evidence than a degraded metric.

### 4. Data Quality Before Risk Veto

Do not convert suspicious data directly into a hard veto.

If a metric is affected by any of the following, mark it degraded first:
- corporate action / split / dividend adjustment uncertainty
- NaN suspension rows
- incomplete latest bar
- fallback source
- missing amount / volume fields
- low row count or poor date alignment

Hard vetoes require `risk_metric_status: valid`. If `risk_metric_status: degraded`, prefer `watch`, `reduce`, or `manual_review_required`.

### 5. Source Boundaries Are Architecture

Use the right source by data type:

| Data need | Primary source |
|---|---|
| fundamentals, valuation snapshots, announcements, reports | iWencai |
| OHLCV, technicals, intraday, risk, portfolio correlation | hoxit `market bars` / mootdx |
| PE/PB/market cap snapshot supplement | Tencent metrics |

Do not make iWencai RSI/MACD/OHLCV the primary technical path. iWencai OHLCV is fallback-only and must be labeled `source: iwencai_fallback`.

### 6. Formula Fidelity With Adaptation Labels

If a formula is copied from `ai-hedge-fund`, say so. If it is adapted for A shares or for available fields, label the adaptation.

Use:

```text
source_formula:
adaptation:
assumption:
impact_if_wrong:
```

Never imply exact source parity when sector rules, data fields, or A-share constraints changed the logic.

### 7. Downstream Consumability

Every command output must be directly consumable by the next command.

Before finishing, verify:
- Field names match existing references.
- Signal enums match the current schema.
- Missing/degraded fields are machine-readable.
- Portfolio can consume the command without interpreting prose.

### 8. A-Share Semantics

Use A-share-compatible actions only:

```text
buy | hold | sell | reduce | watch | reject | blocked
```

Do not use `short` or `cover` unless a command explicitly verifies short eligibility.

## PR Self-Review Checklist

Before reporting completion, answer these checks:

1. Did I read the latest accepted command/reference schema?
2. Did I avoid new unapproved signal enums?
3. Did I separate facts, metrics, warnings, interpretations, and actions?
4. Did I label fallback and degraded data explicitly?
5. Did I avoid overclaiming from sample validation?
6. Did I distinguish data-quality veto from risk veto?
7. Can the next command consume my output without parsing prose?
8. Did I keep iWencai and TDX/mootdx source boundaries intact?
9. Did I document unresolved questions as next verification tasks?

## Required Delivery Format

Every CC PR summary must include:

```text
Files changed:

Schema consumed:

Validation performed:

Data-quality warnings:

Metrics degraded:

Downstream compatibility check:

Unresolved questions:

Self-review against CC Working Constitution:
```

If any self-review item fails, do not mark the PR complete. Report it as a known gap.
