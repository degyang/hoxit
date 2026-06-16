# PR-LIVE-003 Implementation Report

## Summary

Normalized hoxit finance outputs into stable UZEN financial fields with alias mapping, pandas nested-dict flattening, F10 merge, and field-level source quality tracking with status/source attribution preserved in snapshot.

## What Changed

### `hoxit/uzen.py`

1. **`_to_scalar(value)`** — new helper:
   - Extracts scalar from nested pandas-like structures:
     - `{0: 12.0}` → `12.0` (single-row DataFrame `.to_dict()`)
     - `{"2024Q1": 8.5, "2024Q2": 9.0}` → `8.5` (period-indexed)
     - `[42.0]` → `42.0` (single-element list)
   - Recursively unwraps nested dicts/lists.
   - Handles numpy-like objects via `float()` conversion.

2. **`_normalize_finance(result)`** enhanced:
   - After DataFrame→dict and alias normalization, applies `_to_scalar()` to each value.
   - Ensures downstream consumers always get `int | float | str | None`, never nested containers.

3. **`_FINANCE_ALIASES`** constant:
   - Maps 8 groups of Chinese/English/variant aliases to canonical names.

4. **`_normalize_f10(f10, finance)`**:
   - Extracts finance fields from F10 sections, preserving existing values.
   - Calls `_normalize_finance()` on sections, so `_to_scalar()` applies automatically.

5. **`_finance_field_quality(finance, f10, original_finance)`** updated:
   - `original_finance` parameter: pre-F10-merge finance dict for source attribution.
   - Status values: `"available"`, `"missing"`, `"unsupported"`.
   - Source: `"provider.finance"` or `"f10"`.

6. **`collect_snapshot()`** updated:
   - Captures `original_finance` before F10 merge.
   - Passes `original_finance` to `_finance_field_quality()`.
   - Writes `status` field (available/missing/unsupported) into each `finance.<field>` quality record alongside `quality` (full/missing).

### `tests/test_uzen.py`

229 total tests. PR-LIVE-003 additions:
- **_to_scalar** (8): passthrough, single-element dict, multi-element dict, empty dict, list, empty list, nested, numpy-like
- **Nested pandas finance** (4): single-row DataFrame, period-indexed, mixed, collect_snapshot
- **Downstream consumption** (3): DCF, quality investor, Markdown
- **Source tracking** (4): source=provider.finance, source=f10, no-original default, snapshot source
- **Snapshot-level status** (3 new):
  - `test_finance_field_status_available_in_snapshot` — field present → status=available, quality=full
  - `test_finance_field_status_missing_in_snapshot` — field absent + F10 available → status=missing
  - `test_finance_field_status_unsupported_in_snapshot` — field absent + F10 unsupported → status=unsupported
- **Existing snapshot test** updated to assert `status` field

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py tests/test_fundamentals.py -v  → 240 passed
.venv/bin/python -m pytest                                                    → 342 passed, 29 skipped
.venv/bin/hoxit uzen --help                                                   → Normal output
git diff --check -- hoxit tests docs/API_DEVLOG.md                            → No whitespace issues
```

## Base Branch

Built on top of `agent/cc/pr-live-002-uzen-derived-market-metrics` (PR-LIVE-002 latest).

## Status

Ready for Codex review.
