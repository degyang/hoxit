---
title: "PR-RUNTIME-002 Implementation Report"
pr: "PR-RUNTIME-002"
scope: "uzen source quality records"
status: "IMPLEMENTED"
date: "2026-06-15"
---

# PR-RUNTIME-002: UZEN Source Quality Records

## Summary

Added structured per-source quality records to UZEN snapshots so the system can distinguish full, partial, missing, error, and skipped data at the source level.

## Deliverables

### 1. `hoxit/uzen.py`

**Changed `_safe_call` return type**: now returns `(result, error_message)` tuple instead of just result. On success `error_message` is `None`; on exception it contains the stringified exception.

**Added `_quality_record()` helper**: builds a standardized quality record dict:
```python
{
    "label": "quote",
    "quality": "full",      # full | partial | missing | error | skipped
    "source": "provider.quote",
    "warnings": [],
    "required": True,
    "optional_missing": []
}
```

**Updated `_map_or_skip` / `_list_or_skip`**: now track quality for each source:
- Skipped sources → `quality="skipped"`
- Provider exceptions → `quality="error"`
- Empty results → `quality="missing"`
- Successful results → `quality="full"`

**Special handling for `f10` and `metrics`**: these have custom logic:
- `f10` with `status="unsupported"` → `quality="partial"` with `optional_missing=["f10 sections unavailable"]`
- `metrics` unwraps the outer dict and checks for the code key

**Updated `data_quality` output structure**:
```json
{
    "complete": true,
    "warnings": [...],
    "sources": {
        "quote": { "label": "quote", "quality": "full", ... },
        "bars": { "label": "bars", "quality": "skipped", ... },
        ...
    }
}
```

**Key rule**: skipped sources do not make top-level `complete` false. Only non-skipped warnings affect completeness.

### 2. `tests/test_uzen.py`

Added 5 new tests for source quality records:

| Test | Validates |
|------|-----------|
| `test_full_source_quality` | Sources with data have quality "full" |
| `test_provider_exception_quality_is_error` | Provider exceptions produce quality "error" with error in warnings |
| `test_skipped_source_quality` | Mode-skipped sources have quality "skipped" |
| `test_f10_unsupported_quality_is_partial` | F10 unsupported produces quality "partial" with optional_missing |
| `test_skipped_sources_do_not_affect_complete` | Skipped sources alone don't make complete false |

### 3. `docs/superpowers/status/PR-RUNTIME-002-implementation.md`

This report.

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
22 passed in 0.11s

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py
(no output)
```

## Acceptance Criteria Checklist

- [x] Per-source quality records exist for top-level sources and signal sources.
- [x] Provider exceptions are visible in the relevant source quality record.
- [x] Mode-skipped sources are marked `skipped`.
- [x] F10 unsupported is marked `partial`, with warnings preserved.
- [x] Existing tests expecting `data_quality.warnings` still pass.

## Design Notes

- **Backward compatible**: top-level `complete` and `warnings` fields are preserved with the same semantics.
- **Skipped ≠ incomplete**: skipped sources get `quality="skipped"` but don't affect `complete`. This is intentional — a `quick-scan` run with no errors should report `complete: true` even though most sources are skipped.
- **`_safe_call` signature change**: the return type changed from `Any` to `tuple[Any, str | None]`. All internal callers (`_map_or_skip`, `_list_or_skip`, special `f10`/`metrics` handling) are updated accordingly.
