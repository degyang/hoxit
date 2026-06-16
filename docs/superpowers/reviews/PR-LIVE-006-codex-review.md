# PR-LIVE-006 Codex Review

Verdict: REJECTED

## Scope Review

PR-LIVE-006 was approved as a hoxit-level Playwright fallback foundation only:

- reusable browser fallback utility
- optional/disabled-by-default activation
- runtime availability detection
- explicit env var and timeout controls
- page fetch/snapshot primitive
- structured no-op/error/user-assistance model
- unit tests with fake drivers and no real browser
- documentation for login/Cookie/CAPTCHA constraints

The implementation goes substantially beyond that scope and changes production UZEN behavior.

## Blocking Findings

1. `hoxit/web_fallback.py` implements site-specific Eastmoney F10 parsers.

   The PR adds `scrape_eastmoney_bank_metrics()` and `scrape_eastmoney_finance_overview()` with Eastmoney URL construction and Chinese label parsing for fields such as `不良贷款率(%)`, `拨备覆盖率(%)`, `资本充足率(%)`, `ROE`, `EPS`, `净利率`, revenue, and net profit. The ticket explicitly excluded site-specific F10 parser work from PR-LIVE-006.

2. `hoxit/uzen.py` was modified to invoke browser fallback inside `collect_snapshot()`.

   `collect_snapshot()` now imports `scrape_eastmoney_bank_metrics()` and `scrape_eastmoney_finance_overview()` when `HOXIT_WEB_FALLBACK=1`, then fills finance and bank metrics into the snapshot. The ticket explicitly said this PR must not implement UZEN direct browser scraping and must not change `hoxit/uzen.py` except documentation references if absolutely necessary.

3. The PR changes live data semantics before the foundation contract is accepted.

   Enabling `HOXIT_WEB_FALLBACK=1` now changes UZEN report inputs for real stocks by attempting Eastmoney F10 extraction. That belongs in a later provider-specific PR after the fallback boundary, field-level quality model, failure modes, and source precedence are reviewed.

4. Required implementation report is missing at the expected path.

   The ticket requires `docs/superpowers/status/PR-LIVE-006-implementation.md`. This file is not present. The added dated status note does not satisfy the agreed implementation-report contract.

5. Documentation overclaims the current PR.

   `docs/API_DEVLOG.md` and `docs/INTERFACES.md` describe concrete Eastmoney F10 autofill behavior from `collect_snapshot()`. For PR-LIVE-006, docs should describe only the generic fallback foundation, default-off behavior, user-assistance requirements, and future provider-specific extension point.

## Verification Run

- `.venv/bin/python -m pytest tests/test_web_fallback.py -v` -> passed, 43 tests
- `.venv/bin/python -m pytest -v` -> passed, 402 tests, 30 skipped
- `.venv/bin/hoxit --help` -> passed
- `git diff --check -- hoxit tests docs pyproject.toml` -> passed

The rejection is not due to test failure. It is due to scope and architecture violations.

## Required Rework

Redo PR-LIVE-006 as a foundation-only PR from the approved PR-LIVE-005 base, or strip the current branch back to that boundary.

Allowed in PR-LIVE-006:

- generic `hoxit/web_fallback.py` utility primitives
- no-op provider creation when disabled
- explicit `HOXIT_WEB_FALLBACK=1` gate
- timeout/runtime availability controls
- structured result/error/user-assistance objects
- fake-driver unit tests
- docs explaining default-off behavior and login/CAPTCHA/Cookie limitations
- correct implementation report at `docs/superpowers/status/PR-LIVE-006-implementation.md`

Not allowed in PR-LIVE-006:

- `scrape_eastmoney_*` functions
- Eastmoney F10 page-specific parsing
- changes to `collect_snapshot()` that fetch or fill live fields
- UZEN production fallback integration
- claims that missing bank/finance fields are now solved
- any akshare dependency

After that foundation PR is approved, a separate PR can introduce the first provider-specific fallback for Eastmoney F10 with an explicit field mapping, quality records, failure semantics, and live verification target such as Ningbo Bank.
