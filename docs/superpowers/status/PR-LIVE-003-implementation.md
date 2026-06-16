# PR-LIVE-003 Implementation Report

## Summary

Normalized hoxit finance outputs into stable UZEN financial fields with alias mapping, F10 merge, and field-level source quality tracking.

## What Changed

### `hoxit/uzen.py`

1. **`_normalize_finance(result)`** enhanced (was DataFrame→dict only):
   - After DataFrame conversion, applies `_FINANCE_ALIASES` to map Chinese/English/variant field names to canonical names.
   - First-wins: canonical field takes precedence over alias when both present.
   - Always copies dict to avoid mutating provider data.

2. **`_FINANCE_ALIASES`** constant:
   - Maps 8 groups of aliases to canonical names:
     - `ROE` / `净资产收益率` / `roe_ttm` → `roe`
     - `净利润` / `net_profit_ttm` / `归母净利润` / `归属于母公司所有者的净利润` → `net_profit`
     - `营业收入` / `revenue_ttm` / `营业总收入` → `revenue`
     - `毛利率` / `gross_profit_margin` / `销售毛利率` → `gross_margin`
     - `净利率` / `net_profit_margin` / `销售净利率` → `net_margin`
     - `总资产` / `assets` → `total_assets`
     - `净资产` / `股东权益` / `equity` → `total_equity`
     - `股本` / `总股本` / `shares` / `share_count` → `total_shares`

3. **`_normalize_f10(f10, finance)`** — new helper:
   - Extracts finance fields from F10 sections (`financial_summary`, `financial_highlights`, `main_financial`, `financial_indicator`, `basic_financial`).
   - Merges into finance dict without overwriting existing values.
   - Skips when F10 is unsupported or has no sections.

4. **`_finance_field_quality(finance, f10)`** — new helper:
   - Evaluates each tracked field (`roe`, `net_profit`, `revenue`, `gross_margin`, `net_margin`, `total_assets`, `total_equity`, `total_shares`).
   - Returns status: `available` (present), `missing` (F10 available but field absent), `unsupported` (F10 unavailable).
   - Includes specific warning messages.

5. **`collect_snapshot()`** updated:
   - After normalizing finance, merges F10 data via `_normalize_f10()`.
   - Adds `finance.{field}` quality records to `data_quality.sources` (only when finance was fetched, not skipped).

6. **Investor/DCF cleanup**:
   - `_value_investor()`: removed `finance.get("ROE")` fallback — `roe` is now always canonical.
   - `_quality_investor()`: same cleanup.
   - `render_markdown()`: removed `finance.get("ROE")` fallback.
   - DCF reads normalized `net_profit` and `total_shares` (no change needed — already canonical).

### `tests/test_uzen.py`

17 new tests added (208 total):
- `test_normalize_finance_chinese_aliases` — Chinese field names → canonical
- `test_normalize_finance_variant_aliases` — ROE/roe_ttm/归母净利润 → canonical
- `test_normalize_finance_first_wins` — canonical takes precedence
- `test_normalize_finance_dataframe_with_aliases` — DataFrame with Chinese fields
- `test_normalize_finance_preserves_extra_fields` — unknown fields pass through
- `test_normalize_finance_empty_returns_empty` — empty/None → empty dict
- `test_normalize_f10_merges_into_finance` — F10 enriches finance
- `test_normalize_f10_does_not_overwrite_finance` — F10 preserves existing
- `test_normalize_f10_unsupported_status_no_merge` — unsupported F10 skipped
- `test_normalize_f10_empty_returns_finance` — empty F10 no-op
- `test_finance_field_quality_available` — present fields → available
- `test_finance_field_quality_unsupported_f10` — missing + F10 unsupported → unsupported
- `test_finance_field_quality_f10_available_but_field_missing` — missing + F10 available → missing
- `test_finance_field_quality_in_snapshot` — field-level records in snapshot
- `test_finance_field_quality_skipped_in_quick_scan` — quick-scan skips finance field records
- `test_dcf_uses_normalized_finance_fields` — DCF reads Chinese-aliased fields
- `test_quality_investor_uses_normalized_roe` — quality investor reads Chinese ROE

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py tests/test_fundamentals.py -v  → 219 passed
.venv/bin/python -m pytest                                                    → 321 passed, 29 skipped
.venv/bin/hoxit uzen --help                                                   → Normal output
git diff --check -- hoxit tests docs/API_DEVLOG.md                            → No whitespace issues
```

## Base Branch

Built on top of `agent/cc/pr-live-002-uzen-derived-market-metrics` (PR-LIVE-002 latest).

## Status

Ready for Codex review.
