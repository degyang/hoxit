# PR-003 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

PR-003 adds the intended first-version analysis helpers and Markdown renderer without changing CLI, file writing, docs, or external interfaces. The implementation generally follows hoxit structure: no optional third-party imports, no network work in renderer logic, and plain dictionary/string outputs.

However, the PR does not fully satisfy the ticket's required test coverage. The ticket explicitly requires panel summary shape coverage and Markdown section presence plus ordering coverage. Current tests only check `panel.verdict`, `trap_risk.level`, and Markdown section presence. Please add focused assertions for the missing acceptance points.

## Review Object

Base: `origin/agent/cc/pr-002-uzen-snapshot-aggregator`

Head: `agent/cc/pr-003-uzen-markdown-renderer`

Diff command:

```bash
git diff origin/agent/cc/pr-002-uzen-snapshot-aggregator...HEAD
```

Reviewed changed files:

- `docs/superpowers/prs/PR-003-uzen-markdown-renderer.md`
- `docs/superpowers/status/PR-003-implementation.md`
- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Spec Compliance

Pass with test gaps.

The implementation adds the planned analysis and Markdown functions and does not attempt full UZI scoring parity.

## Scope Compliance

Pass.

No CLI integration, file writing, HTML/image rendering, documentation changes, or external endpoint changes were added.

## Acceptance Criteria Check

- [x] `analyze_snapshot()` adds `analysis.summary`.
- [ ] `analyze_snapshot()` adds `analysis.panel` with tested `score`, `verdict`, and `reasons`.
- [x] `analyze_snapshot()` adds `analysis.trap_risk` with `level` and `flags` in implementation.
- [x] `render_markdown()` starts with `# UZEN A股分析：<code>`.
- [ ] Markdown includes required sections with tested stable ordering.
- [x] Markdown includes an investment-advice disclaimer.

## hoxit Structure Check

- [x] No top-level optional dependency imports.
- [x] No CLI changes in this PR.
- [x] No file-writing side effects.
- [x] Outputs remain plain `dict` and `str`.
- [x] Renderer is deterministic and testable without network.

## Test Evidence

Implementation report records:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
# Output: 5 passed

.venv/bin/python -m pytest -q
# Output: 95 passed, 26 skipped

git diff --check -- hoxit/uzen.py tests/test_uzen.py
# Output: no whitespace errors
```

Codex independently reran:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
.venv/bin/python -m pytest -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

Results:

- `tests/test_uzen.py`: `5 passed`
- full default suite: `95 passed, 26 skipped`
- diff check: no whitespace errors

## Issues

### Critical

None.

### Important

1. Missing required test coverage for panel summary shape and Markdown section ordering.

   File: `tests/test_uzen.py`

   The PR ticket requires:

   - panel summary shape coverage, including `score`, `verdict`, and `reasons`
   - Markdown section presence and ordering

   Current tests assert `panel.verdict` and several section presences, but do not assert `panel.score`, `panel.reasons`, or relative ordering of the sections. This leaves part of the public report contract unprotected.

### Minor

None.

## Required Fixes for Claude Code

1. Extend `test_analyze_snapshot_adds_summary_panel_and_risk` to assert:

   ```python
   panel = analyzed["analysis"]["panel"]
   assert isinstance(panel["score"], int)
   assert isinstance(panel["reasons"], list)
   assert panel["reasons"]
   risk = analyzed["analysis"]["trap_risk"]
   assert isinstance(risk["flags"], list)
   ```

2. Extend `test_render_markdown_has_stable_sections` to assert section ordering. For example:

   ```python
   expected_sections = [
       "## 核心结论",
       "## 数据完整性",
       "## 行情与估值",
       "## 基本面与财务",
       "## 研报、新闻与公告",
       "## 资金、龙虎榜与题材",
       "## 行业与同业",
       "## 投资者面板",
       "## 风险与杀猪盘检查",
       "## 后续跟踪项",
   ]
   positions = [markdown.index(section) for section in expected_sections]
   assert positions == sorted(positions)
   ```

3. Rerun:

   ```bash
   .venv/bin/python -m pytest tests/test_uzen.py -q
   .venv/bin/python -m pytest -q
   git diff --check -- hoxit/uzen.py tests/test_uzen.py
   ```

4. Update `docs/superpowers/status/PR-003-implementation.md` with the new evidence and mark the ticket ready for review again.

## Merge Decision

Do not merge PR-003 until the Important issue is resolved.
