# PR-DATA-005: UZEN Phase 6 Docs And Live Test Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-data-005-uzen-phase6-docs-live-tests-sync`

## Design

- `docs/superpowers/specs/2026-06-16-uzen-phase6-a-share-data-gap-review.md`
- `docs/superpowers/plans/2026-06-16-uzen-a-share-data-coverage-phase6.md`

## Goal

Synchronize docs, skills, and optional live tests with Phase 6 A-share data coverage behavior.

## Scope

- Update `docs/INTERFACES.md`.
- Update `uzen-skills/README.md`.
- Update relevant `uzen-skills/commands/*.md`.
- Update relevant `uzen-skills/skills/*/SKILL.md`.
- Update `tests/test_live_endpoints.py` only for optional live coverage of new hoxit interfaces.
- Update `docs/API_DEVLOG.md` if PR-DATA-001 introduced or changed interfaces.
- Update board and implementation report.

## Out of Scope

- No production behavior changes.
- No new runtime capability claims beyond implemented Phase 6.
- No full UZI parity claim.
- No HTML/PNG/Playwright docs as current capability.

## Must Not Change

- `hoxit/uzen.py`
- provider modules
- unit test logic unless correcting stale examples
- later PR tickets

## Acceptance Criteria

- [ ] Docs are Chinese-first.
- [ ] Important terms may use Chinese + English pairing.
- [ ] Docs distinguish current Phase 6 coverage from deferred UZI dimensions.
- [ ] Docs explain new snapshot keys, dimensions, synthesis behavior, and unsupported boundaries.
- [ ] Optional live tests are marked integration/slow and skipped by default.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/hoxit uzen --help
git diff --check -- docs hoxit tests uzen-skills
```

## Dependencies

Depends on PR-DATA-004 approved or merged.

## Stop Condition

After implementation, verification, implementation report, commit, and push, stop for Codex review.

## Rollback Notes

Revert the PR commit. Runtime behavior from PR-DATA-001 through PR-DATA-004 remains intact.
