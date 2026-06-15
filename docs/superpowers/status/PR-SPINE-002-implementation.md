# PR-SPINE-002 Implementation Report

## Summary

Added deterministic `analysis["synthesis"]` and compact `## 综合研判` Markdown section. Synthesis derives stance, confidence, drivers, risks, conflicts, and followups from existing hoxit analysis objects only — no LLM or agent calls.

## Changes

### hoxit/uzen.py

- Added `_synthesis_summary(snapshot)` function that computes synthesis from allowed inputs only:
  - `analysis["panel"]` → stance (bullish/bearish/neutral/data_needed) and drivers
  - `analysis["market_risk"]` → risk flags
  - `analysis["dimensions"]["risk"]` → risk warnings (includes trap_risk unsupported)
  - `analysis["dcf"]` + `analysis["comps"]` → conflict detection
  - `analysis["dimensions"]` + `analysis["lhb"]` → followups from data gaps
  - `snapshot["data_quality"]` → confidence calibration
- Updated `analyze_snapshot()` to include `analysis["synthesis"]` after dimensions
- Added `"synthesis"` to all `_MODE_SECTIONS` mode sets
- Added `## 综合研判` Markdown section in `render_markdown()` with stance, confidence, drivers, risks, conflicts, followups

### tests/test_uzen.py

Added 10 new tests:
- `test_synthesis_schema` — all required fields present with correct types
- `test_synthesis_bullish_when_panel_bullish` — stance follows panel verdict
- `test_synthesis_data_needed_when_panel_data_needed` — stance=data_needed, confidence=low when all signals data_needed
- `test_synthesis_low_confidence_when_data_quality_incomplete` — confidence=low when data quality has gaps
- `test_synthesis_includes_risk_flags` — each market risk flag appears in synthesis risks
- `test_synthesis_includes_risk_dimension_warnings` — risk dimension warnings (e.g. trap_risk unsupported) appear in synthesis risks
- `test_synthesis_in_json_artifact` — synthesis included in JSON output
- `test_synthesis_markdown_section` — Markdown includes `## 综合研判` with stance/confidence
- `test_synthesis_markdown_data_needed` — Markdown shows 数据不足 when no data
- `test_synthesis_markdown_no_raw_dict` — no raw dict repr in synthesis section

## Verification

```
104 tests passed
CLI help unchanged
No whitespace errors
```

## Synthesis Schema

```json
{
  "basis": "deterministic_hoxit_analysis",
  "stance": "bullish|neutral|bearish|data_needed",
  "confidence": "high|medium|low",
  "drivers": ["面板看多 65分"],
  "risks": ["社交/操纵风险检查尚未实现"],
  "conflicts": ["投资者面板内部存在多空分歧"],
  "followups": ["补充 lhb 维度数据"]
}
```

## Confidence Logic

- `data_needed` stance → always `low`
- `complete` data + ≥3 same-direction votes → `high`
- `complete` data + ≥2 same-direction votes → `medium`
- Otherwise → `low`

## Review Fix (PR-SPINE-002 codex review)

- Removed direct `analysis["trap_risk"]` read from `_synthesis_summary()`
- Risk warnings now sourced from `dimensions["risk"]["warnings"]` (allowed input)
- Strengthened `test_synthesis_includes_risk_flags` to assert each flag individually
- Added `test_synthesis_includes_risk_dimension_warnings` for dimension-sourced warnings

## Notes

- Synthesis is purely deterministic — no LLM or agent calls
- Uses only allowed analysis objects (panel, market_risk, dcf, comps, lhb, dimensions, data_quality)
- Synthesis section appears in all modes
- No new data sources or providers
