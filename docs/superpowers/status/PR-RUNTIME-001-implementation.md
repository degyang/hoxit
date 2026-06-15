---
title: "PR-RUNTIME-001 Implementation Report"
pr: "PR-RUNTIME-001"
scope: "uzen mode execution profiles"
status: "IMPLEMENTED"
date: "2026-06-15"
---

# PR-RUNTIME-001: UZEN Mode Execution Profiles

## Summary

Implemented mode-specific source selection in `hoxit.uzen.collect_snapshot()` so that each UZEN command only calls the data providers it actually needs, instead of always running the full call graph.

## Deliverables

### 1. `hoxit/uzen.py`

**Added `_MODE_SOURCES` dict** (lines 76–107): maps each mode name to the set of source keys it requires.

| Mode | Sources |
|------|---------|
| `analyze-stock` | All 20 sources (full coverage) |
| `quick-scan` | quote, metrics, valuation, fundamentals, concept, fund_flow |
| `panel-only` | quote, metrics, valuation, fundamentals, finance |
| `scan-trap` | quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger |
| `lhb-analyzer` | quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup |
| `dcf` | quote, metrics, valuation, fundamentals, finance |
| `comps` | quote, metrics, fundamentals, industry |

**Added `_sources_for_mode()`**: returns the source set for a mode, falling back to `analyze-stock` for unknown modes.

**Refactored `collect_snapshot()`**: introduced `_map_or_skip()` and `_list_or_skip()` helpers that check `needed` before calling a provider. Skipped sources are set to neutral defaults (`{}` for mapping, `[]` for list).

### 2. `tests/test_uzen.py`

Added 8 new tests using a call-recording fake provider:

| Test | Validates |
|------|-----------|
| `test_quick_scan_skips_heavy_providers` | quick-scan calls only 6 expected providers |
| `test_analyze_stock_calls_full_coverage` | analyze-stock calls all 20 providers |
| `test_panel_only_calls_expected_subset` | panel-only calls 5 expected providers |
| `test_scan_trap_calls_expected_subset` | scan-trap calls 8 expected providers |
| `test_lhb_analyzer_calls_expected_subset` | lhb-analyzer calls 7 expected providers |
| `test_dcf_calls_expected_subset` | dcf calls 5 expected providers |
| `test_comps_calls_expected_subset` | comps calls 4 expected providers |
| `test_skipped_sources_use_neutral_defaults` | Skipped sources present with `{}` or `[]` defaults |

### 3. `docs/superpowers/status/PR-RUNTIME-001-implementation.md`

This report.

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
17 passed in 0.19s

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py
(no output)
```

## Acceptance Criteria Checklist

- [x] `quick-scan` no longer calls heavy providers such as reports and filings.
- [x] `analyze-stock` retains the full current provider coverage.
- [x] Focused modes call only their required provider groups.
- [x] Existing JSON source keys remain present (skipped sources get neutral defaults).
- [x] Existing CLI behavior and artifact paths remain compatible.
- [x] Unknown mode falls back to `analyze-stock` behavior.

## Design Notes

- **No new external APIs added**. Mode profiles select among existing `UzenDataProvider` fields only.
- **`UzenDataProvider` unchanged**. The dataclass signature is untouched; only the call-scheduling logic in `collect_snapshot()` changed.
- **Sentinel list reuse**. A module-level `_SENTINEL_LIST` is returned for all skipped list-like sources, avoiding unnecessary allocations.
- **`_map_or_skip` / `_list_or_skip`**. These thin wrappers centralize the skip-or-call decision and keep `collect_snapshot()` readable.
