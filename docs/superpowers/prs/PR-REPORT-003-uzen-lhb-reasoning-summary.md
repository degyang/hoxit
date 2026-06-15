# PR-REPORT-003: UZEN LHB Reasoning Summary

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-report-003-uzen-lhb-reasoning-summary`

## Design

`docs/superpowers/plans/2026-06-15-uzen-report-envelope-phase4.md`

## Goal

Add a deterministic LHB reasoning summary for `lhb-analyzer` without claiming unsupported seat-level interpretation.

## Scope

- Add `analysis["lhb"]`.
- Derive row count, available net-buy fields, and simple signals from `sources.signals.dragon_tiger`.
- Render a focused LHB Markdown section.
- Add tests for data available and missing.

## Out of Scope

- No new data provider.
- No seat-level institution/hot-money classification unless already present in rows.
- No historical seat pattern inference.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-REPORT-003-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

`analysis["lhb"]` shape:

```json
{
  "status": "computed" | "data_needed",
  "rows": 1,
  "net_buy": 2000.0,
  "has_dragon_tiger": true,
  "signals": ["龙虎榜净买入为正"],
  "warnings": []
}
```

When no dragon-tiger rows exist, return `status: "data_needed"` with a warning.

## Acceptance Criteria

- [ ] `lhb-analyzer` JSON includes `analysis["lhb"]`.
- [ ] Markdown has a compact LHB section.
- [ ] Missing rows return `data_needed`, not fake seat interpretation.
- [ ] Existing tests pass.

## Test Requirements

- [ ] Add computed LHB summary test.
- [ ] Add missing LHB rows test.
- [ ] Add Markdown LHB section test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-REPORT-002 approved or merged.

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

Revert the PR commit. `lhb-analyzer` returns to row-count-only reporting.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-REPORT-002 review.
