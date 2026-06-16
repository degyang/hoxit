# PR-LIVE-003 Implementation Report

## Summary

Normalized hoxit finance outputs into stable UZEN financial fields with alias mapping, pandas nested-dict flattening, F10 merge, and field-level source quality tracking with source attribution.

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

3. **`_FINANCE_ALIASES`** constant (unchanged):
   - Maps 8 groups of Chinese/English/variant aliases to canonical names.

4. **`_normalize_f10(f10, finance)`** (unchanged):
   - Extracts finance fields from F10 sections, preserving existing values.
   - Calls `_normalize_finance()` on sections, so `_to_scalar()` applies automatically.

5. **`_finance_field_quality(finance, f10, original_finance)`** updated:
   - New `original_finance` parameter: pre-F10-merge finance dict.
   - When field present in `original_finance` → source = `"provider.finance"`.
   - When field only in merged `finance` (from F10) → source = `"f10"`.
   - Status values: `"available"`, `"missing"`, `"unsupported"`.

6. **`collect_snapshot()`** updated:
   - Captures `original_finance` before F10 merge.
   - Passes `original_finance` to `_finance_field_quality()` for source attribution.

### `tests/test_uzen.py`

18 new tests added (226 total):
- **_to_scalar tests** (8): passthrough, single-element dict, multi-element dict, empty dict, single-element list, empty list, nested dict-in-dict, numpy-like
- **Nested pandas finance tests** (4): single-row DataFrame, period-indexed, mixed scalar/nested, flatten in collect_snapshot
- **Downstream consumption tests** (3): DCF reads flattened, quality investor reads flattened ROE, Markdown renders flattened
- **Source tracking tests** (3): source=provider.finance, source=f10, snapshot-level source attribution

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py tests/test_fundamentals.py -v  → 237 passed
.venv/bin/python -m pytest                                                    → 339 passed, 29 skipped
.venv/bin/hoxit uzen --help                                                   → Normal output
git diff --check -- hoxit tests docs/API_DEVLOG.md                            → No whitespace issues
```

## Base Branch

Built on top of `agent/cc/pr-live-002-uzen-derived-market-metrics` (PR-LIVE-002 latest).

## Status

Ready for Codex review.
