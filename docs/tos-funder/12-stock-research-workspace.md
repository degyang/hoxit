# PR12 Design: Stock Research Workspace

Created: 2026-06-03 14:14:41 Asia/Shanghai

## Purpose

PR12 turns `tos-funder` from a set of analysis commands into a repeatable stock research workspace.

The current system can analyze a stock through value, growth, quant, sentiment, tactical, macro, risk, and portfolio layers. What is missing is the operational skill shape:

- first-time full research should create a durable stock workspace
- redundant mode should preserve each analyst/layer report, not only final summary
- later tracking should reuse existing reports and run incremental updates by default
- outputs should be organized per stock and per run
- every run should update a lightweight state file for future routing

This PR should not create a new investment model. It creates the workflow and persistence layer around existing `tos-funder` commands.

## Target User Experience

First run:

```text
/tos-funder-stock-research 宁波银行 mode=full detail=redundant
```

Expected behavior:

- resolve target as `宁波银行 / 002142`
- create `outputs/stocks/宁波银行-002142/`
- run the full analysis chain
- write separate reports for each layer
- write a final summary
- write `_state.json`
- write or update `_index.md`

Later run:

```text
/tos-funder-stock-research 宁波银行
```

Expected behavior:

- detect existing `outputs/stocks/宁波银行-002142/_state.json`
- default to `mode=incremental`
- update only high-change layers unless user explicitly asks for full refresh
- write a new dated incremental run directory
- compare against previous run
- preserve old reports

Explicit refresh:

```text
/tos-funder-stock-research 宁波银行 mode=refresh layers=technicals,risk,sentiment
```

Expected behavior:

- only refresh requested layers
- generate delta summary
- update state

## Command Shape

Create a new orchestration command:

```text
/tos-funder-stock-research <股票代码或名称> [mode=auto|full|incremental|refresh] [detail=redundant|normal|compact] [layers=all|value,growth,quant,sentiment,risk,tactical,macro,portfolio] [date=YYYY-MM-DD]
```

This command is not an analyst. It is a workspace orchestrator.

It consumes existing commands:

- `/tos-funder-value-buffett`
- `/tos-funder-value-graham`
- `/tos-funder-growth`
- `/tos-funder-quant-fundamentals`
- `/tos-funder-quant-price-series`
- `/tos-funder-quant-technicals`
- `/tos-funder-quant-sentiment`
- `/tos-funder-risk-manager`
- `/tos-funder-tactical`
- `/tos-funder-macro-topdown`
- `/tos-funder-portfolio`

It produces:

- stock workspace directories
- per-run markdown reports
- `_state.json`
- `_index.md`
- run manifest

It does not replace `/tos-funder-analyze` or `/tos-funder-portfolio`.

## Mode Semantics

### `mode=auto`

Default mode.

Routing:

- if no stock workspace exists -> `full`
- if workspace exists -> `incremental`
- if required state is unreadable -> `incremental` with warning, or `full` if no prior full run can be identified

### `mode=full`

Use when:

- first-time analysis
- user explicitly says full / complete / redundant /重新完整分析
- previous analysis is stale or structurally incomplete

Run all major layers:

1. target resolution
2. quant price-series prerequisite
3. value Buffett
4. value Graham
5. growth aggregate
6. quant fundamentals
7. quant technicals
8. quant sentiment
9. risk-manager
10. tactical synthesis
11. macro topdown
12. portfolio decision
13. final summary

### `mode=incremental`

Default for existing stock workspace.

Update high-change layers:

- price-series
- technicals
- sentiment / announcement / report search
- risk-manager
- tactical
- macro-topdown
- portfolio decision

Refresh low-change layers only when triggers are present:

- value: annual report, major capital action, large valuation change, user request
- growth/fundamentals: quarterly/annual report, material earnings change, user request

### `mode=refresh`

Partial update.

Requires `layers=...`.

Examples:

```text
layers=technicals,risk
layers=sentiment,tactical
layers=value,growth
```

If `layers` is missing, ask for clarification or default to:

```text
layers=technicals,risk,sentiment,tactical,portfolio
```

## Detail Semantics

### `detail=redundant`

Use for first full research.

Write every layer report, including:

- facts used
- assumptions
- route coverage
- source status
- scoring
- risks and opportunities
- expert/persona interpretation where applicable
- next-step prompts

