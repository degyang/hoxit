# PR-DATA-002: UZEN Snapshot Data Coverage

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-data-002-uzen-snapshot-data-coverage`

## Design

- `docs/superpowers/specs/2026-06-16-uzen-phase6-a-share-data-gap-review.md`
- `docs/superpowers/plans/2026-06-16-uzen-a-share-data-coverage-phase6.md`

## Goal

Wire PR-DATA-001 hoxit interfaces into UZEN snapshot collection and data quality records.

## Scope

- Extend `UzenDataProvider` with new optional callables.
- Add mode source keys for governance, business, events, and policy/industry context if available.
- Update `collect_snapshot()` to collect the new sources with neutral defaults.
- Add `data_quality.sources` records for each new source.
- Keep existing JSON keys and CLI behavior compatible.
- Add tests in `tests/test_uzen.py`.

## Out of Scope

- No new hoxit interface functions.
- No synthesis changes beyond preserving existing output.
- No Markdown rendering changes.
- No docs sync outside implementation report and board.

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- Later PR tickets

## Acceptance Criteria

- [ ] Snapshot JSON includes new source objects under stable keys.
- [ ] Existing provider tests can omit new callables or use neutral defaults.
- [ ] Mode profiles skip heavy sources where appropriate.
- [ ] `data_quality.sources` distinguishes `full`, `missing`, `error`, and `skipped`.
- [ ] Existing Phase 5 tests still pass.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on PR-DATA-001 approved or merged.

## Stop Condition

After implementation, verification, implementation report, commit, and push, stop for Codex review. Do not begin PR-DATA-003.

## Rollback Notes

Revert the PR commit. New hoxit functions remain available but UZEN returns to Phase 5 snapshot shape.
