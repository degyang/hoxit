# PR-REPORT-001 Implementation Report

## Summary

Implemented mode-specific Markdown section visibility in `hoxit/uzen.py` so focused commands render only relevant sections.

## Changes

### `hoxit/uzen.py`

- Added `_MODE_SECTIONS` dictionary mapping modes to visible Markdown sections
- Added `_sections_for_mode()` helper function
- Updated `render_markdown()` to accept optional `mode` parameter
- Gated all Markdown sections by mode:
  - `core`: Always visible (title, name, price, change)
  - `data_quality`: Always visible
  - `market_valuation`: Always visible
  - `fundamentals`: Always visible
  - `reports_news_filings`: Only in `analyze-stock`
  - `capital_flow`: Only in `analyze-stock`, `quick-scan`, `lhb-analyzer`
  - `industry`: Only in `analyze-stock`, `comps`
  - `panel`: Only in `analyze-stock`, `panel-only`
  - `market_risk`: Only in `analyze-stock`, `scan-trap`
  - `trap_risk`: Only in `analyze-stock`, `scan-trap`
  - `dcf`: Only in `analyze-stock`, `dcf`
  - `comps`: Only in `analyze-stock`, `comps`
  - `followups`: Always visible
- Disclaimer always visible in all modes
- Updated `run_analysis()` to pass mode to `render_markdown()`

### `tests/test_uzen.py`

Added 7 new tests:
- `test_analyze_stock_markdown_has_all_sections` — verify full report
- `test_dcf_markdown_omits_unrelated_sections` — verify DCF mode omits Comps/risk
- `test_comps_markdown_omits_unrelated_sections` — verify Comps mode omits DCF/risk
- `test_panel_only_markdown_omits_unrelated_sections` — verify panel mode omits DCF/Comps/risk
- `test_scan_trap_markdown_omits_unrelated_sections` — verify scan-trap mode omits DCF/Comps/panel
- `test_all_modes_include_disclaimer` — verify disclaimer in all modes
- `test_unknown_mode_renders_all_sections` — verify unknown mode falls back to full

## Mode Section Visibility

| Section | analyze-stock | dcf | comps | panel-only | scan-trap | quick-scan | lhb-analyzer |
|---------|---------------|-----|-------|------------|-----------|------------|--------------|
| 核心结论 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 数据完整性 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 行情与估值 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 基本面与财务 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 研报/新闻/公告 | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 资金/龙虎榜/题材 | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| 行业与同业 | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 投资者面板 | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| 市场数据风险 | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| 社交/操纵风险 | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| DCF 估值 | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| 同业比较 | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 后续跟踪项 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 免责声明 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
59 passed

$ .venv/bin/hoxit uzen --help
[OK]

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
[OK]
```

## Scope Compliance

- ✅ Only modified `hoxit/uzen.py` and `tests/test_uzen.py`
- ✅ JSON artifact unchanged (all analysis objects preserved)
- ✅ No CLI changes
- ✅ No docs/INTERFACES.md changes
- ✅ No uzen-skills/ changes
- ✅ Disclaimer always present in all modes