### `detail=normal`

Write:

- updated layer reports
- final summary
- important raw source references

Do not expand every stable historical layer.

### `detail=compact`

Write:

- delta summary
- changed facts
- changed signals
- changed risk/opportunity
- updated portfolio decision

No long analyst essays unless explicitly requested.

## Output Directory Protocol

Base directory:

```text
outputs/stocks/
```

Stock directory:

```text
outputs/stocks/<股票名>-<代码>/
```

Example:

```text
outputs/stocks/宁波银行-002142/
```

Required files:

```text
_index.md
_state.json
```

Run directories:

```text
YYYY-MM-DD-full/
YYYY-MM-DD-incremental/
YYYY-MM-DD-refresh-<layers>/
```

Example:

```text
outputs/stocks/宁波银行-002142/
  _index.md
  _state.json
  2026-06-03-full/
    _manifest.json
    00-summary.md
    01-value-buffett.md
    02-value-graham.md
    03-growth.md
    04-quant-fundamentals.md
    05-price-series.md
    06-quant-technicals.md
    07-sentiment.md
    08-risk-manager.md
    09-tactical.md
    10-macro-topdown.md
    11-portfolio-decision.md
    raw/
      iwencai-queries.json
      market-series-summary.json
  2026-06-10-incremental/
    _manifest.json
    00-delta-summary.md
    05-price-series-delta.md
    06-quant-technicals-delta.md
    07-sentiment-delta.md
    08-risk-manager-delta.md
    09-tactical-delta.md
    10-macro-topdown-delta.md
    11-portfolio-decision-delta.md
```

## State File

`_state.json` should be compact and machine-readable.

Minimum schema:

```json
{
  "schema_version": "1.0",
  "stock": {
    "code": "002142",
    "name": "宁波银行",
    "market": "A-share",
    "industry": "银行"
  },
  "workspace": {
    "created_at": "2026-06-03",
    "updated_at": "2026-06-03",
    "base_path": "outputs/stocks/宁波银行-002142"
  },
  "latest_runs": {
    "full": "2026-06-03-full",
    "incremental": null,
    "refresh": null
  },
  "latest_decision": {
    "action": "hold",
    "confidence": 69,
    "source_run": "2026-06-03-full"
  },
  "latest_signals": {
    "value_buffett": {"signal": "bullish", "confidence": 75, "run": "2026-06-03-full"},
    "value_graham": {"signal": "neutral", "confidence": 65, "run": "2026-06-03-full"},
    "growth": {"signal": "bullish", "confidence": 70, "run": "2026-06-03-full"},
    "technicals": {"signal": "bearish", "strength": "weak", "confidence": 55, "run": "2026-06-03-full"},
    "risk": {"risk_level": "moderate", "risk_metric_status": "valid", "run": "2026-06-03-full"},
    "tactical": {"signal": "neutral", "confidence": 55, "run": "2026-06-03-full"},
    "macro": {"signal": "neutral", "coverage_status": "partial", "confidence": 70, "run": "2026-06-03-full"}
  },
  "watch_triggers": [
    {"type": "technical", "condition": "MA5 > MA20", "reason": "entry add confirmation"},
    {"type": "fundamental", "condition": "next quarterly report", "reason": "refresh growth/fundamentals"}
  ],
  "open_questions": [],
  "data_quality": {
    "last_adjustment_status": "verified",
    "last_risk_metric_status": "valid",
    "manual_review_required": false
  }
}
```

## Manifest File

Each run directory must include `_manifest.json`.

Minimum schema:

```json
{
  "run_id": "2026-06-03-full",
  "created_at": "2026-06-03T14:20:00+08:00",
  "mode": "full",
  "detail": "redundant",
  "target": {"code": "002142", "name": "宁波银行"},
  "commands_planned": [],
  "commands_completed": [],
  "reports_written": [],
  "source_status": {
    "iwencai": "used",
    "mootdx": "used",
    "fallbacks": []
  },
  "previous_run": null,
  "summary": {
    "final_action": "hold",
    "confidence": 69
  }
}
```

## `_index.md`

The stock index should be human-readable.

Minimum content:

```text
# 宁波银行 002142

## Latest Decision

- Action:
- Confidence:
- Latest run:

## Runs

| Date | Mode | Summary | Key change |

## Current Watch Triggers

## Open Questions

## File Map
```

