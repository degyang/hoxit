# PR-LIVE-001 Implementation Report

## Status

REVIEW_READY

## Summary

Introduced deterministic UZEN provider normalization boundary so report logic consumes stable dict/list structures even when live hoxit providers return pandas DataFrame-like objects or nested provider mappings.

## Changes Made

### hoxit/uzen.py

Added three normalization helpers after `_quote_change_pct()`:

- **`_normalize_finance(result)`**: Converts DataFrame-like objects to plain dicts. Priority: `.to_dict()` (pandas) → `.__dict__` (generic objects) → passthrough. `None` returns `{}`.
- **`_normalize_concept(result)`**: Normalizes concept provider output to `list[{name: …}]`. Handles dict form `{total, boards, concept_tags}` with `concept_tags` taking precedence over `boards`.
- **`_normalize_dragon_tiger(result)`**: Normalizes dragon-tiger provider output to list of record dicts. Handles dict form `{records, seats, institution}` by extracting `records`.

Applied normalization in `collect_snapshot()` after sources/signals construction:
```python
sources["finance"] = _normalize_finance(sources.get("finance"))
signals["concept"] = _normalize_concept(signals.get("concept"))
signals["dragon_tiger"] = _normalize_dragon_tiger(signals.get("dragon_tiger"))
```

### tests/test_uzen.py

Added 16 new tests (178 total):

**`_normalize_finance` unit tests (4):**
- `test_normalize_finance_passthrough_dict` — plain dict passthrough
- `test_normalize_finance_none_returns_empty` — None → empty dict
- `test_normalize_finance_to_dict_method` — pandas-like `.to_dict()` conversion
- `test_normalize_finance_dunder_dict` — generic object `.__dict__` fallback

**`_normalize_concept` unit tests (5):**
- `test_normalize_concept_passthrough_list` — canonical list passthrough
- `test_normalize_concept_empty_returns_empty` — None/empty inputs
- `test_normalize_concept_concept_tags` — dict with `concept_tags`
- `test_normalize_concept_boards_only` — dict with `boards` only
- `test_normalize_concept_tags_take_precedence` — `concept_tags` over `boards`

**`_normalize_dragon_tiger` unit tests (4):**
- `test_normalize_dragon_tiger_passthrough_list` — canonical list passthrough
- `test_normalize_dragon_tiger_empty_returns_empty` — None/empty inputs
- `test_normalize_dragon_tiger_records` — dict with `records`
- `test_normalize_dragon_tiger_empty_records` — dict with empty `records`

**Integration tests (3):**
- `test_normalize_finance_dataframe_in_collect_snapshot` — DataFrame-like finance through full pipeline
- `test_normalize_concept_in_collect_snapshot` — dict concept through full pipeline
- `test_normalize_dragon_tiger_in_collect_snapshot` — dict dragon_tiger through full pipeline

**Regression test (1):**
- `test_markdown_no_raw_dict_repr_for_normalized_shapes` — no `concept_tags`, `{'records'`, or `{'name'` in Markdown

Updated 3 existing tests to align with normalization:
- `test_collect_snapshot_finance_dataframe_quality_full` — now uses `.to_dict()` DataFrame mock
- `test_markdown_concepts_accepts_provider_mapping` — verifies normalized list in snapshot
- `test_markdown_lhb_detail_accepts_provider_mapping` — verifies normalized list in snapshot

### docs/API_DEVLOG.md

Added 2026-06-16 entry documenting normalization boundary hardening.

## Files Not Changed

- `hoxit/cli.py` — no CLI changes
- Provider modules — no changes
- `uzen-skills/` — no changes
- PR-LIVE-002 through PR-LIVE-006 — untouched

## Verification

- `.venv/bin/python -m pytest tests/test_uzen.py -v` → 178 passed
- `.venv/bin/hoxit uzen --help` → Normal output
- `git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md` → No whitespace issues

## Notes

- Normalization happens once at `collect_snapshot()` boundary; downstream `analyze_snapshot()` and `render_markdown()` always receive stable types
- `_compact_concepts()` and lhb_detail dict handling retained as defensive code
- No new provider calls, no akshare fallback, no Playwright, no UZEN-internal scraping
