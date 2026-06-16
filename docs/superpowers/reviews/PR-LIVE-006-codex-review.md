# PR-LIVE-006 Codex Review

Verdict: CHANGES_REQUESTED

## Scope Review

Updated review basis: the user explicitly approved widening this PR beyond the original
foundation-only ticket because the final report is not useful when key finance/bank
fields are missing. This review therefore no longer rejects the PR for including
Eastmoney F10 Playwright fallback or for wiring it into UZEN. The gate is now whether
the generation logic is correct, controlled, and auditable.

## Findings

1. Web fallback-filled fields lose their true source in field quality records.

   In `hoxit/uzen.py`, after `scrape_eastmoney_bank_metrics()` or
   `scrape_eastmoney_finance_overview()` fills `sources["finance"]`, the code calls
   `_finance_field_quality(...)`. That helper can distinguish only `provider.finance`
   from `f10`, so fields filled by `web_fallback.eastmoney_f10` are reported as
   `source=f10`.

   Reproduction with monkeypatched fallback:

   - `sources.finance.roe = 3.6`
   - `data_quality.sources.finance.roe.source = f10`

   Expected: source should preserve `web_fallback.eastmoney_f10` or an equivalent
   explicit fallback source. This matters because the report must be able to separate
   normal hoxit provider data, ordinary F10 data, and browser fallback data.

2. Failed fallback results are not surfaced in `data_quality.warnings`.

   `collect_snapshot()` records exceptions from the fallback call, but if the scraper
   returns `WebFetchResult(quality="failed", errors=[...])`, the errors are silently
   ignored. The original missing-field warnings remain, but the user cannot tell that
   browser fallback was attempted and failed, nor why it failed.

   Expected: failed or partial fallback should add concise warnings such as
   `Playwright fallback failed for finance overview: ...`.

3. Bank fallback success warning can overstate actual filled fields.

   The bank path appends a message based on all available fields in `web_result`, not
   the fields actually inserted into `sources["finance"]`. If a field is already
   present, the warning can claim it was filled by Playwright when it was not.

   Expected: count only fields actually inserted, and preferably include the field
   names.

4. Number parsing is too narrow for live web text.

   `_parse_cn_number()` handles plain numbers and Chinese units, but not common web
   formats such as `0.76%`, `1,234.56`, or values with surrounding spaces/units. Since
   the extraction target is rendered page text, this parser should accept `%` and
   comma-separated numbers at minimum.

5. Required implementation report is still missing at the expected path.

   The workflow expects `docs/superpowers/status/PR-LIVE-006-implementation.md`.
   The dated status note does not replace the standard implementation report.

## Verification Run

- `.venv/bin/python -m pytest tests/test_web_fallback.py tests/test_uzen.py -q` -> passed, 289 tests
- Prior full suite run on this branch: `.venv/bin/python -m pytest -v` -> passed, 402 tests, 30 skipped
- Prior CLI check: `.venv/bin/hoxit --help` -> passed

The requested changes are not because the current tests fail. They are because the
tests do not cover the fallback-to-report quality path tightly enough.

## Required Rework

Keep the widened scope, but fix the generation path:

- preserve `web_fallback.eastmoney_f10` in `data_quality.sources.finance.<field>.source`
- add regression tests for `collect_snapshot()` with monkeypatched web fallback
- surface `WebFetchResult.errors` when fallback returns `quality="failed"`
- count and report only actually inserted fallback fields
- broaden `_parse_cn_number()` for `%` and comma-separated values
- add the required implementation report at `docs/superpowers/status/PR-LIVE-006-implementation.md`

After those fixes, rerun targeted UZEN/web fallback tests and one Ningbo Bank live smoke
with `HOXIT_WEB_FALLBACK=1` if the local browser environment is available.
