# PR-REPORT-003 Implementation Report

## Summary

Added deterministic LHB (龙虎榜) reasoning summary for `lhb-analyzer` mode without claiming unsupported seat-level interpretation.

## Changes

### hoxit/uzen.py

- Added `_lhb_summary()` function that derives row count, net-buy totals, and simple signals from `sources.signals.dragon_tiger`
- Updated `analyze_snapshot()` to include `analysis["lhb"]`
- Added "lhb" to `_MODE_SECTIONS` for `lhb-analyzer` mode
- Updated `render_markdown()` to render "龙虎榜分析" section when "lhb" is in visible sections

### tests/test_uzen.py

Added 8 new tests:
- `test_lhb_summary_computed_with_data` — computed status with net_buy and signals
- `test_lhb_summary_data_needed_when_no_rows` — data_needed when no dragon_tiger rows
- `test_lhb_summary_net_sell_signal` — detects net sell signal
- `test_lhb_in_json_artifact` — JSON artifact includes lhb analysis
- `test_markdown_lhb_section_computed` — Markdown renders LHB section with computed values
- `test_markdown_lhb_section_data_needed` — Markdown shows data_needed status
- `test_lhb_section_included_in_lhb_analyzer_mode` — lhb-analyzer mode includes LHB section
- `test_lhb_section_excluded_in_other_modes` — other modes exclude LHB section

## Verification

```
75 tests passed
CLI help shows lhb-analyzer
No whitespace errors
```

## LHB Summary Schema

```json
{
  "status": "computed" | "data_needed",
  "rows": 1,
  "net_buy": 2000.0,
  "has_dragon_tiger": true,
  "signals": ["龙虎榜净买入为正", "龙虎榜共 1 条记录"],
  "warnings": []
}
```

## Notes

- No new data provider added
- No seat-level institution/hot-money classification unless already present in source rows
- No historical seat pattern inference
- Only uses `sources.signals.dragon_tiger` data
- Deterministic signals: net buy/sell/balance, row count
