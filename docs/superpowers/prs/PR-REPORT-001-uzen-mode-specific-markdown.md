# PR-REPORT-001: UZEN Mode-Specific Markdown Sections

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-report-001-uzen-mode-specific-markdown`

## Design

`docs/superpowers/plans/2026-06-15-uzen-report-envelope-phase4.md`

## Goal

Make Markdown reports respect the selected UZEN mode so focused commands do not render unrelated `data_needed` sections.

## Scope

- Add an internal mode-to-Markdown-section profile in `hoxit/uzen.py`.
- Gate `render_markdown()` sections by mode.
- Preserve full JSON output and existing analysis objects.
- Add tests for `dcf`, `comps`, `scan-trap`, `panel-only`, and `analyze-stock` section visibility.

## Out of Scope

- No agent analysis envelope.
- No CLI argument changes.
- No LHB reasoning changes.
- No DCF/Comps math changes.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-REPORT-001-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

- `analyze-stock` Markdown keeps full sections.
- `dcf` Markdown includes DCF and omits Comps and risk sections.
- `comps` Markdown includes Comps and omits DCF and risk sections.
- `panel-only` Markdown includes investor panel and omits DCF/Comps/risk sections.
- `scan-trap` Markdown includes market/trap risk and omits DCF/Comps/panel sections.
- Raw JSON artifacts are unchanged except for any test fixture ordering created by existing functions.

## Acceptance Criteria

- [ ] Focused mode Markdown no longer shows unrelated `data_needed` sections.
- [ ] `analyze-stock` remains a full report.
- [ ] Existing Markdown disclaimer remains present in every mode.
- [ ] Existing tests pass.

## Test Requirements

- [ ] Add section visibility tests for focused modes.
- [ ] Add regression test for `analyze-stock` full sections.
- [ ] Keep tests network-free.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- Phase 3 complete and merged.

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Board row moved to REVIEW_READY
- [ ] Current branch committed
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert the PR commit to restore always-render-all Markdown behavior.

## Handoff Notes for Claude Code

Start from `main`. Follow this ticket exactly and do not begin PR-REPORT-002.
