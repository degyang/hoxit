# PR-DATA-004 Implementation Report

## Summary

Extended UZEN synthesis and Markdown to consume Phase 6 A-share data coverage facts (governance, business, events) without fabricating unsupported conclusions.

## Changes

### `hoxit/uzen.py`

1. **Extended `_synthesis_summary()`**:
   - Added Phase 6 source consumption: governance, business, event
   - Governance driver: "实控人：{controller}" when controller present
   - Governance risk: "股权质押比例偏高" when pledge > 50%
   - Business driver: "主营构成：{segment}" when segments present
   - Event driver: "近期正面事件 N 条" when positive > negative
   - Event risk: "近期负面事件 N 条" when negative > positive

2. **Added 4 new Markdown sections**:
   - `## 治理与股权结构` — controller, pledge ratio, executive holding, shareholder changes
   - `## 经营与产业链` — revenue segments, customer/supplier concentration
   - `## 事件与催化剂` — event counts, catalysts, latest events with sentiment markers
   - `## 龙虎榜详情` — dragon_tiger record count, latest reason

3. **Updated `_MODE_SECTIONS["analyze-stock"]`**:
   - Added "governance", "business", "events", "lhb_detail" to analyze-stock mode
   - Other modes (quick-scan, etc.) skip these sections

### `tests/test_uzen.py`

Added 16 new tests:

**Synthesis tests (5):**
- `test_synthesis_governance_driver` — controller appears in drivers
- `test_synthesis_governance_high_pledge_risk` — high pledge appears in risks
- `test_synthesis_business_driver` — revenue segment appears in drivers
- `test_synthesis_event_positive_driver` — positive events appear in drivers
- `test_synthesis_event_negative_risk` — negative events appear in risks

**Markdown section tests (8):**
- `test_markdown_governance_section` — governance section renders
- `test_markdown_business_section` — business section renders
- `test_markdown_events_section` — events section renders
- `test_markdown_lhb_detail_section` — lhb_detail section renders
- `test_markdown_governance_no_raw_dict` — no raw dict in governance
- `test_markdown_business_no_raw_dict` — no raw dict in business
- `test_markdown_events_no_raw_dict` — no raw dict in events
- `test_markdown_trap_risk_unsupported_wording` — explicit unsupported wording

**Mode visibility tests (3):**
- `test_markdown_governance_skipped_in_quick_scan` — governance not in quick-scan
- `test_markdown_business_skipped_in_quick_scan` — business not in quick-scan
- `test_markdown_events_skipped_in_quick_scan` — events not in quick-scan

## Verification

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
# Result: 157 passed (141 existing + 16 new)

.venv/bin/hoxit uzen --help
# Result: Normal output, all modes listed

git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
# Result: No whitespace issues
```

## Acceptance Criteria

- [x] Synthesis uses only existing snapshot/analysis objects
- [x] New data can produce concrete drivers, risks, or followups
- [x] Markdown renders human-readable Chinese summaries
- [x] Markdown has no raw dict/list repr
- [x] Unsupported social trap and LHB identity claims remain guarded

## Design Decisions

1. **Synthesis consumption**: Only consumes Phase 6 sources when `status == "computed"`. Data_needed sources are silently skipped — no fabricated conclusions.

2. **Governance risk threshold**: Pledge ratio > 50% triggers risk flag. This is a reasonable threshold for A-share stocks.

3. **Event sentiment**: Positive/negative counts determine driver vs risk. Neutral events are ignored in synthesis.

4. **Markdown sections**: Compact Chinese bullets with sentiment markers (↑/↓/—) for events. No raw dict rendering.

5. **Mode visibility**: New sections only appear in analyze-stock mode. Other modes (quick-scan, panel-only, etc.) skip them to keep output focused.

6. **Trap risk wording**: Explicitly states "尚未支持" (not yet supported) to prevent false security claims.

## Status

Implementation complete. Ready for review.
