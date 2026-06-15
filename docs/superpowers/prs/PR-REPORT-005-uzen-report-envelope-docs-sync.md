# PR-REPORT-005: UZEN Report Envelope Docs Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-report-005-uzen-report-envelope-docs-sync`

## Design

`docs/superpowers/plans/2026-06-15-uzen-report-envelope-phase4.md`

## Goal

Synchronize Chinese-first docs and skill protocols with Phase 4 report-envelope behavior.

## Scope

- Update user docs for mode-specific Markdown behavior.
- Document the agent analysis envelope and its limits.
- Document LHB summary and DCF/Comps input quality.
- Update command docs and relevant skill protocols.
- Keep docs honest about unsupported UZI features.

## Out of Scope

- No production code changes.
- No test logic changes unless examples are executable and incorrect.
- No new runtime capability claims.

## Files Likely to Change

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `uzen-skills/skills/*/SKILL.md`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-REPORT-005-implementation.md`

## Must Not Change

- `hoxit/uzen.py`
- `hoxit/cli.py`
- `tests/test_uzen.py`
- `tests/test_cli.py`

## Required Behavior

- Docs are Chinese-first.
- Important terms may use bilingual form, for example `分析封套（Agent Analysis Envelope）`.
- Docs distinguish raw JSON, deterministic analysis, and optional qualitative agent analysis.
- Docs do not claim full UZI parity.

## Acceptance Criteria

- [ ] Docs describe mode-specific Markdown sections.
- [ ] Docs describe `agent_analysis` shape and no-fabrication boundary.
- [ ] Docs describe LHB summary limits.
- [ ] Docs describe DCF/Comps input quality.
- [ ] `hoxit uzen --help` still works.

## Test Requirements

- [ ] No new unit tests required unless examples are executable.
- [ ] Run whitespace/diff check.

## Verification Commands

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

## Dependencies

Depends on:

- PR-REPORT-004 approved or merged.

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

Revert the docs PR commit. Runtime behavior from previous Phase 4 PRs remains intact.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-REPORT-004 review.
