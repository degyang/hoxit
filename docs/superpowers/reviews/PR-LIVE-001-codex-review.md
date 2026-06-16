# PR-LIVE-001 Codex Final Review

## Verdict

APPROVED

## Scope Reviewed

- Branch: `agent/cc/pr-live-001-uzen-provider-normalization-boundary`
- Implementation commit: `965ae51 feat: add UZEN provider normalization boundary (PR-LIVE-001)`
- Base: `main` at `887bbdd docs: add hoxit playwright fallback ticket`
- Ticket: `docs/superpowers/prs/PR-LIVE-001-uzen-provider-normalization-boundary.md`
- Implementation report: `docs/superpowers/status/PR-LIVE-001-implementation.md`

## Findings

No blocking findings.

The implementation stays within PR-LIVE-001 scope:

- Adds a UZEN boundary normalization pass in `collect_snapshot()`.
- Normalizes finance DataFrame-like objects enough to avoid pandas truthiness failures.
- Normalizes concept dict output into list form.
- Normalizes dragon-tiger dict `records` output into list form.
- Adds focused unit and integration-style tests for the new provider shapes.
- Does not add provider calls, Playwright, akshare fallback, UZEN scraping, CLI changes, or provider module changes.

## Residual Risk

`_normalize_finance()` currently calls `.to_dict()` without forcing a pandas orientation. Real pandas `DataFrame.to_dict()` defaults to `{column -> {index -> value}}`, so this PR stabilizes type/shape at the boundary but does not guarantee semantic finance fields such as `roe` or `net_profit` are flat and report-ready.

This is acceptable for PR-LIVE-001 because PR-LIVE-003 is explicitly scoped for finance field normalization and source quality. PR-LIVE-003 must not treat this as solved.

Reference checked: pandas documents the default `DataFrame.to_dict()` orientation as `{column -> {index -> value}}`.

## Verification

Commands run locally:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md
.venv/bin/python -m pytest
```

Results:

- `tests/test_uzen.py -v`: 178 passed.
- `hoxit uzen --help`: passed.
- `git diff --check`: passed.
- Full test suite: 291 passed, 29 skipped.

## Notes

- The public UZEN report path remains stable for the tested shapes.
- Concept and dragon-tiger normalization intentionally shifts downstream rendering to canonical list forms.
- `tos/` remains an untracked local report output and is not part of this PR.
