# PR-RUNTIME-003: UZEN Markdown Report Contract

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-runtime-003-uzen-markdown-report-contract`

## Design

`docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`

## Goal

Replace raw dict/list Markdown dumps with compact, stable, human-readable report sections while preserving raw JSON artifacts.

## Scope

Improve `render_markdown()` and small private formatting helpers in `hoxit/uzen.py`.

## Out of Scope

- Do not change snapshot JSON structure except reading existing fields.
- Do not change provider calls or source quality logic.
- Do not add HTML rendering or share cards.
- Do not implement DCF/comps/panel runtime models.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/PR-RUNTIME-003-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `hoxit/signals.py`
- `docs/API_DEVLOG.md`
- `uzen-skills/skills/*/SKILL.md`

## Required Behavior

Keep the current Markdown section order:

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

Render compact values instead of raw Python representations:

- quote: name, latest price, change percent.
- valuation/metrics: forward PE, PEG, PE TTM, PB, market cap when available.
- fundamentals/finance: industry, ROE, net profit when available.
- reports/news/filings: counts plus top 3 titles.
- concepts: top 5-8 names.
- fund flow/LHB/industry: counts and compact highlights.
- warnings: grouped and de-duplicated.

## Acceptance Criteria

- [ ] Markdown no longer contains raw `行情：{...}` or `概念：[{...}]` style dumps.
- [ ] Section order remains stable.
- [ ] JSON output remains unchanged except for prior approved quality additions.
- [ ] Missing values render as `缺失` or a short Chinese sentence, not `{}` or `[]`.
- [ ] Disclaimer remains present.

## Test Requirements

- [ ] Add regression tests that raw dict/list reprs are not emitted for quote, valuation, fundamentals, finance, and concept sections.
- [ ] Preserve existing section-order test.
- [ ] Test missing data renders readable fallback text.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-003-implementation.md
```

## Dependencies

Depends on:

- PR-RUNTIME-002 APPROVED or MERGED

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Current PR status moved to REVIEW_READY
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update PR-RUNTIME-004 or any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert this PR to restore the previous Markdown renderer while keeping JSON artifacts unaffected.

## Handoff Notes for Claude Code

Follow this ticket exactly. Do not expand scope. If PR-RUNTIME-002 is not approved or merged, stop and report the dependency blocker.
