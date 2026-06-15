# UZEN Research Spine Phase 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small hoxit-native research spine to UZEN so raw hoxit data, deterministic dimensions, synthesis, report review, and optional agent judgment are separate and auditable.

**Architecture:** Keep the current `collect_snapshot() -> analyze_snapshot() -> render_markdown()` flow and add additive `analysis` objects instead of replacing existing keys. Phase 5 must not import UZI-Skill runtime/provider code; it adapts the staged research idea using hoxit's A-share data boundary. Runtime changes should stay in `hoxit/uzen.py` unless a helper split becomes clearly necessary.

**Tech Stack:** Python stdlib, argparse CLI, pytest. No new runtime dependency, no network requirement in unit tests.

---

## Baseline

Phase 4 is merged to `main`.

Current UZEN has:

- mode-specific data collection;
- source quality records;
- compact mode-specific Markdown;
- light DCF and Comps;
- LHB summary;
- five deterministic investor signals;
- optional analysis封套（Agent Analysis Envelope）.

The remaining UZI-Skill gap is the absence of a staged research spine:

```text
raw data -> dimensions -> synthesis -> report review -> final artifact
```

Phase 5 adds that spine incrementally while preserving all existing JSON keys and CLI behavior.

## Non-Goals

- Do not add HTML reports, share cards, browser rendering, or image output.
- Do not add non-A-share support.
- Do not add new external providers.
- Do not import UZI-Skill Python code, provider chain, persona assets, or HTML templates.
- Do not claim full UZI 66-investor parity.
- Do not add LHB seat identity inference, social trap providers, or web/browser fallback.
- Do not change command names, default output paths, or existing artifact filenames.

## PR Sequence

| PR | Title | Purpose |
| --- | --- | --- |
| PR-SPINE-001 | UZEN Dimension Layer | Add additive deterministic `analysis["dimensions"]` objects. |
| PR-SPINE-002 | UZEN Synthesis Layer | Add non-fabricated `analysis["synthesis"]` from existing analysis objects. |
| PR-SPINE-003 | UZEN Report Self Review | Add deterministic `analysis["report_review"]` checklist and tests. |
| PR-SPINE-004 | UZEN Deep Review Envelope | Extend optional agent envelope with validated deep-review fields. |
| PR-SPINE-005 | UZEN Research Spine Docs Sync | Update docs and skills for Phase 5 behavior. |

Only one ticket may be implemented at a time. Claude Code must stop after each ticket's implementation report, commit, push, and `REVIEW_READY` board update.

## Task Details

### Task 1: Dimension Layer

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

- [ ] **Step 1: Add a failing test for dimensions**

Add a test like:

```python
def test_analysis_dimensions_schema():
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14"))
    dimensions = snapshot["analysis"]["dimensions"]

    expected = {"basic", "market", "valuation", "fundamentals", "capital_flow", "panel", "risk", "lhb", "dcf", "comps"}
    assert expected <= set(dimensions)
    for item in dimensions.values():
        assert item["status"] in {"computed", "partial", "data_needed", "unsupported"}
        assert item["quality"] in {"full", "partial", "missing", "skipped", "error"}
        assert isinstance(item["inputs"], list)
        assert isinstance(item["outputs"], list)
        assert isinstance(item["warnings"], list)
```

- [ ] **Step 2: Run the targeted test**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_analysis_dimensions_schema -v
```

Expected: fail because `analysis["dimensions"]` does not exist.

- [ ] **Step 3: Implement `_dimension_summary(snapshot, analysis)`**

Add a helper returning the ten dimension records. Derive quality from existing `snapshot["data_quality"]["sources"]` where possible. Keep it deterministic and additive.

Each record should look like:

```python
{
    "status": "computed",
    "quality": "full",
    "inputs": ["quote", "metrics"],
    "outputs": ["summary"],
    "warnings": [],
}
```

- [ ] **Step 4: Attach dimensions in `analyze_snapshot()`**

Build the existing `analysis` dict first, then set:

```python
analysis["dimensions"] = _dimension_summary(snapshot, analysis)
```

- [ ] **Step 5: Add mode/missing data tests**

Add tests that skipped mode sources produce `quality: "skipped"` or `status: "data_needed"` without failing the report.

- [ ] **Step 6: Verify**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

### Task 2: Synthesis Layer

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

- [ ] **Step 1: Add a failing synthesis schema test**

Add:

```python
def test_synthesis_schema_is_deterministic():
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14"))
    synthesis = snapshot["analysis"]["synthesis"]

    assert synthesis["stance"] in {"bullish", "neutral", "bearish", "data_needed"}
    assert synthesis["confidence"] in {"high", "medium", "low"}
    assert isinstance(synthesis["drivers"], list)
    assert isinstance(synthesis["risks"], list)
    assert isinstance(synthesis["conflicts"], list)
    assert isinstance(synthesis["followups"], list)
    assert synthesis["basis"] == "deterministic_hoxit_analysis"
