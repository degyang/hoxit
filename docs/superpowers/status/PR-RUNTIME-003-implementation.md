---
title: "PR-RUNTIME-003 Implementation Report"
pr: "PR-RUNTIME-003"
scope: "uzen markdown report contract"
status: "IMPLEMENTED"
date: "2026-06-15"
---

# PR-RUNTIME-003: UZEN Markdown Report Contract

## Summary

Replaced raw dict/list Markdown dumps with compact, stable, human-readable report sections while preserving raw JSON artifacts.

## Deliverables

### 1. `hoxit/uzen.py`

**Added formatting helpers**:

| Helper | Purpose |
|--------|---------|
| `_fmt_number(value, suffix, precision)` | Format number with optional suffix; returns "缺失" for None |
| `_fmt_pct(value)` | Format percentage with +/- sign |
| `_fmt_market_cap(value)` | Format market cap in 亿 units |
| `_compact_list(items, key, max_items)` | Format list as bullet points with top N items |
| `_compact_concepts(concepts, max_items)` | Format concepts as comma-separated names |
| `_group_warnings(warnings)` | De-duplicate warnings |

**Rewrote `render_markdown()`** with compact formatting:

| Section | Before | After |
|---------|--------|-------|
| 核心结论 | `{name}` / `{price}` | `名称：测试股份` / `最新价：10.00元` / `涨跌幅：+2.50%` |
| 行情与估值 | `行情：{...}` / `估值：{...}` | `前瞻 PE：15.00倍` / `PEG：1.20` / `总市值：100.00亿` |
| 基本面与财务 | `基本面：{...}` / `财务：{...}` | `行业：软件开发` / `ROE：12.30%` / `净利润：100,000,000元` |
| 研报/新闻/公告 | `研报数量：1` | `研报（1 条）：` + top 3 titles |
| 资金/龙虎榜 | `概念：[{...}]` | `概念：人工智能` |
| 缺失数据 | `{}` / `[]` | `缺失` / `暂无数据` / `暂无概念数据` |

**Section order preserved**: 10 sections in exact same order as before.

### 2. `tests/test_uzen.py`

Added 8 new tests for markdown report contract:

| Test | Validates |
|------|-----------|
| `test_markdown_no_raw_dict_repr` | No raw `行情：{` or `概念：[{` patterns |
| `test_markdown_quote_section_compact` | Name, price, change_pct formatted |
| `test_markdown_valuation_section_compact` | PE, PEG, PB, market cap formatted |
| `test_markdown_fundamentals_section_compact` | Industry, ROE, net profit formatted |
| `test_markdown_reports_section_compact` | Count + top titles |
| `test_markdown_concepts_section_compact` | Names, not raw list |
| `test_markdown_missing_data_renders_chinese` | "缺失", "未知", "暂无数据" |
| `test_markdown_disclaimer_present` | Disclaimer always present |

### 3. `docs/superpowers/status/PR-RUNTIME-003-implementation.md`

This report.

## Verification

```
$ .venv/bin/python -m pytest tests/test_uzen.py -v
30 passed in 0.12s

$ git diff --check -- hoxit/uzen.py tests/test_uzen.py
(no output)
```

## Acceptance Criteria Checklist

- [x] Markdown no longer contains raw `行情：{...}` or `概念：[{...}]` style dumps.
- [x] Section order remains stable.
- [x] JSON output remains unchanged.
- [x] Missing values render as `缺失` or short Chinese sentence.
- [x] Disclaimer remains present.

## Design Notes

- **JSON untouched**: `render_markdown()` only reads from the snapshot; it never modifies the data structure.
- **Backward compatible**: section order and headings are identical to the previous version.
- **Compact formatting**: numbers use locale-aware formatting with commas; percentages show +/- sign.
- **De-duplicated warnings**: `_group_warnings()` removes exact duplicates while preserving order.