## Full Run Report Set

`detail=redundant` full run should create these report files:

| File | Purpose | Source command |
|---|---|---|
| `00-summary.md` | final integrated summary | stock-research orchestrator |
| `01-value-buffett.md` | Buffett quality/moat/capital allocation | `/tos-funder-value-buffett` |
| `02-value-graham.md` | Graham margin-of-safety | `/tos-funder-value-graham` |
| `03-growth.md` | Fisher/Lynch/growth aggregate | `/tos-funder-growth` |
| `04-quant-fundamentals.md` | deterministic fundamentals | `/tos-funder-quant-fundamentals` |
| `05-price-series.md` | canonical OHLCV and data quality | `/tos-funder-quant-price-series` |
| `06-quant-technicals.md` | local technical indicators | `/tos-funder-quant-technicals` |
| `07-sentiment.md` | announcements/reports/event proxy | `/tos-funder-quant-sentiment` |
| `08-risk-manager.md` | risk metrics and constraints | `/tos-funder-risk-manager` |
| `09-tactical.md` | catalyst/tail-risk synthesis | `/tos-funder-tactical` |
| `10-macro-topdown.md` | market regime context | `/tos-funder-macro-topdown` |
| `11-portfolio-decision.md` | final portfolio decision | `/tos-funder-portfolio` |

## Incremental Run Report Set

Default incremental run should create:

| File | Purpose |
|---|---|
| `00-delta-summary.md` | what changed since previous run |
| `05-price-series-delta.md` | price-series changes |
| `06-quant-technicals-delta.md` | technical signal changes |
| `07-sentiment-delta.md` | new announcements/reports |
| `08-risk-manager-delta.md` | risk metric changes |
| `09-tactical-delta.md` | catalyst/tail-risk changes |
| `10-macro-topdown-delta.md` | market-regime changes |
| `11-portfolio-decision-delta.md` | updated final action |

## Incremental Decision Rules

When existing workspace is found:

1. Read `_state.json`.
2. Identify last full run and latest run.
3. Compare current date and requested mode.
4. If `mode=auto`, choose `incremental`.
5. Reuse stable reports from latest full run.
6. Refresh high-change layers.
7. Refresh low-change layers only if triggered.
8. Generate delta summary.
9. Update `_state.json`.
10. Append run to `_index.md`.

Low-change refresh triggers:

- quarterly/annual report released
- major announcement affecting capital allocation, litigation, regulation, M&A, share issuance, dividends
- large valuation regime change
- user explicitly requests full refresh or specific layer refresh
- previous data quality was blocked/degraded and can now be repaired

## Summary Report Structure

`00-summary.md` and `00-delta-summary.md` should follow:

```text
# <股票名> <代码> - <Full/Incremental> Research Summary

## Executive View

## Final Portfolio Decision

## Signal Matrix

| Layer | Signal | Confidence | Change vs Previous | Source report |

## Key Facts

## Opportunities

## Risks

## What Changed

## Watch Triggers

## Open Questions

## Files Written
```

## Data Source Boundary

The workspace orchestrator must preserve accepted boundaries:

- iWencai: fundamentals, valuation, announcements, reports, broad A-share natural-language queries
- mootdx/TDX: OHLCV, quote, intraday, technical indicators, risk metrics
- iWencai OHLCV: fallback only, labeled `iwencai_fallback`
- `management` route: validated narrow fields only
- `business` and `event query2data`: blocked
- `management` insider fields: blocked

## Acceptance Criteria

PR12 is acceptable if:

1. New command `/tos-funder-stock-research` exists and is routed in `SKILL.md`.
2. Workspace protocol is documented in `tos-funder/references/stock-research-workspace.md`.
3. `docs/tos-funder/validation-pr12.md` validates first-run full mode and second-run incremental mode.
4. Full mode writes separate layer reports and does not collapse everything into one summary.
5. Incremental mode reads existing `_state.json` and avoids full recomputation by default.
6. `_state.json`, `_index.md`, and `_manifest.json` schemas are documented.
7. No existing analyst command is rewritten into a workspace command.
8. Existing final action boundary remains: portfolio produces final portfolio decisions.
9. Output paths are deterministic and do not overwrite prior runs.
10. Data source boundaries from PR11 remain intact.