```

- [ ] **Step 2: Implement `_synthesis_summary(snapshot, analysis)`**

Use only existing deterministic objects:

- `analysis["panel"]`
- `analysis["market_risk"]`
- `analysis["dcf"]`
- `analysis["comps"]`
- `analysis["lhb"]`
- `snapshot["data_quality"]`

Do not use new data sources and do not fabricate statements.

- [ ] **Step 3: Render a compact synthesis section**

Add Markdown section key `synthesis` to modes where useful, preferably after core conclusion. Include stance, confidence, drivers, risks, conflicts, and followups when non-empty.

- [ ] **Step 4: Add Markdown tests**

Assert that Markdown includes `## 综合研判` and no raw dict repr.

- [ ] **Step 5: Verify**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

### Task 3: Report Self Review

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

- [ ] **Step 1: Add report review tests**

Add tests for:

- required JSON sections present;
- disclaimer present;
- mode sections align with `_sections_for_mode()`;
- no raw dict repr in Markdown;
- unsupported UZI features are not claimed.

- [ ] **Step 2: Implement `_report_review(snapshot, markdown=None)`**

Return:

```json
{
  "status": "passed",
  "checks": [
    {"name": "disclaimer_present", "status": "passed", "warnings": []}
  ],
  "warnings": []
}
```

If a check fails, return `status: "warnings"` and list warnings. Do not fail report generation in this phase.

- [ ] **Step 3: Attach review to analysis**

Because Markdown is rendered after `analyze_snapshot()`, initial report review may check JSON-only invariants in `analysis["report_review"]`. Markdown-specific checks can be exposed through helper tests or added before writing artifacts in `run_analysis()`.

- [ ] **Step 4: Verify**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

### Task 4: Deep Review Envelope

**Files:**
- Modify: `hoxit/uzen.py`
- Modify: `hoxit/cli.py` only if needed for error text or validation wiring
- Test: `tests/test_uzen.py`
- Test: `tests/test_cli.py` only if CLI behavior changes

- [ ] **Step 1: Add validation tests for new optional fields**

Extend `_validate_agent_analysis()` tests for:

- `data_gap_acknowledged: dict[str, str]`
- `dimension_commentary: dict[str, str]`
- `panel_insights: str`

- [ ] **Step 2: Extend default envelope**

Default envelope remains `not_provided`, with empty new fields:

```json
{
  "data_gap_acknowledged": {},
  "dimension_commentary": {},
  "panel_insights": ""
}
```

- [ ] **Step 3: Extend Markdown rendering**

When agent analysis is provided, render new fields in `## Agent 定性分析` without raw dict dumps.

- [ ] **Step 4: Preserve compatibility**

Existing agent JSON files without new fields must still validate and get defaults.

- [ ] **Step 5: Verify**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py hoxit/cli.py tests docs/superpowers
```

### Task 5: Documentation Sync

**Files:**
- Modify: `docs/INTERFACES.md`
- Modify: `uzen-skills/README.md`
- Modify: `uzen-skills/commands/*.md`
- Modify: `uzen-skills/skills/*/SKILL.md`

- [ ] **Step 1: Update user docs**

Document:

- `analysis["dimensions"]`
- `analysis["synthesis"]`
- `analysis["report_review"]`
- extended analysis封套（Agent Analysis Envelope）

- [ ] **Step 2: Update skill protocols**

Keep Chinese first. Use bilingual terms only where useful.

- [ ] **Step 3: Fix known doc polish items**

Fix:

- duplicated `### 7.2` heading in `uzen-skills/skills/lhb-analyzer/SKILL.md`;
- `--trade-date` wording so docs match CLI optional default behavior.

- [ ] **Step 4: Verify**

Run:

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

## Full Phase Verification

After PR-SPINE-001 through PR-SPINE-005 are approved and merged:

```bash
.venv/bin/python -m pytest
.venv/bin/hoxit uzen --help
git diff --check
```
