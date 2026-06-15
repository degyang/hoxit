# PR-ANALYTICS-004: UZEN Investor Panel Signals

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-analytics-004-uzen-investor-panel-signals`

## Design

`docs/superpowers/plans/2026-06-15-uzen-analytical-models-phase3.md`

## Goal

Move the investor panel from a scalar PE/ROE score toward a stable deterministic signal schema while preserving existing summary fields.

## Scope

- Extend `analysis["panel"]` with `signals` and `vote_distribution`.
- Preserve `score`, `verdict`, and `reasons`.
- Implement only deterministic baseline investor archetypes:
  - value
  - quality
  - growth
  - momentum
  - hot-money suitability when data exists
- Render a compact Chinese-first panel summary in Markdown.
- Add schema and aggregation tests.

## Out of Scope

- No full 65-investor UZI parity.
- No LLM role-play.
- No external persona files unless already present and approved.
- No DCF, comps, or risk model changes.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-ANALYTICS-004-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `pyproject.toml`
- `uzen-skills/`
- `docs/INTERFACES.md`
- later PR tickets

## Required Behavior

Panel output must include:

```python
{
    "score": int,
    "verdict": "bullish" | "neutral" | "bearish",
    "reasons": list[str],
    "signals": [
        {
            "investor_id": str,
            "name": str,
            "group": str,
            "signal": "pass" | "fail" | "neutral" | "data_needed",
            "score": int,
            "confidence": float,
            "reasoning": list[str],
        }
    ],
    "vote_distribution": dict,
}
```

All persona rules must be deterministic and explain their evidence from hoxit snapshot fields.

## Acceptance Criteria

- [ ] `panel-only` JSON includes `signals` and `vote_distribution`.
- [ ] Existing `score`, `verdict`, and `reasons` remain available.
- [ ] Missing data produces `data_needed` signals where appropriate.
- [ ] Markdown shows panel signal distribution without raw dict/list dumps.

## Test Requirements

- [ ] Add schema test for all signal fields.
- [ ] Add vote aggregation test.
- [ ] Add missing-data signal test.
- [ ] Add Markdown panel summary test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-ANALYTICS-003 approved or merged.

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Board row moved to REVIEW_READY
- [ ] Current branch committed
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert the PR commit. Existing scalar panel behavior should remain recoverable.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-ANALYTICS-003 review.
