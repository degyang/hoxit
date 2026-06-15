# PR-DATA-003: UZEN Coverage Dimensions

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-data-003-uzen-coverage-dimensions`

## Design

- `docs/superpowers/specs/2026-06-16-uzen-phase6-a-share-data-gap-review.md`
- `docs/superpowers/plans/2026-06-16-uzen-a-share-data-coverage-phase6.md`

## Goal

Extend `analysis["dimensions"]` so UZEN can express A-share data coverage closer to UZI Task 1 without claiming full UZI parity.

## Scope

- Add or extend dimensions for:
  - governance / ownership;
  - business / supply-chain;
  - events / catalysts;
  - policy / macro context;
  - sentiment / social evidence boundary;
  - LHB detail coverage.
- Preserve existing 10 dimensions for backward compatibility.
- Add `data_needed` or `unsupported` states for deferred UZI dimensions such as materials, futures, moat/patents, and contests.
- Add tests for computed, skipped, missing, and unsupported states.

## Out of Scope

- No new provider calls.
- No synthesis or Markdown changes.
- No scoring engine with 1-10 UZI dimension scores.
- No 65/66 persona panel.

## Must Not Change

- `hoxit/cli.py`
- Provider modules
- `docs/INTERFACES.md`
- `uzen-skills/`

## Acceptance Criteria

- [ ] `analysis["dimensions"]` includes new coverage dimensions.
- [ ] Each dimension has stable `status`, `quality`, `inputs`, `outputs`, `warnings`.
- [ ] Deferred UZI dimensions are explicit, not silently omitted.
- [ ] Existing consumers of prior dimensions keep working.
- [ ] Tests cover mode-specific skipped sources.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on PR-DATA-002 approved or merged.

## Stop Condition

After implementation, verification, implementation report, commit, and push, stop for Codex review. Do not begin PR-DATA-004.

## Rollback Notes

Revert the PR commit. UZEN returns to PR-DATA-002 snapshot shape with Phase 5 dimensions.
