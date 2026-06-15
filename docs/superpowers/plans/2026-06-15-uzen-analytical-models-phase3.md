# UZEN Analytical Models Phase 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute this plan. Follow it step by step, verify each PR independently, and stop at the review gate after each assigned ticket.

**Goal:** Turn UZEN's focused commands from mode-shaped reports into A-share-first analytical models with deterministic, testable outputs.

**Architecture:** Keep hoxit as the only data boundary. Analytical helpers live inside `hoxit/uzen.py` unless a PR proves a separate module is needed. `collect_snapshot()` remains responsible for data collection and quality records. `analyze_snapshot()` adds derived analysis objects. `render_markdown()` presents compact Chinese-first report sections while raw JSON preserves full detail.

**Tech Stack:** Python stdlib, pytest, argparse CLI. Optional data dependencies stay behind existing hoxit provider functions. No new network calls in unit tests.

---

## Current Baseline

Runtime Phase 2 is complete:

- mode execution profiles control provider calls;
- per-source quality records exist with `full`, `partial`, `missing`, `error`, and `skipped`;
- Markdown avoids raw Python dict/list dumps;
- UZEN skill and command docs are Chinese-first for user-facing text.

The remaining gap is analytical depth. `dcf`, `comps`, `panel-only`, and `scan-trap` are currently mostly labels over shared summary logic. Phase 3 makes each focused mode produce a distinct, honest, hoxit-native analysis object.

## Non-Goals

- Do not import `Reference/UZI-Skill` runtime/provider code.
- Do not add one-off data scrapers under `uzen-skills/`.
- Do not add non-A-share support.
- Do not claim full UZI investor/persona parity.
- Do not label market-data flags as social or manipulation evidence.
- Do not change CLI command names or artifact paths unless explicitly assigned.

## PR Sequence

| PR | Title | Purpose |
| --- | --- | --- |
| PR-ANALYTICS-001 | UZEN Light DCF Model | Make `hoxit uzen dcf` return a traceable simplified DCF analysis. |
| PR-ANALYTICS-002 | UZEN Comparable Summary | Make `hoxit uzen comps` return peer/industry multiple context or an explicit insufficiency result. |
| PR-ANALYTICS-003 | UZEN Risk Model Split | Split deterministic market risk from future trap/social-risk evidence. |
| PR-ANALYTICS-004 | UZEN Investor Panel Signals | Replace the scalar-only panel with a stable signal schema and vote distribution. |
| PR-ANALYTICS-005 | UZEN Analytics Docs Sync | Update Chinese-first user docs for the new analytical outputs. |

Only one ticket may be implemented at a time. Claude Code must stop after each ticket's report, commit, and `REVIEW_READY` board update.

## PR-ANALYTICS-001 Implementation Notes

Add a deterministic DCF helper that accepts a snapshot and returns:

```python
{
    "status": "computed" | "data_needed",
    "inputs": {...},
    "assumptions": {
        "forecast_years": 5,
        "discount_rate": 0.10,
        "terminal_growth": 0.03,
        "growth_rate": ...
    },
    "intrinsic_value_per_share": ...,
    "market_price": ...,
    "margin_of_safety": ...,
    "sensitivity": [...],
    "warnings": [...]
}
```

Preferred inputs, in order:

- cash flow/profit proxy from `sources.finance`;
- market price from `sources.quote.price`;
- shares outstanding from metrics/finance if available;
- growth hints from valuation/fundamentals/finance only when numeric and traceable.

If enough inputs are missing, return `status: data_needed` with missing fields instead of fabricating values.

Tests should include:

- pure computed case with deterministic expected math;
- missing cash-flow/profit case;
- missing share count case;
- Markdown section appears for `dcf` mode and uses Chinese-first labels.

## PR-ANALYTICS-002 Implementation Notes

Add a comparable summary based on currently available hoxit data:

```python
{
    "status": "computed" | "data_needed",
    "subject": {...},
    "rows": [...],
    "median_pe": ...,
    "median_pb": ...,
    "position": "below_median" | "near_median" | "above_median" | "unknown",
    "warnings": [...]
}
```

Use `signals.industry` rows first. If peers lack PE/PB fields, return `data_needed` and preserve row count. Do not add iwencai peer queries unless the PR explicitly adds a reusable hoxit interface and tests it.

## PR-ANALYTICS-003 Implementation Notes

Rename the current deterministic risk object conceptually to `market_risk` and introduce a separate `trap_risk` schema for unsupported/future evidence:

```python
"market_risk": {
    "level": "low" | "medium" | "high",
    "basis": "market_data",
    "flags": [...]
},
"trap_risk": {
    "status": "unsupported" | "data_needed" | "computed",
    "basis": "social_evidence",
    "evidence": [],
    "warnings": [...]
}
```

Keep backward compatibility where practical, but Markdown must not imply social/manipulation evidence when only market data was checked.

## PR-ANALYTICS-004 Implementation Notes

Extend the panel while preserving `score`, `verdict`, and `reasons`:

```python
"panel": {
    "score": 60,
    "verdict": "neutral",
    "reasons": [...],
    "signals": [
        {
            "investor_id": "value",
            "name": "价值型投资者",
            "group": "valuation",
            "signal": "pass" | "fail" | "neutral" | "data_needed",
            "score": ...,
            "confidence": ...,
            "reasoning": [...]
        }
    ],
    "vote_distribution": {...}
}
```

Implement only deterministic A-share baseline personas: value, quality, growth, momentum, and hot-money suitability if data exists.

## PR-ANALYTICS-005 Implementation Notes

Update Chinese-first docs after runtime behavior is approved:

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- relevant `uzen-skills/commands/*.md`
- relevant `uzen-skills/skills/*/SKILL.md` only if runtime behavior changes their contracts

Important English terms may be written as bilingual labels, for example `折现率（Discount Rate）`.

## Verification

Each production PR should run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py uzen-skills docs
```

Docs-only PRs should run:

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

Before merge, Codex should run at least the ticket-specific test command and inspect the diff against the ticket scope.
