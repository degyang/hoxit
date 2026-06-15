# PR-REPORT-004: UZEN DCF/Comps Input Quality

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-report-004-uzen-dcf-comps-input-quality`

## Design

`docs/superpowers/plans/2026-06-15-uzen-report-envelope-phase4.md`

## Goal

Make DCF and Comps missing-data behavior easier to audit by adding compact input-quality summaries.

## Scope

- Add `input_quality` to `analysis["dcf"]`.
- Add `input_quality` to `analysis["comps"]`.
- Render compact input-quality lines in DCF and Comps Markdown sections.
- Add tests for available, missing, and proxy-used cases.

## Out of Scope

- No DCF formula changes.
- No Comps median/position logic changes except quality metadata.
- No new data source.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-REPORT-004-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

DCF quality:

```json
"input_quality": {
  "required": ["net_profit", "share_count"],
  "available": ["market_price", "net_profit"],
  "missing": ["share_count"],
  "proxy_used": ["net_profit_as_cash_flow"]
}
```

Comps quality:

```json
"input_quality": {
  "peer_rows": 5,
  "pe_samples": 5,
  "pb_samples": 5,
  "missing": []
}
```

## Acceptance Criteria

- [ ] DCF JSON exposes required, available, missing, and proxy-used input quality.
- [ ] Comps JSON exposes peer row and sample counts.
- [ ] Markdown summarizes quality without raw dict dumps.
- [ ] Existing DCF/Comps numeric behavior remains unchanged.

## Test Requirements

- [ ] Add DCF input-quality computed test.
- [ ] Add DCF missing input-quality test.
- [ ] Add Comps input-quality test.
- [ ] Add Markdown input-quality test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-REPORT-003 approved or merged.

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

Revert the PR commit. DCF/Comps return to existing status/warnings-only quality behavior.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-REPORT-003 review.
