# PR-DATA-002 Implementation Report

## Summary

Wired PR-DATA-001 hoxit interfaces (governance, business, event) into UZEN snapshot collection and data quality records.

## Changes

### `hoxit/uzen.py`

1. **Extended `UzenDataProvider`** with three new optional callables:
   - `governance: Callable[[str], dict]` — defaults to `_empty_mapping`
   - `business: Callable[[str], dict]` — defaults to `_empty_mapping`
   - `event: Callable[[str], dict]` — defaults to `_empty_mapping`

2. **Updated `default_provider()`** to wire:
   - `governance=fundamentals.governance_summary`
   - `business=fundamentals.business_summary`
   - `event=signals.event_summary`

3. **Updated `_MODE_SOURCES`**:
   - Added `"governance"`, `"business"`, `"event"` to `"analyze-stock"` mode
   - Other modes skip these sources (quick-scan, panel-only, scan-trap, lhb-analyzer, dcf, comps)

4. **Updated `collect_snapshot()`**:
   - Added `governance`, `business`, `event` to sources dict using `_map_or_skip()`
   - Quality records automatically created via `_map_or_skip()` (full/missing/error/skipped)

### `tests/test_uzen.py`

1. **Updated `provider()`** — added governance, business, event mock callables
2. **Updated `_recording_provider()`** — added recording wrappers for new callables
3. **Updated `test_analyze_stock_calls_full_coverage()`** — added new keys to expected set
4. **Updated `test_skipped_sources_use_neutral_defaults()`** — added assertions for new sources
5. **Updated `test_skipped_source_quality()`** — added assertions for new sources quality="skipped"
6. **Added 7 new tests**:
   - `test_governance_source_in_snapshot` — verifies governance data in snapshot
   - `test_business_source_in_snapshot` — verifies business data in snapshot
   - `test_event_source_in_snapshot` — verifies event data in snapshot
   - `test_governance_business_event_quality_full` — quality="full" when data present
   - `test_governance_business_event_skipped_in_quick_scan` — quality="skipped" in quick-scan
   - `test_governance_business_event_error_quality` — quality="error" when provider raises
   - `test_governance_business_event_missing_quality` — quality="missing" when empty

## Verification

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
# Result: 127 passed (7 new tests)

.venv/bin/hoxit uzen --help
# Result: Normal output, all modes listed

git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
# Result: No whitespace issues
```

## Acceptance Criteria

- [x] Snapshot JSON includes new source objects under stable keys
- [x] Existing provider tests can omit new callables or use neutral defaults
- [x] Mode profiles skip heavy sources where appropriate
- [x] `data_quality.sources` distinguishes `full`, `missing`, `error`, and `skipped`
- [x] Existing Phase 5 tests still pass (120 existing + 7 new = 127 total)

## Design Decisions

1. **Optional callables with `_empty_mapping` default**: Existing code that creates `UzenDataProvider` without the new fields will get empty dict responses, maintaining backward compatibility.

2. **Only `analyze-stock` mode collects new sources**: Governance, business, and event data are A-share specific and add API latency. Other modes (quick-scan, panel-only, etc.) skip them.

3. **Quality records via `_map_or_skip()`**: Reuses existing infrastructure for quality tracking. The `_map_or_skip()` helper automatically creates quality records with appropriate status.

4. **No synthesis or Markdown changes**: This PR only wires data collection. Synthesis and rendering will be updated in later PRs when the data is used for analysis.

## Status

Implementation complete. Ready for review.
