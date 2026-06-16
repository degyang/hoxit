# PR-LIVE-003 Codex Final Review

## Verdict

CHANGES_REQUESTED

## Findings

1. `hoxit/uzen.py:612` still calls DataFrame-like `.to_dict()` without an orientation. Real pandas defaults to a nested shape such as `{"净资产收益率": {0: 12.0}}`, so `_normalize_finance()` currently returns `{"roe": {0: 12.0}}` instead of `{"roe": 12.0}`. That means `_first_number()`, DCF input quality, investor signals, and Markdown still cannot consume real pandas finance output. This is a core PR-LIVE-003 acceptance item because the ticket explicitly requires DataFrame-like finance with aliases.

2. `hoxit/uzen.py:341` converts `_finance_field_quality()` records into `_quality_record()` but drops the field-level `status` (`available` / `missing` / `unsupported`) required by the PR ticket. It maps `available` to `quality="full"` and everything else to `quality="missing"`, so consumers cannot distinguish `missing` from `unsupported`. The source is also always `provider.finance`, even when a value was filled from F10, so the final record does not reliably show the source used.

## Required Changes

- Normalize real pandas/DataFrame-like finance outputs into scalar canonical fields. Prefer `.to_dict("records")` when supported, or otherwise flatten single-row `{column: {index: value}}` dicts before alias mapping.
- Add tests that simulate pandas default `.to_dict()` nested output and verify scalar canonical fields, DCF inputs, and Markdown/investor reads work from that shape.
- Preserve field-level `status` in final `data_quality.sources["finance.<field>"]` records, or otherwise expose an equivalent explicit status field without losing `unsupported` versus `missing`.
- Track whether a finance field came from direct finance data or F10 enrichment, and write that source into the field-level quality record.
- Keep the fix scoped to PR-LIVE-003; no Playwright, akshare, CLI changes, or PR-LIVE-004 work.

## Verified

- `.venv/bin/python -m pytest tests/test_uzen.py tests/test_fundamentals.py -v` passed: 219 passed.
- `.venv/bin/hoxit uzen --help` passed.
- `git diff --check -- hoxit tests docs/API_DEVLOG.md` passed.
- `.venv/bin/python -m pytest` passed: 321 passed, 29 skipped.

## Notes

- The branch is correctly based on `origin/agent/cc/pr-live-002-uzen-derived-market-metrics`.
- `tos/` remains an untracked local output directory and was not reviewed as part of this PR.
