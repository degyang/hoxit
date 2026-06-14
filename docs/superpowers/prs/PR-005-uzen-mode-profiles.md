# PR-005: UZEN Mode Profiles

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-005-uzen-mode-profiles`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Add explicit first-version mode profiles so each UZEN command is labeled and reviewable.

## Scope

- Add `_mode_profile()`.
- Add `analysis.mode_profile`.
- Distinguish `quick-scan`, `dcf`, `comps`, `panel-only`, `scan-trap`, `lhb-analyzer`, and `analyze-stock`.
- Add tests for mode labels.

## Out of Scope

- Different provider call graphs per mode unless needed by existing tests.
- Full UZI command parity.
- Documentation updates.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `docs/API_DEVLOG.md`
- `uzen-skills/`

## Acceptance Criteria

- [ ] `quick-scan` profile has `depth == "lite"`.
- [ ] `panel-only` profile has `primary_section == "panel"`.
- [ ] `lhb-analyzer` profile has `primary_section == "dragon_tiger"`.
- [ ] Unknown mode falls back to standard analyze-stock profile.
- [ ] Existing UZEN tests still pass.

## Test Requirements

- [ ] Extend `tests/test_uzen.py` for mode profile behavior.
- [ ] Cover fallback behavior.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

## Dependencies

Depends on:

- PR-004 approved or merged.

## Definition of Done

- [ ] Implementation complete.
- [ ] Tests pass.
- [ ] Verification commands pass.
- [ ] Commit created on branch `agent/cc/pr-005-uzen-mode-profiles`.
- [ ] Implementation report written to `docs/superpowers/status/PR-005-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove mode profiles without removing CLI support.

## Handoff Notes for Claude Code

Follow Task 5 in the implementation plan. Keep mode profiles as metadata only unless a test requires a minimal behavior change.
