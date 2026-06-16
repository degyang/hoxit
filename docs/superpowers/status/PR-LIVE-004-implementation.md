# PR-LIVE-004 Implementation Report

## Summary

Added bank stock detection and bank-aware report quality for UZEN, using Ningbo Bank (002142) as acceptance target. Bank stocks now get specialized metrics, DCF caveats, and explicit missing-field warnings.

## What Changed

### `hoxit/uzen.py`

1. **Bank-specific finance aliases** added to `_FINANCE_ALIASES`:
   - `净息差` / `net_interest_margin` → `nim`
   - `不良贷款率` / `npl` / `不良率` → `npl_ratio`
   - `拨备覆盖率` / `provision_coverage_ratio` → `provision_coverage`
   - `资本充足率` / `capital_adequacy_ratio` / `car` → `capital_adequacy`

2. **`_FINANCE_TRACKED_FIELDS`** expanded with bank-specific fields:
   - `nim`, `npl_ratio`, `provision_coverage`, `capital_adequacy`

3. **`_BANK_INDUSTRY_KEYWORDS`** constant:
   - `("银行", "bank", "商业银行", "城市银行", "农村银行")`

4. **`_is_bank_stock(snapshot)`** — new helper:
   - Checks `fundamentals.industry` against bank keywords
   - Checks `signals.concept` tags against bank keywords

5. **`_bank_metrics_summary(snapshot)`** — new helper:
   - Extracts nim/npl_ratio/provision_coverage/capital_adequacy from finance
   - Returns `is_bank`, `metrics`, `data_needed` (list of missing field labels)

6. **`_dcf_analysis()`** updated:
   - Detects bank stocks via `_is_bank_stock()`
   - Adds warning: "银行股 FCFF DCF 不适用：银行现金流受资本充足率等监管约束，净利润折现仅作参考"
   - Internal variable renamed from `metrics` to `metrics_data` to avoid shadowing

7. **`analyze_snapshot()`** updated:
   - Adds `bank_metrics` to analysis dict (from `_bank_metrics_summary()`)

8. **`render_markdown()`** updated:
   - When `bank_metrics.is_bank`, renders "### 银行专项指标" section with NIM/NPL/provision coverage/capital adequacy
   - Shows missing fields explicitly: "缺失字段：净息差 (NIM)、..."

### `tests/test_uzen.py`

15 new tests added (244 total):
- `test_is_bank_stock_detected_by_industry` — industry="银行" detection
- `test_is_bank_stock_detected_by_concept` — concept tag detection
- `test_is_not_bank_stock` — non-bank not detected
- `test_bank_metrics_summary_with_data` — all 4 metrics present
- `test_bank_metrics_summary_missing_fields` — data_needed list
- `test_bank_metrics_not_bank_stock` — non-bank returns is_bank=False
- `test_bank_dcf_warning` — FCFF caveat in DCF warnings
- `test_bank_metrics_in_analysis` — bank_metrics in analysis dict
- `test_bank_metrics_not_in_analysis_for_non_bank` — non-bank is_bank=False
- `test_bank_specific_aliases_normalized` — Chinese bank field names → canonical
- `test_bank_metrics_in_markdown` — bank section in Markdown
- `test_bank_metrics_missing_fields_in_markdown` — "缺失" in Markdown
- `test_non_bank_no_bank_section_in_markdown` — no bank section for non-bank
- `test_bank_field_quality_tracks_bank_fields` — nim/npl tracked in field quality
- `test_ningbo_bank_fixture_quality` — full 002142 fixture acceptance test

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py -v            → 244 passed
.venv/bin/python -m pytest                                   → 357 passed, 29 skipped
.venv/bin/hoxit uzen --help                                  → Normal output
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md → No whitespace issues
```

## Bank Data Source Quality Assessment

| Metric | Source | Status |
|--------|--------|--------|
| ROE | provider.finance | available (if returned) |
| Net profit | provider.finance | available (if returned) |
| NIM | provider.finance | depends on provider |
| NPL ratio | provider.finance | depends on provider |
| Provision coverage | provider.finance | depends on provider |
| Capital adequacy | provider.finance | depends on provider |
| PE TTM | provider.metrics | available |
| PB | provider.metrics | available |
| Dividend yield | — | not currently tracked |

### Fallback Candidates (not implemented in this PR)

- **NIM/NPL/Provision/Capital adequacy**: These require F10 sections or annual report pages. If `provider.finance` does not return them, a Playwright/web fallback targeting east money F10 pages may be needed. User assistance would be required for cookie/auth setup.
- **Dividend yield**: Could be computed from `dividend` provider data if available. Deferred to future PR.

## Base Branch

Built on top of `agent/cc/pr-live-003-hoxit-uzen-finance-field-normalization` (PR-LIVE-003 latest).

## Status

Ready for Codex review.
