# PR-SPINE-001: UZEN Dimension Layer

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-spine-001-uzen-dimension-layer`

## Design

`docs/superpowers/plans/2026-06-15-uzen-research-spine-phase5.md`

## Goal

Add a deterministic `analysis["dimensions"]` layer that summarizes current UZEN analysis areas without changing existing CLI behavior or report sections.

## Scope

- Add internal dimension summary helper.
- Attach `analysis["dimensions"]` inside `analyze_snapshot()`.
- Include initial dimensions: `basic`, `market`, `valuation`, `fundamentals`, `capital_flow`, `panel`, `risk`, `lhb`, `dcf`, `comps`.
- Derive dimension status and quality from existing snapshot sources, source quality, and analysis objects.
- Add tests in `tests/test_uzen.py`.

## Out of Scope

- No synthesis layer.
- No Markdown section changes.
- No report self-review.
- No agent envelope changes.
- No new data provider.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-SPINE-001-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

`analysis["dimensions"]` must include records shaped like:

```json
{
  "status": "computed",
  "quality": "full",
  "inputs": ["quote", "metrics"],
  "outputs": ["summary"],
  "warnings": []
}
```

Allowed statuses:

- `computed`
- `partial`
- `data_needed`
- `unsupported`

Allowed qualities:

- `full`
- `partial`
- `missing`
- `skipped`
- `error`

## Acceptance Criteria

- [ ] JSON artifact includes `analysis["dimensions"]`.
- [ ] All required dimension keys exist.
- [ ] Each dimension has `status`, `quality`, `inputs`, `outputs`, and `warnings`.
- [ ] Existing analysis keys remain unchanged.
- [ ] Existing Markdown output remains unchanged.
- [ ] No new data source is introduced.

## Test Requirements

- [ ] Add dimension schema test.
- [ ] Add missing/skipped source behavior test.
- [ ] Add JSON artifact persistence test.
- [ ] Existing UZEN tests pass.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- Phase 4 merged on `main`.

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

Revert the PR commit. Existing analysis output returns to Phase 4 shape without `analysis["dimensions"]`.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it.
