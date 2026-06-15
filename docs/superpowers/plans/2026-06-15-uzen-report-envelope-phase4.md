# UZEN Report Envelope Phase 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tighten UZEN's report behavior after Phase 3 by making Markdown mode-specific, adding a declared agent-analysis envelope, and improving LHB/DCF/Comps output quality without adding new data sources.

**Architecture:** Keep `hoxit/uzen.py` as the runtime boundary for this phase. `collect_snapshot()` continues to collect raw hoxit data, `analyze_snapshot()` creates deterministic derived objects, and `render_markdown()` controls human-readable output sections. Optional qualitative agent judgment must live only in a declared `analysis["agent_analysis"]` envelope and must never modify raw hoxit data or deterministic analysis objects.

**Tech Stack:** Python stdlib, argparse CLI, pytest. No new runtime dependency, no network requirement in unit tests.

---

## Current Baseline

Phase 3 is merged:

- `dcf` produces a light DCF analysis.
- `comps` produces industry multiple context.
- `scan-trap` splits `market_risk` and unsupported `trap_risk`.
- `panel-only` produces 5 deterministic investor signals and vote distribution.
- User-facing docs and skill protocols describe the Phase 3 runtime.

Remaining product gaps are now mostly report behavior and qualitative-boundary gaps:

- Markdown still renders every major section for every mode, causing focused reports to show unrelated `data_needed` sections.
- There is no explicit place for an agent to add qualitative judgment without mixing it into deterministic hoxit output.
- `lhb-analyzer` still reports raw counts but lacks a focused LHB reasoning summary.
- DCF/Comps report insufficient-input details but do not yet expose a compact, shared input-quality summary.

## Non-Goals

- Do not add new external providers.
- Do not import UZI-Skill runtime/provider code.
- Do not implement social trap evidence, HTML rendering, share cards, or non-A-share support.
- Do not claim full UZI 65-investor parity.
- Do not change existing command names or default artifact paths.
- Do not let agent-written qualitative judgment overwrite `sources`, `data_quality`, or deterministic analysis fields.

## PR Sequence

| PR | Title | Purpose |
| --- | --- | --- |
| PR-REPORT-001 | UZEN Mode-Specific Markdown Sections | Render only the sections expected for each focused mode while preserving raw JSON. |
| PR-REPORT-002 | UZEN Agent Analysis Envelope | Add optional declared qualitative-analysis envelope with validation and CLI input. |
| PR-REPORT-003 | UZEN LHB Reasoning Summary | Add deterministic LHB summary object and focused Markdown section. |
| PR-REPORT-004 | UZEN DCF/Comps Input Quality | Add compact input-quality summaries for DCF and Comps so missing data is easier to audit. |
| PR-REPORT-005 | UZEN Report Envelope Docs Sync | Update Chinese-first docs and skill protocols for Phase 4 behavior. |

Only one ticket may be implemented at a time. Claude Code must stop after each ticket's implementation report, commit, push, and `REVIEW_READY` board update.

## Task Details

### Task 1: Mode-Specific Markdown Sections

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

- [ ] **Step 1: Add tests for focused report sections**

Add tests that assert:

```python
def test_dcf_markdown_is_focused(tmp_path):
    result = run_analysis("600000", mode="dcf", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    markdown = Path(result["markdown_path"]).read_text(encoding="utf-8")
    assert "## DCF 估值" in markdown
    assert "## 同业比较（Comps）" not in markdown
    assert "## 市场数据风险检查" not in markdown

def test_comps_markdown_is_focused(tmp_path):
    result = run_analysis("600000", mode="comps", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    markdown = Path(result["markdown_path"]).read_text(encoding="utf-8")
    assert "## 同业比较（Comps）" in markdown
    assert "## DCF 估值" not in markdown

def test_analyze_stock_markdown_keeps_full_sections():
    snapshot = analyze_snapshot(collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)
    assert "## DCF 估值" in markdown
    assert "## 同业比较（Comps）" in markdown
    assert "## 市场数据风险检查" in markdown
```

