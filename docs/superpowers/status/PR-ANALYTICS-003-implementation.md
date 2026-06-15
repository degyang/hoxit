# PR-ANALYTICS-003 Implementation Report

## Summary

Implemented risk model split in `hoxit/uzen.py`, separating market-data-based risk flags from social/manipulation trap risk evidence.

## Changes

### `hoxit/uzen.py`

- Renamed `_trap_risk()` to `_market_risk()` with `basis="market_data"` field
- Created new `_trap_risk()` function returning `status="unsupported"` with `basis="social_evidence"`
- Updated `analyze_snapshot()` to include both `market_risk` and `trap_risk`
- Updated `_mode_profile()` for `scan-trap` to use `market_risk` as primary section
- Updated `render_markdown()`:
  - "市场数据风险检查" section with clear "非社交证据" disclaimer
  - "社交/操纵风险检查" section showing unsupported status

### `tests/test_uzen.py`

Updated existing test and added 6 new tests:
- `test_analyze_snapshot_adds_summary_panel_and_risk` — updated to check both market_risk and trap_risk
- `test_market_risk_uses_market_data_basis` — verifies basis="market_data"
- `test_market_risk_flags_from_signals` — verifies flags from block_trade, margin_trading, holder_num
- `test_trap_risk_unsupported` — verifies status="unsupported" with warnings
- `test_markdown_market_risk_section` — verifies market data risk section rendering
- `test_markdown_trap_risk_section` — verifies social/trap risk section rendering
- `test_markdown_risk_wording_no_social_implication` — verifies market risk section doesn't imply social evidence

## Risk Object Shapes

### market_risk
```python
{
    "level": "low" | "medium" | "high",
    "basis": "market_data",
    "flags": list[str],
}
```

### trap_risk
```python
{
    "status": "unsupported" | "data_needed" | "computed",
    "basis": "social_evidence",
    "evidence": list[dict],
    "warnings": list[str],
}
```

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
45 passed

$ .venv/bin/hoxit uzen --help
[OK]

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
[OK]
```

## Scope Compliance

- ✅ Only modified `hoxit/uzen.py`, `tests/test_uzen.py`, `docs/superpowers/status/board.md`
- ✅ No changes to `cli.py`, `pyproject.toml`, `uzen-skills/`, `docs/INTERFACES.md`
- ✅ No social media scraping or evidence collection
- ✅ No new hoxit provider
- ✅ Backward compatibility maintained (trap_risk still exists)
- ✅ Market risk section doesn't imply social/manipulation evidence
