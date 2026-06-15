# PR-SPINE-004 Implementation Report

## Summary

Extended the optional agent analysis envelope with validated deep-review fields (`data_gap_acknowledged`, `dimension_commentary`, `panel_insights`) while preserving backward compatibility with Phase 4 `agent_analysis` JSON files.

## Changes

### hoxit/uzen.py

- Extended `_DEFAULT_AGENT_ANALYSIS` and `_empty_agent_analysis()` with 3 new fields:
  - `data_gap_acknowledged`: `dict[str, str]` — agent-acknowledged data gaps per dimension
  - `dimension_commentary`: `dict[str, str]` — agent commentary per dimension
  - `panel_insights`: `str` — agent qualitative insights on investor panel
- Extended `_validate_agent_analysis()` to validate new field types:
  - `data_gap_acknowledged` must be `dict[str, str]`
  - `dimension_commentary` must be `dict[str, str]`
  - `panel_insights` must be `str`
  - Invalid types raise `ValueError` with clear message
  - Missing keys receive defaults (backward compatible)
- Extended Agent Analysis Markdown section to render new fields:
  - `面板洞察：{panel_insights}`
  - `数据缺口确认：` with per-dimension notes
  - `维度评注：` with per-dimension comments

### tests/test_uzen.py

Added 8 new tests:
- `test_agent_analysis_deep_review_defaults` — default envelope includes new fields with empty defaults
- `test_agent_analysis_deep_review_backward_compat` — Phase 4 envelope without new fields remains valid
- `test_agent_analysis_deep_review_provided` — new fields accepted and stored correctly
- `test_agent_analysis_deep_review_invalid_data_gap` — invalid data_gap_acknowledged raises ValueError
- `test_agent_analysis_deep_review_invalid_dimension_commentary` — invalid dimension_commentary raises ValueError
- `test_agent_analysis_deep_review_invalid_panel_insights` — invalid panel_insights raises ValueError
- `test_agent_analysis_deep_review_markdown` — Markdown renders all new fields
- `test_agent_analysis_deep_review_json_artifact` — JSON artifact includes new fields

## Verification

```
120 tests passed (uzen)
13 tests passed (cli)
CLI help unchanged
No whitespace errors
```

## Deep Review Envelope Schema

```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "看多",
  "assumptions": ["行业复苏"],
  "conflicts": [],
  "followups": ["关注 Q2"],
  "warnings": [],
  "data_gap_acknowledged": {"lhb": "龙虎榜数据缺失"},
  "dimension_commentary": {"risk": "风险维度不完整"},
  "panel_insights": "投资者面板显示多空分歧"
}
```

## Notes

- Backward compatible: Phase 4 envelopes without new fields receive defaults
- New fields are optional — no breaking changes to existing CLI or JSON files
- No LLM calls — fields are populated by the calling agent, not by hoxit
- Chinese-first wording preserved; technical terms use Chinese + English pairing
