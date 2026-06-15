# PR-ANALYTICS-002: UZEN Comparable Summary

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-analytics-002-uzen-comps-summary`

## Design

`docs/superpowers/plans/2026-06-15-uzen-analytical-models-phase3.md`

## Goal

Make `hoxit uzen comps` produce a hoxit-native comparable-company or industry-multiple summary, with explicit insufficiency reporting when peer data is not available.

## Scope

- Add a comps helper in `hoxit/uzen.py`.
- Attach the result under `snapshot["analysis"]["comps"]`.
- Use existing `sources.metrics`, `sources.fundamentals`, and `sources.signals.industry`.
- Render a compact Chinese-first comps section in Markdown.
- Add unit tests for available and missing peer multiple cases.

## Out of Scope

- No new iwencai peer interface unless separately approved.
- No provider-chain import from UZI.
- No DCF changes.
- No risk split or panel changes.
- No docs sync beyond implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-ANALYTICS-002-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `pyproject.toml`
- `uzen-skills/`
- `docs/INTERFACES.md`
- later PR tickets

## Required Behavior

The comps object must use this shape:

```python
{
    "status": "computed" | "data_needed",
    "subject": dict,
    "rows": list[dict],
    "median_pe": float | None,
    "median_pb": float | None,
    "position": "below_median" | "near_median" | "above_median" | "unknown",
    "warnings": list[str],
}
```

If usable peer multiples are missing, preserve sample counts and return `data_needed` with warnings.

## Acceptance Criteria

- [ ] `analyze_snapshot()` includes `analysis["comps"]`.
- [ ] `comps` mode JSON distinguishes computed comps from insufficient peer data.
- [ ] Markdown includes peer/industry sample count and median multiples when available.
- [ ] Tests prove missing peer multiples do not create fake medians.

## Test Requirements

- [ ] Add peer-multiple computed test.
- [ ] Add missing peer-data test.
- [ ] Add Markdown comps section test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-ANALYTICS-001 approved or merged.

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

Revert the PR commit. The change should only affect derived comps analysis and tests.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-ANALYTICS-001 review.
