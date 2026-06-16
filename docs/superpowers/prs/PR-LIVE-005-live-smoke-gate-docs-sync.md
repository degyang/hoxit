# PR-LIVE-005: Live Smoke Gate And Docs Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-005-live-smoke-gate-docs-sync`

## Goal

Add optional live smoke coverage and documentation so future UZEN work cannot pass review solely on mock provider tests when real hoxit provider output breaks report generation.

## Scope

- Add optional live smoke test(s), skipped by default.
- Fixed target: Ningbo Bank `002142`.
- Smoke test should generate `analyze-stock` JSON/Markdown into a temporary directory.
- Assert:
  - JSON and Markdown files exist.
  - `analysis.summary.change_pct` is not missing.
  - Markdown contains core report sections.
  - report review status is present.
  - no raw dict/list repr in key sections.
- Update docs:
  - `docs/INTERFACES.md`
  - `uzen-skills/README.md`
  - relevant `uzen-skills/commands/*.md` if needed.
  - `docs/API_DEVLOG.md`
- Document Phase 7 live contract policy.
- Document source quality evaluation and fallback policy:
  - hoxit-first
  - field-level fallback
  - no UZEN one-off scraper
  - quality reason required when data remains missing
  - no akshare fallback in Phase 7
  - controlled Web/Playwright fallback policy and user-assistance requirements

## Out of Scope

- No production behavior changes except test/docs helper code.
- No HTML/PNG/Playwright.
- No new providers.
- No claim that all live data gaps are solved.

## Files Likely To Change

- `tests/test_live_endpoints.py` or a new live test file.
- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `docs/API_DEVLOG.md`
- `docs/superpowers/status/PR-LIVE-005-implementation.md`

## Must Not Change

- `hoxit/uzen.py` except for tiny smoke-test support if absolutely necessary and approved by previous PRs.
- provider modules.
- Earlier PR tickets.

## Acceptance Criteria

- Live smoke is skipped by default.
- Live smoke can be enabled with an explicit environment variable.
- Docs explain hoxit-first provider contract and UZEN normalization boundary.
- Docs explain how to treat unqualified data sources and when to add reusable hoxit fallback helpers.
- Docs explain when Playwright/Web may be introduced and how to request user help.
- Docs do not claim full UZI parity or visual output.
- Ningbo Bank is documented as the Phase 7 smoke target.

## Required Tests

- Default test suite remains offline.
- Optional live smoke test is marked integration/slow/skip by default.
- If live smoke cannot run due to missing credentials/network, implementation report must say so explicitly.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/python -m pytest tests/test_live_endpoints.py -v
.venv/bin/hoxit uzen --help
git diff --check -- docs hoxit tests uzen-skills
```

Optional live command when credentials/network are available:

```bash
set -a; source .env.local; set +a; HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -k uzen -v
```

## Dependencies

Depends on PR-LIVE-004 approved or merged.

## Definition Of Done

- Tests pass.
- Docs synchronized.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-005-implementation.md`.
- Board marks PR-LIVE-005 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. Phase 7 implementation remains, but live smoke/docs gate is removed.
