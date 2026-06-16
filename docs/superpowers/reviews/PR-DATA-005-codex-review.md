# PR-DATA-005 Codex Final Review

## Verdict

CHANGES_REQUESTED

## Scope Reviewed

- Branch: `agent/cc/pr-data-005-uzen-phase6-docs-live-tests-sync`
- Implementation commit: `3e61852 docs: sync UZEN Phase 6 coverage across docs, skills, and live tests`
- Base: `origin/agent/cc/pr-data-004-uzen-data-aware-synthesis-markdown`
- Ticket: `docs/superpowers/prs/PR-DATA-005-uzen-phase6-docs-live-tests-sync.md`
- Implementation report: `docs/superpowers/status/PR-DATA-005-implementation.md`

## Findings

### Blocking

1. `tests/test_live_endpoints.py:338` leaves `assert rows[0]["title"]` inside `test_live_event_summary()`, but `rows` is not defined in that test.

   The assertion appears to belong to `test_live_cninfo_reports()` and was displaced when adding the Phase 6 live tests. With `HOXIT_LIVE_TESTS=1`, `test_live_event_summary()` can fail with `NameError` after `signals.event_summary()` returns successfully. This directly affects the PR-DATA-005 acceptance criterion that optional live tests remain valid while skipped by default.

## Required Fix

- Move `assert rows[0]["title"]` back under `test_live_cninfo_reports()` after `assert len(rows) >= 1`.
- Remove the stray `rows` assertion from `test_live_event_summary()`.
- Re-run the required verification commands.

## Verification

Commands run locally:

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/hoxit uzen --help
git diff --check -- docs hoxit tests uzen-skills
```

Results:

- `tests/test_uzen.py tests/test_cli.py -v`: 170 passed.
- `hoxit uzen --help`: passed.
- `git diff --check`: passed.

## Notes

- File scope is otherwise aligned with the ticket: docs, `uzen-skills`, optional live tests, status report, and board only.
- No production runtime behavior change was observed.
- The review remains blocked until the live test assertion placement is corrected.
