# PR-REPORT-002 Implementation Report

## Summary

Added optional agent-analysis envelope to UZEN, allowing qualitative judgment to be included without modifying raw data or deterministic hoxit analysis.

## Changes

### hoxit/uzen.py

- Added `_DEFAULT_AGENT_ANALYSIS` constant with default envelope structure
- Added `_empty_agent_analysis()` helper to return deep copies of the default envelope
- Added `_validate_agent_analysis()` to validate and normalize agent analysis input
- Updated `analyze_snapshot()` to accept optional `agent_analysis` parameter
- Updated `render_markdown()` to render "Agent 定性分析" section only when status="provided"
- Updated `run_analysis()` to accept and pass through `agent_analysis` parameter

### hoxit/cli.py

- Added `--agent-analysis <json-file>` argument to all UZEN subcommands (analyze-stock, quick-scan, dcf, comps, panel-only, scan-trap, lhb-analyzer)
- Updated CLI dispatch to read, parse, and validate agent analysis JSON file
- Passes validated envelope to `run_analysis()`

### tests/test_uzen.py

Added 8 new tests:
- `test_agent_analysis_default_is_not_provided` — default envelope has status="not_provided"
- `test_agent_analysis_provided_envelope` — provided envelope preserves all fields
- `test_agent_analysis_partial_envelope` — partial envelope fills missing fields with defaults
- `test_agent_analysis_in_json_artifact` — JSON artifact includes agent_analysis
- `test_agent_analysis_markdown_when_provided` — Markdown renders Agent 定性分析 section
- `test_agent_analysis_markdown_when_not_provided` — Markdown omits section when not provided
- `test_agent_analysis_invalid_type_raises` — non-dict input raises ValueError
- `test_agent_analysis_invalid_field_types_raises` — invalid field types raise ValueError

### tests/test_cli.py

Added 6 new tests:
- `test_cli_uzen_agent_analysis_argument` — --agent-analysis parsed for all subcommands
- `test_cli_uzen_agent_analysis_default_none` — defaults to None
- `test_cli_uzen_dispatch_with_agent_analysis` — passes validated envelope to run_analysis
- `test_cli_uzen_dispatch_without_agent_analysis` — passes None when not provided
- `test_cli_uzen_agent_analysis_file_not_found` — raises FileNotFoundError
- `test_cli_uzen_agent_analysis_invalid_json` — raises ValueError

Updated existing test:
- `test_cli_uzen_dispatch_calls_run_analysis` — now expects agent_analysis=None in kwargs

## Verification

```
80 tests passed
CLI --agent-analysis shown in help
No whitespace errors
```

## Envelope Schema

Default (not provided):
```json
{
  "status": "not_provided",
  "basis": "agent_qualitative_input",
  "thesis": "",
  "assumptions": [],
  "conflicts": [],
  "followups": [],
  "warnings": []
}
```

Provided:
```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "string",
  "assumptions": ["string"],
  "conflicts": ["string"],
  "followups": ["string"],
  "warnings": []
}
```

## Notes

- No LLM calls or prompt generation
- No mutation of sources, data_quality, DCF, Comps, panel, or risk objects
- Agent analysis is purely additive — existing analysis objects are unchanged
- Invalid JSON or non-object JSON fails clearly with ValueError