- [ ] **Step 2: Add a section profile helper**

Implement an internal helper such as:

```python
def _markdown_sections_for_mode(mode: str) -> set[str]:
    profiles = {
        "quick-scan": {"summary", "quality", "quote_valuation", "fundamentals", "capital_theme", "market_risk", "followups"},
        "dcf": {"summary", "quality", "quote_valuation", "fundamentals", "dcf", "followups"},
        "comps": {"summary", "quality", "quote_valuation", "fundamentals", "industry", "comps", "followups"},
        "panel-only": {"summary", "quality", "quote_valuation", "fundamentals", "panel", "followups"},
        "scan-trap": {"summary", "quality", "capital_theme", "market_risk", "trap_risk", "followups"},
        "lhb-analyzer": {"summary", "quality", "capital_theme", "market_risk", "followups"},
        "analyze-stock": {"summary", "quality", "quote_valuation", "fundamentals", "reports_news_filings", "capital_theme", "industry", "panel", "market_risk", "trap_risk", "dcf", "comps", "followups"},
    }
    return profiles.get(mode, profiles["analyze-stock"])
```

- [ ] **Step 3: Gate Markdown sections**

In `render_markdown()`, append each section only when its section key appears in the mode section profile.

- [ ] **Step 4: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
```

Expected: all UZEN tests pass.

### Task 2: Agent Analysis Envelope

**Files:**
- Modify: `hoxit/uzen.py`
- Modify: `hoxit/cli.py`
- Test: `tests/test_uzen.py`
- Test: `tests/test_cli.py`

Add optional input without changing existing defaults:

```python
def run_analysis(..., agent_analysis: dict[str, Any] | None = None) -> dict[str, Any]:
    ...
```

Envelope shape:

```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "...",
  "assumptions": ["..."],
  "conflicts": ["..."],
  "followups": ["..."],
  "warnings": []
}
```

If not provided:

```json
{
  "status": "not_provided",
  "basis": "agent_qualitative_input",
  "thesis": "",
  "assumptions": [],
  "conflicts": [],
  "followups": [],
  "warnings": []
}
```

CLI input should be a JSON file path:

```bash
hoxit uzen analyze-stock 600000 --agent-analysis path/to/agent-analysis.json
```

The CLI must parse JSON only, reject invalid JSON with a clear argparse/runtime error, and pass the parsed dict to `run_analysis()`.

### Task 3: LHB Reasoning Summary

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

Add `analysis["lhb"]` with a deterministic structure:

```json
{
  "status": "computed" | "data_needed",
  "trade_date": "2026-06-14",
  "rows": 1,
  "net_buy": 2000.0,
  "has_dragon_tiger": true,
  "signals": ["龙虎榜净买入为正"],
  "warnings": []
}
```

Do not infer seat-level institution/hot-money detail unless current hoxit data exposes it.

### Task 4: DCF/Comps Input Quality

**Files:**
- Modify: `hoxit/uzen.py`
- Test: `tests/test_uzen.py`

Add compact input quality subobjects:

```json
"dcf": {
  "input_quality": {
    "required": ["net_profit", "share_count"],
    "available": ["market_price", "net_profit"],
    "missing": ["share_count"],
    "proxy_used": ["net_profit_as_cash_flow"]
  }
}
```

```json
"comps": {
  "input_quality": {
    "peer_rows": 5,
    "pe_samples": 5,
    "pb_samples": 5,
    "missing": []
  }
}
```

The goal is auditability, not new valuation logic.

### Task 5: Documentation Sync

**Files:**
- Modify: `docs/INTERFACES.md`
- Modify: `uzen-skills/README.md`
- Modify: `uzen-skills/commands/*.md`
- Modify: `uzen-skills/skills/*/SKILL.md`

Update docs after runtime PRs are approved. Keep Chinese first, with important terms bilingual only where useful, for example `分析封套（Agent Analysis Envelope）`.

## Verification

Production PRs:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py hoxit/cli.py tests docs/superpowers
```

Docs-only PR:

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

Full phase merge:

```bash
.venv/bin/python -m pytest
```
