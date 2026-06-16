# PR-LIVE-003: hoxit/UZEN Finance Field Normalization And Source Quality

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-003-hoxit-uzen-finance-field-normalization`

## Goal

Normalize hoxit finance outputs into stable UZEN financial fields and add field-level source quality evaluation so ROE, net profit, revenue, margins, equity/assets, and share count are not silently missing when one hoxit source is incomplete or unstable.

## Scope

- Inspect current `fundamentals.finance_snapshot()` live/mock shapes.
- Add UZEN finance normalization helper or hoxit reusable helper if needed.
- Normalize common aliases for:
  - `roe`
  - `net_profit`
  - `revenue`
  - `gross_margin`
  - `net_margin`
  - `total_assets`
  - `total_equity`
  - `total_shares`
- Convert DataFrame-like finance outputs at the boundary.
- Update DCF input quality to consume normalized `net_profit` and `total_shares` where available.
- Add field-level source quality records for normalized finance fields:
  - source used
  - status: `available`, `derived`, `missing`, `unsupported`
  - warning/reason when missing
- Evaluate hoxit fallback candidates for missing finance fields. If a current source is not good enough, either:
  - document why fallback is not yet available, or
  - add a reusable hoxit helper with tests.
- Do not use akshare as a Phase 7 fallback candidate.
- If a Web/Playwright fallback appears necessary, do not implement it in this PR unless it is explicitly small and does not require user login/cookies. Otherwise document:
  - target fields
  - candidate pages
  - required user assistance
  - risk/stability assessment
- Keep pandas imports delayed or avoid pandas imports entirely.

## Out of Scope

- No full bank valuation model.
- No UZEN-internal one-off scraper.
- No new external data provider unless implemented as a reusable hoxit helper with tests and documented source quality.
- No akshare fallback.
- No authenticated Playwright/browser workflow without explicit user assistance and a separate ticket.
- No visual output.
- No broad rewrite of `fundamentals.py`.

## Files Likely To Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/API_DEVLOG.md`
- Possibly `hoxit/fundamentals.py` only if a reusable, tested helper is required.

## Must Not Change

- `hoxit/cli.py` unless exposing a new hoxit helper is explicitly required by this ticket.
- `uzen-skills/`
- PR-LIVE-004/005 tickets.

## Acceptance Criteria

- Finance dict and DataFrame-like inputs normalize to stable UZEN financial fields.
- Markdown basic financial section can show ROE/net profit when inputs exist under aliases.
- DCF input quality reads normalized fields.
- Missing finance fields list exact missing inputs.
- If a source returns unusable/empty data, field-level quality records explain it and fallback candidates are evaluated.

## Required Tests

- DataFrame-like finance with Chinese/English aliases.
- Dict finance with alternate field names.
- DCF input quality using normalized net profit/share count.
- Missing field warnings/input_quality.
- Source quality records for usable, missing, and fallback-not-available fields.
- If Playwright/Web is deferred, a clear follow-up section listing field/page/user-assistance requirements.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_fundamentals.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit tests docs/API_DEVLOG.md
```

## Dependencies

Depends on PR-LIVE-002 approved or merged.

## Definition Of Done

- Tests pass.
- Finance normalization behavior is documented in implementation report.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-003-implementation.md`.
- Board marks PR-LIVE-003 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. UZEN returns to existing finance field reads.
