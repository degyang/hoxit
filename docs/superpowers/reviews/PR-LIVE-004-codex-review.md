# PR-LIVE-004 Codex Final Review

## Verdict

CHANGES_REQUESTED

## Findings

1. `hoxit/uzen.py:762` expands `_FINANCE_TRACKED_FIELDS` with bank-specific fields globally, so non-bank stocks now get `finance.nim`, `finance.npl_ratio`, `finance.provision_coverage`, and `finance.capital_adequacy` records. A non-bank fixture now has those fields marked `status="unsupported"` / `quality="missing"` even though bank metrics are irrelevant. This violates the PR acceptance criterion that non-bank stock behavior remains unchanged and risks polluting data-quality diagnostics for ordinary industrial stocks.

## Required Changes

- Track bank-specific finance fields only when `_is_bank_stock(snapshot)` is true, or otherwise ensure non-bank snapshots do not emit bank-specific `finance.<field>` quality records/warnings.
- Add a regression test asserting a non-bank snapshot has no `finance.nim`, `finance.npl_ratio`, `finance.provision_coverage`, or `finance.capital_adequacy` records.
- Keep the bank stock path unchanged: bank snapshots should still expose bank metric availability/missing status and render the bank section.
- Keep the fix scoped to PR-LIVE-004; no provider rewrites, no akshare, no Playwright, no CLI changes.

## Verified

- `.venv/bin/python -m pytest tests/test_uzen.py -v` passed: 244 passed.
- `.venv/bin/hoxit uzen --help` passed.
- `git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md` passed.
- `.venv/bin/python -m pytest` passed: 357 passed, 29 skipped.

## Notes

- The branch is correctly based on `origin/agent/cc/pr-live-003-hoxit-uzen-finance-field-normalization`.
- PE TTM, PB, and ROE are already rendered through the existing market valuation and finance sections; the new bank section adds NIM/NPL/provision/capital adequacy and explicit missing fields.
- `tos/` remains an untracked local output directory and was not reviewed as part of this PR.
