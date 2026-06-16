# PR-LIVE-006: hoxit Playwright Fallback Provider Foundation

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-006-hoxit-playwright-fallback-foundation`

## Goal

Add a controlled hoxit-level Playwright fallback foundation for cases where existing HTTP/API providers cannot supply required A-share fields, especially future snapshot/report needs.

## Scope

- Design and implement a small hoxit reusable browser fallback utility.
- Keep Playwright optional and disabled by default.
- Provide a stable API boundary that future hoxit provider helpers can use.
- Include:
  - runtime availability detection
  - explicit opt-in environment variable
  - timeout handling
  - page fetch / snapshot capture primitive
  - structured error result instead of uncaught browser failures
  - no-op behavior when Playwright is unavailable or disabled
- Add unit tests that do not launch a real browser.
- Add optional live/browser smoke test only if it can be skipped by default.
- Document user-assistance requirements for login/Cookie/验证码/profile-dependent pages.

## Out of Scope

- No UZEN direct browser scraping.
- No default browser launch in normal hoxit or test runs.
- No akshare fallback.
- No authenticated scraping implementation unless explicitly approved in a later ticket.
- No site-specific F10 parser in this PR.
- No visual report output.

## Files Likely To Change

- New hoxit helper module, for example `hoxit/browser_fallback.py`.
- `tests/test_*` for browser fallback utility.
- `docs/INTERFACES.md`.
- `docs/API_DEVLOG.md`.
- Possibly `pyproject.toml` only if optional dependency metadata is needed.

## Must Not Change

- `hoxit/uzen.py` except documentation references if absolutely necessary.
- Existing provider modules except to import no-op capability checks if needed.
- `uzen-skills/` unless docs sync is explicitly needed.
- Earlier Phase 7 PR behavior.

## Acceptance Criteria

- Normal unit test suite does not require Playwright installed.
- Browser fallback is disabled by default.
- When disabled/unavailable, helper returns structured `unsupported`/`disabled` result.
- When enabled but failing, helper returns structured error with timeout/reason.
- API shape is reusable by future hoxit providers.
- Docs explain how and when user assistance is required.

## Required Tests

- Disabled-by-default behavior.
- Missing Playwright dependency behavior.
- Timeout/error result behavior using mocks.
- Successful mocked page/snapshot result.
- No real browser launch in default tests.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_browser_fallback.py -v
.venv/bin/python -m pytest -v
.venv/bin/hoxit --help
git diff --check -- hoxit tests docs pyproject.toml
```

Optional browser smoke when Playwright is installed and explicitly enabled:

```bash
HOXIT_BROWSER_FALLBACK=1 HOXIT_BROWSER_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_browser_fallback_live.py -v
```

## Dependencies

Depends on PR-LIVE-005 approved or merged.

## Definition Of Done

- Tests pass without Playwright installed.
- Optional browser behavior is documented and skipped by default.
- `docs/API_DEVLOG.md` records the new fallback foundation and its constraints.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-006-implementation.md`.
- Board marks PR-LIVE-006 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. hoxit returns to HTTP/API-only fallback behavior.
