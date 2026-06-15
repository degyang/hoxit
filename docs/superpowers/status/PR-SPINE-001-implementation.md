# PR-SPINE-001 Implementation Report

## Summary

Added a deterministic dimension layer to `analyze_snapshot()`. Each dimension summarizes one analysis area (basic, market, valuation, fundamentals, capital_flow, panel, risk, lhb, dcf, comps) with status, quality, inputs, outputs, and warnings.

## Changes

### hoxit/uzen.py

- Added `_dimension_summary(snapshot)` function that computes 10 dimension objects from snapshot data:
  - `basic` — quote + fundamentals quality
  - `market` — quote + bars + metrics quality
  - `valuation` — valuation + metrics quality
  - `fundamentals` — fundamentals + finance + f10 quality
  - `capital_flow` — concept + fund_flow + dragon_tiger quality
  - `panel` — investor panel analysis status
  - `risk` — market_risk + trap_risk status
  - `lhb` — LHB analysis status (data_needed when no dragon_tiger rows)
  - `dcf` — DCF analysis status (data_needed when inputs missing)
  - `comps` — Comps analysis status (data_needed when no peer data)
- Updated `analyze_snapshot()` to include `snapshot["analysis"]["dimensions"]`
- Fixed ordering: dimensions computed after analysis dict is populated so `_dim_status` can read panel/dcf/lhb/comps statuses
- Fixed risk dimension: when `trap_risk.status == "unsupported"`, risk is now `partial` with warning "社交/操纵风险检查尚未实现"
- Removed unused `sources` and `signals` local variables from `_dimension_summary`

### tests/test_uzen.py

Added 14 new tests:
- `test_dimensions_schema` — each dimension has status, quality, inputs, outputs, warnings
- `test_dimensions_basic_computed` — basic dimension computed with quote + fundamentals
- `test_dimensions_market_computed` — market dimension computed with quote + bars + metrics
- `test_dimensions_panel_computed` — panel dimension derived from panel analysis
- `test_dimensions_risk_computed` — risk dimension partial when trap_risk unsupported
- `test_dimensions_risk_partial_when_trap_risk_unsupported` — explicit partial+warning check
- `test_dimensions_skipped_sources_in_quick_scan` — quick-scan produces skipped quality for heavy sources
- `test_dimensions_lhb_data_needed` — LHB dimension data_needed when no dragon_tiger rows
- `test_dimensions_lhb_computed` — LHB dimension computed when dragon_tiger data exists
- `test_dimensions_dcf_data_needed` — DCF dimension data_needed when inputs missing
- `test_dimensions_computed_with_sufficient_data` — DCF dimension computed when all inputs present
- `test_dimensions_in_json_artifact` — dimensions included in JSON output
- `test_dimensions_existing_analysis_unchanged` — dimensions added without breaking existing analysis keys

## Verification

```
94 tests passed
CLI help unchanged
No whitespace errors
```

## Dimension Schema

```json
"dimensions": {
  "basic": {"status": "computed", "quality": "full", "inputs": ["quote", "fundamentals"], "outputs": ["summary"], "warnings": []},
  "market": {"status": "computed", "quality": "full", "inputs": ["quote", "bars", "metrics"], "outputs": ["price", "change"], "warnings": []},
  "panel": {"status": "computed", "quality": "full", "inputs": ["panel"], "outputs": ["verdict"], "warnings": []},
  "risk": {"status": "partial", "quality": "partial", "inputs": ["block_trade", "margin_trading", "holder_num", "fund_flow"], "outputs": ["market_risk", "trap_risk"], "warnings": ["社交/操纵风险检查尚未实现"]},
  "lhb": {"status": "data_needed", "quality": "missing", "inputs": ["lhb"], "outputs": ["lhb"], "warnings": []},
  "dcf": {"status": "data_needed", "quality": "missing", "inputs": ["dcf"], "outputs": ["dcf"], "warnings": []},
  "comps": {"status": "data_needed", "quality": "missing", "inputs": ["comps"], "outputs": ["comps"], "warnings": []}
}
```

## Review Fix (PR-SPINE-001 codex review)

- Risk dimension now returns `partial` status/quality when `trap_risk.status == "unsupported"`
- Risk dimension includes warning "社交/操纵风险检查尚未实现" from trap_risk analysis
- Removed unused `sources` and `signals` local variables from `_dimension_summary`
- Added `test_dimensions_risk_partial_when_trap_risk_unsupported` test
- Added `test_dimensions_skipped_sources_in_quick_scan` test for skipped-source behavior

## Notes

- Dimensions are purely additive metadata — no existing analysis keys changed
- `_dim_status` reads from the already-populated analysis dict (panel, dcf, lhb, comps)
- `_dim_quality` aggregates source quality records for composite dimensions
- No new data sources or providers added
