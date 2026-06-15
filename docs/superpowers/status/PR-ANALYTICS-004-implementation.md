# PR-ANALYTICS-004 Implementation Report

## Summary

Extended investor panel with deterministic signal schema and vote distribution in `hoxit/uzen.py`.

## Changes

### `hoxit/uzen.py`

- Added 5 investor archetype functions:
  - `_value_investor()` — low PE, reasonable PB
  - `_quality_investor()` — high ROE, stable profitability
  - `_growth_investor()` — earnings growth, PEG
  - `_momentum_investor()` — price trend, fund flow, dragon tiger
  - `_hot_money_investor()` — block trade, margin trading, holder changes
- Each returns: `investor_id`, `name`, `group`, `signal`, `score`, `confidence`, `reasoning`
- Updated `_panel_summary()` to:
  - Run all 5 investor archetypes
  - Compute `vote_distribution` (pass/fail/neutral/data_needed counts)
  - Preserve `score`, `verdict`, `reasons` for backward compatibility
- Updated `render_markdown()` with compact panel section:
  - Shows vote distribution (看多/看空/中性/数据不足)
  - Shows individual investor signals with scores
  - No raw dict/list dumps

### `tests/test_uzen.py`

Updated existing test and added 7 new tests:
- `test_analyze_snapshot_adds_summary_panel_and_risk` — updated to check signals and vote_distribution
- `test_panel_signals_schema` — verifies all required fields present
- `test_panel_vote_distribution` — verifies vote counts match signals
- `test_panel_investor_ids` — verifies all 5 archetypes present
- `test_panel_data_needed_when_missing_data` — verifies data_needed when data missing
- `test_panel_value_investor_low_pe` — verifies value investor passes with low PE
- `test_panel_quality_investor_high_roe` — verifies quality investor passes with high ROE
- `test_markdown_panel_section` — verifies markdown rendering

## Panel Object Shape

```python
{
    "score": int,
    "verdict": "bullish" | "neutral" | "bearish",
    "reasons": list[str],
    "signals": [
        {
            "investor_id": str,
            "name": str,
            "group": str,
            "signal": "pass" | "fail" | "neutral" | "data_needed",
            "score": int,
            "confidence": float,
            "reasoning": list[str],
        }
    ],
    "vote_distribution": {
        "pass": int,
        "fail": int,
        "neutral": int,
        "data_needed": int,
    },
}
```

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
52 passed

$ .venv/bin/hoxit uzen --help
[OK]

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
[OK]
```

## Scope Compliance

- ✅ Only modified `hoxit/uzen.py`, `tests/test_uzen.py`, `docs/superpowers/status/board.md`
- ✅ No changes to `cli.py`, `pyproject.toml`, `uzen-skills/`, `docs/INTERFACES.md`
- ✅ No LLM role-play or external persona files
- ✅ Preserved backward compatibility (score, verdict, reasons still present)
- ✅ All 5 baseline investor archetypes implemented
- ✅ Missing data produces data_needed signals
- ✅ Markdown shows panel signal distribution without raw dict/list dumps
