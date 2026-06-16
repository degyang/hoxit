# PR-LIVE-004: Bank Report Quality For Ningbo Bank

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-004-bank-report-quality-ningbo`

## Goal

Improve UZEN report quality for bank stocks, using Ningbo Bank `002142` as the first acceptance target, without forcing ordinary industrial DCF assumptions onto banks.

## Scope

- Add deterministic bank-aware report logic in UZEN.
- Detect bank industry from hoxit fundamentals/concept/industry fields where available.
- For bank stocks, emphasize:
  - PE TTM
  - PB
  - ROE
  - dividend yield if available
  - NIM / NPL / provision coverage / capital adequacy if available
- If bank-specific fields are unavailable, surface clear `data_needed` messages.
- Evaluate data source quality for bank-specific fields. If existing hoxit sources are not sufficient, document fallback candidates and add reusable hoxit helper only when it is small, tested, and within scope.
- For bank-specific metrics that may require web pages such as F10 or annual-report pages, document whether Playwright/Web fallback is needed and what user assistance is required.
- DCF section for bank stocks should clearly state ordinary FCFF DCF is not the primary model when required inputs are absent.
- Do not invent values.

## Out of Scope

- No full bank valuation model yet.
- No scraping bank annual reports directly in UZEN.
- No UZEN-internal one-off data collection.
- No akshare fallback.
- No browser automation that requires login/Cookie/user interaction without explicit separate approval.
- No visual output.
- No investment advice wording.

## Files Likely To Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/API_DEVLOG.md`

## Must Not Change

- Provider modules unless adding a reusable hoxit bank metric helper is explicitly needed and tested.
- `hoxit/cli.py`
- `uzen-skills/` docs, deferred to PR-LIVE-005.

## Acceptance Criteria

- UZEN can identify a bank-like stock from available hoxit fields.
- Bank report section or finance section highlights bank-relevant metrics.
- Missing bank metrics are explicit and not silent.
- Data source quality for bank metrics is visible in JSON or input_quality.
- If bank metrics require Web/Playwright fallback, implementation report identifies exact fields, target pages, and user-assistance needs.
- DCF wording for banks avoids overclaiming ordinary FCFF applicability.
- Ningbo Bank report quality target is documented in implementation report.

## Required Tests

- Bank stock fixture with PE/PB/ROE available.
- Bank stock fixture missing bank-specific metrics, showing data_needed.
- Non-bank stock fixture remains unchanged.
- DCF bank wording test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md
```

## Dependencies

Depends on PR-LIVE-003 approved or merged.

## Definition Of Done

- Tests pass.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-004-implementation.md`.
- Board marks PR-LIVE-004 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. UZEN returns to generic stock report behavior.
