# PR-ANALYTICS-005: UZEN Analytics Docs Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-analytics-005-uzen-analytics-docs-sync`

## Design

`docs/superpowers/plans/2026-06-15-uzen-analytical-models-phase3.md`

## Goal

Synchronize user-facing Chinese-first documentation with the Phase 3 analytical model behavior after runtime PRs are approved.

## Scope

- Update UZEN command/interface documentation for DCF, comps, risk split, and investor panel outputs.
- Keep Chinese as the primary language.
- Use bilingual labels only for important terms, such as `自由现金流（Free Cash Flow）` and `折现率（Discount Rate）`.
- Update implementation status notes.
- Run docs-focused verification.

## Out of Scope

- No production code changes.
- No test logic changes unless a typo in docs examples requires it.
- No new runtime capability claims.
- No non-A-share documentation beyond deferred/future notes.

## Files Likely to Change

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `uzen-skills/skills/*/SKILL.md`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-ANALYTICS-005-implementation.md`

## Must Not Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `hoxit/cli.py`
- `pyproject.toml`

## Required Behavior

Docs must describe actual implemented behavior and clearly distinguish:

- computed data;
- skipped mode sources;
- missing data;
- unsupported future capabilities;
- JSON raw artifact versus Markdown human report.

## Acceptance Criteria

- [ ] Docs are Chinese-first.
- [ ] Important analytical terms use Chinese labels with optional English in parentheses.
- [ ] Docs do not claim UZI full parity.
- [ ] Docs match current CLI command names and output paths.
- [ ] `hoxit uzen --help` still works.

## Test Requirements

- [ ] No new unit tests required unless docs examples are executable.
- [ ] Run diff whitespace check.

## Verification Commands

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

## Dependencies

Depends on:

- PR-ANALYTICS-004 approved or merged.

## Definition of Done

- [ ] Documentation complete
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Board row moved to REVIEW_READY
- [ ] Current branch committed
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert the docs PR commit. Runtime behavior from previous Phase 3 PRs remains intact.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-ANALYTICS-004 review.
