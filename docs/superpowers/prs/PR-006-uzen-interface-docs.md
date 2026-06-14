# PR-006: UZEN Interface Documentation

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-006-uzen-interface-docs`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Document the public UZEN CLI and under-documented signal helpers.

## Scope

- Update `docs/INTERFACES.md` with `hoxit uzen` examples.
- Document output artifact names.
- Document that UZEN first version is A-share-only and JSON/Markdown-first.
- Add missing docs for existing signal helpers: margin trading, block trades, holder number changes, and dividends.
- Update `docs/API_DEVLOG.md` only if this PR or prior UZEN PRs add/change external endpoint behavior.

## Out of Scope

- Production code changes.
- New tests unless docs assertions are added elsewhere.
- Interface claims for deferred features.

## Files Likely to Change

- `docs/INTERFACES.md`
- `docs/API_DEVLOG.md` only if needed.

## Must Not Change

- `hoxit/`
- `tests/`
- `uzen-skills/`

## Acceptance Criteria

- [ ] `docs/INTERFACES.md` includes all seven UZEN commands.
- [ ] Docs state output files are `<code>-<mode>.json` and `<code>-<mode>.md`.
- [ ] Docs state non-A-share and HTML/share images are deferred.
- [ ] Existing signal helpers are documented.
- [ ] `docs/API_DEVLOG.md` is untouched if no external interface changed.

## Test Requirements

- [ ] No code tests required for docs-only changes.
- [ ] Run full tests as a regression check if previous PRs are already merged.

## Verification Commands

```bash
git diff --check -- docs/INTERFACES.md docs/API_DEVLOG.md
.venv/bin/python -m pytest -q
```

## Dependencies

Depends on:

- PR-005 approved or merged.

## Definition of Done

- [ ] Documentation complete.
- [ ] Verification commands pass or unrelated existing failures are recorded.
- [ ] Commit created on branch `agent/cc/pr-006-uzen-interface-docs`.
- [ ] Implementation report written to `docs/superpowers/status/PR-006-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove only public documentation changes.

## Handoff Notes for Claude Code

Follow Task 6 in the implementation plan. Do not edit production code in this PR.
