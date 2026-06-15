# UZEN Runtime Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make UZEN runtime behavior match the Phase 1 skill protocols by adding real mode-specific execution, structured source quality, and readable Markdown reports.

**Architecture:** Keep `hoxit.uzen` as a single hoxit-native orchestration module for this phase. Add small internal helpers and tests without introducing UZI's provider chain or new external dependencies.

**Tech Stack:** Python stdlib, pytest, existing hoxit modules, injectable `UzenDataProvider`.

---

## File Structure

- `hoxit/uzen.py`: runtime orchestration, mode profiles, source quality, analysis helpers, Markdown rendering.
- `tests/test_uzen.py`: non-network unit tests using injected fake providers.
- `docs/INTERFACES.md`: CLI/API documentation after runtime behavior changes.
- `docs/superpowers/status/PR-RUNTIME-XXX-implementation.md`: cc implementation reports.

## Task 1: Mode Execution Profiles

Ticket: `docs/superpowers/prs/PR-RUNTIME-001-uzen-mode-execution-profiles.md`

Purpose: make `hoxit uzen <mode>` control provider calls instead of only changing `mode_profile` metadata.

- [ ] **Step 1: Write tests proving focused modes skip unrelated providers**

Add a call-recording provider in `tests/test_uzen.py` that appends provider call labels to a list. Assert:

```python
def test_quick_scan_skips_heavy_sources():
    calls = []
    p = recording_provider(calls)
    snapshot = collect_snapshot("600000", mode="quick-scan", provider=p, today="2026-06-14")
    assert "quote" in calls
    assert "metrics" in calls
    assert "reports" not in calls
    assert "filings" not in calls
    assert snapshot["sources"]["reports"] == []
    assert snapshot["sources"]["filings"] == []
```

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_quick_scan_skips_heavy_sources -v
```

Expected before implementation: FAIL because current `collect_snapshot()` calls every provider for every mode.

- [ ] **Step 2: Add internal mode profile call selection**

Modify `hoxit/uzen.py` with an internal profile map that identifies source keys per mode. Keep source keys stable in the JSON payload by filling skipped sources with `{}` or `[]`.

- [ ] **Step 3: Add tests for all modes**

Cover:

- `analyze-stock` calls the full current call graph.
- `panel-only` calls quote, metrics, valuation, fundamentals, finance, and skips news/reports/filings.
- `scan-trap` calls risk-related signals and skips reports.
- `lhb-analyzer` calls dragon tiger and nearby context only.
- unknown mode falls back to `analyze-stock`.

- [ ] **Step 4: Run focused verification**

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-001-implementation.md
```

## Task 2: Source Quality Records

Ticket: `docs/superpowers/prs/PR-RUNTIME-002-uzen-source-quality-records.md`

Purpose: replace warning-only quality with structured per-source quality while preserving backward compatibility.

- [ ] **Step 1: Write tests for full, error, skipped, and unsupported states**

Add assertions for:

```python
quality = snapshot["data_quality"]["sources"]
assert quality["quote"]["quality"] == "full"
assert quality["reports"]["quality"] == "skipped"
assert quality["f10"]["quality"] == "partial"
assert "warnings" in snapshot["data_quality"]
```

Run one new test and confirm it fails before implementation.

- [ ] **Step 2: Add a small `_source_record()` helper**

Represent each source as:

```json
{
  "label": "valuation",
  "quality": "full",
  "source": "provider.valuation",
  "warnings": [],
  "required": false,
  "optional_missing": []
}
```

Use quality values: `full`, `partial`, `missing`, `error`, `skipped`.

- [ ] **Step 3: Preserve existing top-level warning behavior**

Keep:

```python
snapshot["data_quality"]["warnings"]
snapshot["data_quality"]["complete"]
```

Skipped sources must not make `complete` false by themselves.

- [ ] **Step 4: Run verification**

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-002-implementation.md
```

## Task 3: Markdown Report Contract

Ticket: `docs/superpowers/prs/PR-RUNTIME-003-uzen-markdown-report-contract.md`

Purpose: stop rendering raw dict/list dumps and produce compact human-readable Markdown.

- [ ] **Step 1: Add regression tests against raw dumps**

Assert rendered Markdown does not include raw repr patterns for common sections:

```python
markdown = render_markdown(snapshot)
assert "行情：{" not in markdown
assert "估值：{" not in markdown
assert "概念：[{" not in markdown
```

Run the new test and confirm it fails before implementation.

- [ ] **Step 2: Add small formatting helpers**

Keep helpers private in `hoxit/uzen.py`:

- `_fmt_value(value)`
- `_top_titles(rows, limit=3)`
- `_top_names(rows, limit=8)`
- `_render_warnings(warnings)`
- `_render_quote(quote)`
- `_render_valuation(valuation, metrics)`

- [ ] **Step 3: Preserve section order**

Keep current Markdown sections:

1. 核心结论
2. 数据完整性
3. 行情与估值
4. 基本面与财务
5. 研报、新闻与公告
6. 资金、龙虎榜与题材
7. 行业与同业
8. 投资者面板
9. 风险与杀猪盘检查
10. 后续跟踪项

- [ ] **Step 4: Run verification**

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-003-implementation.md
```

## Task 4: Runtime Documentation Sync

Ticket: `docs/superpowers/prs/PR-RUNTIME-004-uzen-runtime-docs-sync.md`

Purpose: update docs after runtime behavior is real and tested.

- [ ] **Step 1: Update `docs/INTERFACES.md`**

Document:

- mode-specific execution behavior;
- source quality records;
- Markdown output contract;
- which capabilities remain deferred.

- [ ] **Step 2: Update UZEN command docs only if runtime behavior changed**

Only edit `uzen-skills/commands/*.md` where current runtime docs are now stale.

- [ ] **Step 3: Run verification**

```bash
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers/status/PR-RUNTIME-004-implementation.md
.venv/bin/hoxit uzen --help
```

## Self-Review

- Spec coverage: This plan covers Phase 2 mode execution correctness, Phase 3 Markdown report contract, and Phase 4 structured source quality from the final parity strategy.
- Placeholder scan: No task contains open-ended implementation placeholders; every PR has concrete tests or verification.
- Type consistency: Source keys remain compatible with current `snapshot["sources"]`; new quality records are additive under `snapshot["data_quality"]["sources"]`.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`.

Execute through the dual-agent workflow, one PR ticket at a time. Start with PR-RUNTIME-001 only.
