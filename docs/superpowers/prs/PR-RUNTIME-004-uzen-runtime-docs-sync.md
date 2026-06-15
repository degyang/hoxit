# PR-RUNTIME-004: UZEN Runtime Docs Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-runtime-004-uzen-runtime-docs-sync`

## Design

`docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`

## Goal

Update user-facing docs after runtime mode execution, source quality, and Markdown contract are implemented.

## Scope

Synchronize docs with actual tested runtime behavior.

## Out of Scope

- Do not change production code.
- Do not add tests unless documentation examples require a smoke command.
- Do not add new runtime capabilities.

## Files Likely to Change

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `docs/superpowers/status/PR-RUNTIME-004-implementation.md`

## Must Not Change

- `hoxit/`
- `tests/`
- `docs/API_DEVLOG.md`
- `uzen-skills/skills/*/SKILL.md` unless a specific runtime fact is stale.

## Required Behavior

Document:

- mode-specific execution profiles;
- structured `data_quality.sources`;
- Markdown report contract;
- current runtime limitations;
- deferred UZI parity items.

Keep docs A-share-first and hoxit-first.

## Acceptance Criteria

- [ ] `docs/INTERFACES.md` reflects current UZEN JSON and Markdown behavior.
- [ ] Command docs do not claim unavailable runtime capabilities.
- [ ] Docs clearly distinguish current runtime support from deferred UZI parity.
- [ ] No production code changes are included.

## Test Requirements

- [ ] Run doc formatting check with `git diff --check`.
- [ ] Run CLI help smoke to verify documented command still exists.

## Verification Commands

```bash
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers/status/PR-RUNTIME-004-implementation.md
.venv/bin/hoxit uzen --help
```

## Dependencies

Depends on:

- PR-RUNTIME-003 APPROVED or MERGED

## Definition of Done

- [ ] Implementation complete
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Current PR status moved to REVIEW_READY
- [ ] Executor stopped after current PR and did not begin later work
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review.

## Rollback Notes

Revert this PR to restore previous documentation. No runtime behavior is affected.

## Handoff Notes for Claude Code

Follow this ticket exactly. Do not expand scope. If PR-RUNTIME-003 is not approved or merged, stop and report the dependency blocker.
