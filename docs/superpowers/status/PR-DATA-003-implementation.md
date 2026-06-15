# PR-DATA-003 Implementation Report

## Summary

Extended `analysis["dimensions"]` with Phase 6 coverage dimensions for A-share governance, business, events, policy, sentiment, LHB detail, and deferred UZI dimensions.

## Changes

### `hoxit/uzen.py`

Extended `_dimension_summary()` with 10 new dimensions:

**Phase 6 coverage dimensions (6):**
1. **`governance`** — ownership/governance data from `governance` source
2. **`business`** — supply-chain/business data from `business` source
3. **`events`** — catalysts/events data from `event` source
4. **`policy`** — policy/macro context (unsupported, no source yet)
5. **`sentiment`** — sentiment/social evidence boundary (unsupported, no source yet)
6. **`lhb_detail`** — LHB detail coverage from `dragon_tiger` source

**Deferred UZI dimensions (4):**
7. **`materials`** — commodities/materials (unsupported)
8. **`futures`** — futures/derivatives (unsupported)
9. **`moat`** — moat/patents (unsupported)
10. **`contest`** — competition landscape (unsupported)

Each dimension follows the schema:
- `status`: computed | partial | data_needed | unsupported
- `quality`: full | partial | missing | skipped | error
- `inputs`: source keys used
- `outputs`: analysis keys produced
- `warnings`: any warnings from source quality records

### `tests/test_uzen.py`

1. **Updated `test_dimensions_schema()`** — added all new dimension keys to required set
2. **Added 13 new tests**:
   - `test_dimensions_governance_computed` — governance computed when source full
   - `test_dimensions_business_computed` — business computed when source full
   - `test_dimensions_events_computed` — events computed when source full
   - `test_dimensions_policy_unsupported` — policy is unsupported with warning
   - `test_dimensions_sentiment_unsupported` — sentiment is unsupported with warning
   - `test_dimensions_lhb_detail_computed` — lhb_detail computed when dragon_tiger full
   - `test_dimensions_deferred_uzi_unsupported` — materials/futures/moat/contest all unsupported
   - `test_dimensions_governance_skipped_in_quick_scan` — governance skipped in quick-scan
   - `test_dimensions_business_skipped_in_quick_scan` — business skipped in quick-scan
   - `test_dimensions_events_skipped_in_quick_scan` — events skipped in quick-scan
   - `test_dimensions_lhb_detail_skipped_in_quick_scan` — lhb_detail skipped in quick-scan
   - `test_dimensions_governance_data_needed` — governance reflects data_needed from source
   - `test_dimensions_all_phase6_in_json_artifact` — all Phase 6 dimensions in JSON

## Verification

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
# Result: 141 passed (128 existing + 13 new)

.venv/bin/hoxit uzen --help
# Result: Normal output, all modes listed

git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
# Result: No whitespace issues
```

## Acceptance Criteria

- [x] `analysis["dimensions"]` includes new coverage dimensions
- [x] Each dimension has stable `status`, `quality`, `inputs`, `outputs`, `warnings`
- [x] Deferred UZI dimensions are explicit, not silently omitted
- [x] Existing consumers of prior dimensions keep working (128 existing tests pass)
- [x] Tests cover mode-specific skipped sources

## Design Decisions

1. **Phase 6 coverage dimensions**: Added 6 dimensions for governance, business, events, policy, sentiment, and lhb_detail. These map directly to PR-DATA-001/002 sources.

2. **Deferred UZI dimensions**: Added 4 explicit unsupported dimensions (materials, futures, moat, contest) with Chinese warnings explaining they are not yet implemented. This prevents silent omission.

3. **Policy and sentiment**: Marked as unsupported because no hoxit source exists yet. These are placeholders for future implementation.

4. **LHB detail vs LHB**: Separated `lhb_detail` (dragon_tiger source coverage) from `lhb` (lhb analysis status) to distinguish raw data availability from analysis completeness.

5. **No provider calls**: This PR only extends dimension computation from existing snapshot data. No new provider calls were added.

6. **No synthesis/Markdown changes**: Dimensions are computed but not rendered or used in synthesis. This preserves Phase 5 behavior.

## Status

Implementation complete. Ready for review.
