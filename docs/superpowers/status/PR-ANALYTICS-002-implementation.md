# PR-ANALYTICS-002 Implementation Report

## Summary

Implemented hoxit-native comparable-company summary in `hoxit/uzen.py`.

## Changes

### `hoxit/uzen.py`

- Added `_comps_summary(snapshot)` helper function
  - Extracts subject PE/PB from `sources.metrics`
  - Extracts peer multiples from `sources.signals.industry`
  - Computes median PE and median PB from peer data
  - Determines position: `below_median`, `near_median`, `above_median`, or `unknown`
  - Returns `status="data_needed"` when peer PE/PB data is insufficient
- Updated `analyze_snapshot()` to include `comps: _comps_summary(snapshot)`
- Updated `render_markdown()` with Chinese-first comps section:
  - Shows sample count, subject PE/PB, industry median PE/PB, position
  - Shows `data_needed` status with warnings when peer data missing

### `tests/test_uzen.py`

Added 5 new tests:
- `test_comps_computed_with_peer_data` — verifies median calculation and position
- `test_comps_data_needed_when_no_peers` — verifies data_needed when no peers
- `test_comps_data_needed_when_peers_have_no_multiples` — verifies data_needed when peers lack PE/PB
- `test_markdown_comps_section_computed` — verifies markdown rendering with computed comps
- `test_markdown_comps_section_data_needed` — verifies markdown rendering with data_needed

Updated `test_render_markdown_has_stable_sections` to include DCF and Comps sections.

## Comps Object Shape

```python
{
    "status": "computed" | "data_needed",
    "subject": {"name": str, "industry": str, "pe_ttm": float|None, "pb": float|None},
    "rows": [{"name": str, "code": str, "pe_ttm": float|None, "pb": float|None}],
    "median_pe": float | None,
    "median_pb": float | None,
    "position": "below_median" | "near_median" | "above_median" | "unknown",
    "warnings": list[str],
}
```

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
39 passed

$ .venv/bin/hoxit uzen --help
[OK]

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
[OK]
```

## Scope Compliance

- ✅ Only modified `hoxit/uzen.py`, `tests/test_uzen.py`, `docs/superpowers/status/board.md`
- ✅ No changes to `cli.py`, `pyproject.toml`, `uzen-skills/`, `docs/INTERFACES.md`
- ✅ No DCF changes
- ✅ No new iwencai peer interface
- ✅ Tests prove missing peer multiples do not create fake medians
