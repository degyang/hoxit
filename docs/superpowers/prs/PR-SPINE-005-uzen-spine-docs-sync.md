# PR-SPINE-005: UZEN Research Spine Docs Sync

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-spine-005-uzen-spine-docs-sync`

## Design

`docs/superpowers/plans/2026-06-15-uzen-research-spine-phase5.md`

## Goal

Synchronize Chinese-first docs and skill protocols with Phase 5 research spine behavior.

## Scope

- Update `docs/INTERFACES.md`.
- Update `uzen-skills/README.md`.
- Update relevant `uzen-skills/commands/*.md`.
- Update relevant `uzen-skills/skills/*/SKILL.md`.
- Document dimensions, synthesis, report review, and extended agent analysis envelope.
- Fix known doc polish items from Phase 4 review.

## Out of Scope

- No production code changes.
- No test logic changes unless an executable docs example is incorrect.
- No new runtime capability claims.
- No HTML/66-investor/LHB-seat/social-trap claims.

## Files Likely to Change

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `uzen-skills/skills/*/SKILL.md`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-SPINE-005-implementation.md`

## Must Not Change

- `hoxit/uzen.py`
- `hoxit/cli.py`
- `tests/test_uzen.py`
- `tests/test_cli.py`

## Required Behavior

Docs must explain:

- `analysis["dimensions"]`
- `analysis["synthesis"]`
- `analysis["report_review"]`
- extended analysis封套（Agent Analysis Envelope）
- current vs deferred UZI parity boundaries

Docs must fix:

- duplicated `### 7.2` in `uzen-skills/skills/lhb-analyzer/SKILL.md`
- `--trade-date` wording mismatch with CLI optional behavior

## Acceptance Criteria

- [ ] Docs are Chinese-first.
- [ ] Important terms may use bilingual form.
- [ ] Docs distinguish raw data, dimensions, deterministic synthesis, report review, and optional agent judgment.
- [ ] Docs do not claim full UZI parity.
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

- PR-SPINE-004 approved or merged.

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

Revert the docs PR commit. Runtime behavior from previous Phase 5 PRs remains intact.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-SPINE-004 review.
