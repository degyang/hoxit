# PR-SPINE-004: UZEN Deep Review Envelope

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-spine-004-uzen-deep-review-envelope`

## Design

`docs/superpowers/plans/2026-06-15-uzen-research-spine-phase5.md`

## Goal

Extend the optional agent analysis envelope with validated deep-review fields while preserving backward compatibility with Phase 4 `agent_analysis` JSON files.

## Scope

- Extend `_empty_agent_analysis()`.
- Extend `_validate_agent_analysis()`.
- Render new provided fields in `## Agent 定性分析`.
- Add tests for validation, defaults, backward compatibility, JSON artifact, and Markdown.

## Out of Scope

- No LLM calls.
- No required agent review mode.
- No mutation of deterministic analysis objects.
- No synthesis rewrite based on agent fields.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `tests/test_cli.py` only if CLI validation behavior changes
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-SPINE-004-implementation.md`

## Must Not Change

- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

Extend envelope with:

```json
{
  "data_gap_acknowledged": {},
  "dimension_commentary": {},
  "panel_insights": ""
}
```

Validation:

- `data_gap_acknowledged` must be `dict[str, str]`.
- `dimension_commentary` must be `dict[str, str]`.
- `panel_insights` must be a string.
- Existing files without these keys remain valid and receive defaults.

## Acceptance Criteria

- [ ] Default envelope includes new fields.
- [ ] Partial Phase 4 envelope remains valid.
- [ ] Invalid new field types raise clear `ValueError`.
- [ ] JSON artifact includes new fields.
- [ ] Markdown renders provided new fields without raw dict dumps.

## Test Requirements

- [ ] Add default new-fields test.
- [ ] Add partial backward-compatible envelope test.
- [ ] Add invalid type tests.
- [ ] Add Markdown rendering test for new fields.
- [ ] Run CLI tests if CLI path is touched.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py hoxit/cli.py tests docs/superpowers
```

## Dependencies

Depends on:

- PR-SPINE-003 approved or merged.

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

Revert the PR commit. Agent analysis returns to Phase 4 envelope shape.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-SPINE-003 review.
