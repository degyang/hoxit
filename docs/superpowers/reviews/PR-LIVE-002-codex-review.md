# PR-LIVE-002 Codex Final Review

## Verdict

CHANGES_REQUESTED

## Findings

1. `hoxit/uzen.py:467` computes `avg_price` as the arithmetic average of all available bar close prices. In A-share market data, `avg_price` is normally understood as成交均价 / transaction average price, which should come from成交额 and成交量 when those inputs are available. Filling `summary.avg_price` with a historical close average gives a misleading field with a correct-looking number. Given Phase 7 is specifically about live data contract hardening and avoiding silent bad indicators, this must be fixed before approval.

## Required Changes

- Do not populate `summary.avg_price` from `_bars_avg_price(closes)`.
- Either:
  - derive `avg_price` from quote amount and volume/vol with an explicit, tested A-share unit rule; or
  - leave `avg_price` as `None` with a warning/data-needed entry when成交额/成交量 inputs are unavailable, and use a separately named field such as `avg_close` if the historical close average is still useful.
- Update tests so `avg_price` verifies成交额/成交量 semantics, not close-price averaging.
- Keep the PR scoped to PR-LIVE-002; no CLI, Playwright, akshare, or later-ticket work.

## Verified

- `.venv/bin/python -m pytest tests/test_uzen.py -v` passed: 187 passed.
- `.venv/bin/hoxit uzen --help` passed.
- `git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md` passed.
- `.venv/bin/python -m pytest` passed: 300 passed, 29 skipped.

## Notes

- The branch is now correctly based on `origin/agent/cc/pr-live-001-uzen-provider-normalization-boundary`; the earlier base-branch issue is resolved.
- `tos/` remains an untracked local output directory and was not reviewed as part of this PR.
