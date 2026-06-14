# PR-003: UZEN Analysis And Markdown Renderer

## Owner

Claude Code

## Status

CHANGES_REQUESTED

## Branch

`agent/cc/pr-003-uzen-markdown-renderer`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Add first-version analysis summaries, lightweight panel/risk logic, and stable Markdown rendering over UZEN snapshots.

## Scope

- Add `analyze_snapshot()`.
- Add `render_markdown()`.
- Add lightweight valuation/finance panel summary.
- Add lightweight trap-risk flags.
- Keep output informational and avoid unsupported investment advice.

## Out of Scope

- CLI integration.
- File writing.
- Full UZI persona migration.
- Full 22-dimension scoring parity.
- HTML or image rendering.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Must Not Change

- `hoxit/cli.py`
- `uzen-skills/`
- `docs/INTERFACES.md`
- `docs/API_DEVLOG.md`

## Acceptance Criteria

- [ ] `analyze_snapshot()` adds `analysis.summary`.
- [ ] `analyze_snapshot()` adds `analysis.panel` with `score`, `verdict`, and `reasons`.
- [ ] `analyze_snapshot()` adds `analysis.trap_risk` with `level` and `flags`.
- [ ] `render_markdown()` starts with `# UZEN A股分析：<code>`.
- [ ] Markdown includes required sections in stable order.
- [ ] Markdown includes an investment-advice disclaimer.

## Test Requirements

- [ ] Extend `tests/test_uzen.py`.
- [ ] Cover panel summary shape.
- [ ] Cover risk summary shape.
- [ ] Cover Markdown section presence and ordering.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

## Dependencies

Depends on:

- PR-002 approved or merged.

## Definition of Done

- [ ] Implementation complete.
- [ ] Tests pass.
- [ ] Verification commands pass.
- [ ] Commit created on branch `agent/cc/pr-003-uzen-markdown-renderer`.
- [ ] Implementation report written to `docs/superpowers/status/PR-003-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove analysis and Markdown rendering while leaving snapshot collection intact.

## Handoff Notes for Claude Code

Follow Task 3 in the implementation plan. Keep logic deliberately lightweight; do not attempt full UZI scoring parity in this PR.
