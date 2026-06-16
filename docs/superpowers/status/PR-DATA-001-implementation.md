# PR-DATA-001 Implementation Report

## Summary

Added three new iwencai-based interfaces to hoxit for A-share governance, business, and event data:

1. **`governance_summary(code)`** in `fundamentals.py` — 股权结构与治理摘要
2. **`business_summary(code)`** in `fundamentals.py` — 经营与产业链摘要
3. **`event_summary(code)`** in `signals.py` — 事件催化摘要

## Changes

### `hoxit/fundamentals.py`

- Added `governance_summary(code, http_post=None)` using iwencai `management` route
  - Returns: `actual_controller`, `pledge_ratio`, `shareholder_changes`, `executive_holding`
  - Status: `computed` on success, `data_needed` on empty/error

- Added `business_summary(code, http_post=None)` using iwencai `business` route
  - Returns: `revenue_segments`, `customer_concentration`, `supplier_concentration`, `top_customers`
  - Status: `computed` on success, `data_needed` on empty/error

- Added helper functions:
  - `_safe_float(value)` — safe float conversion
  - `_extract_shareholder_changes(rows)` — parse shareholder change records
  - `_extract_revenue_segments(row)` — parse revenue segment breakdown
  - `_extract_top_items(row, keyword)` — extract top-N items (customers/suppliers)

### `hoxit/signals.py`

- Added `event_summary(code, http_post=None)` using iwencai `event` route
  - Returns: `events`, `catalysts`, `positive_count`, `negative_count`
  - Sentiment classification: `positive`, `negative`, `neutral` based on keywords
  - Status: `computed` on success, `data_needed` on empty/error

- Added helper functions:
  - `_extract_events(rows)` — parse event records
  - `_extract_catalysts(rows)` — extract catalyst keywords
  - `_classify_event_sentiment(title, row)` — keyword-based sentiment classification

### Tests

- `tests/test_fundamentals.py`: 8 new tests for governance_summary and business_summary
- `tests/test_signals.py`: 7 new tests for event_summary

Total: 19 new tests, all passing.

## Verification

```bash
# Run tests
.venv/bin/python -m pytest tests/test_fundamentals.py tests/test_signals.py tests/test_iwencai.py -v
# Result: 64 passed

# CLI help
.venv/bin/hoxit --help
# Result: Normal output

# Whitespace check
git diff --check -- hoxit tests docs
# Result: No issues
```

## Design Decisions

1. **Graceful degradation**: All three functions return `status: "data_needed"` with warnings on empty rows or network errors, never raise exceptions.

2. **Injectable http_post**: Follows existing hoxit pattern for testable code without network dependencies.

3. **Keyword-based sentiment**: `_classify_event_sentiment()` uses simple keyword matching (利好/增长/增持 = positive, 利空/减持/处罚 = negative). This is sufficient for initial implementation and can be enhanced later with NLP models.

4. **Field name flexibility**: Functions try multiple field names (e.g., `实际控制人` or `实控人`) to handle iwencai's inconsistent naming across different stocks/time periods.

5. **Limits**: Events capped at 10 records, shareholder changes at 5, catalysts at 5 — prevents excessive data in typical usage.

## API Devlog

Updated `docs/API_DEVLOG.md` with interface additions entry (2026-06-13).

## Status

Implementation complete. Ready for review.
