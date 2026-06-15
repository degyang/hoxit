# Agent Work Board

## Current Feature

UZEN Runtime Phase 2

## Design

- Spec: `docs/superpowers/specs/2026-06-14-uzen-skills-design.md`
- Plan: `docs/superpowers/plans/2026-06-14-uzen-skills.md`
- Gap Audit: `docs/superpowers/specs/2026-06-14-uzen-uzi-gap-audit.md`
- Final Strategy: `docs/superpowers/specs/2026-06-15-uzen-final-parity-strategy.md`
- Skill Gap Audit: `docs/superpowers/specs/2026-06-15-uzen-skill-file-gap-audit.md`
- Phase 1 Plan: `docs/superpowers/plans/2026-06-15-uzen-skill-protocol-phase1.md`
- Runtime Phase 2 Plan: `docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`
- Status: PHASE_2_PR_PLANNED

## UZEN v1 PR Queue

| PR | Title | Owner | Status | Branch | Review |
| --- | --- | --- | --- | --- | --- |
| PR-001 | UZEN Skill Skeleton | Claude Code | MERGED | agent/cc/pr-001-uzen-skill-skeleton | docs/superpowers/reviews/PR-001-codex-review.md |
| PR-002 | UZEN Snapshot Aggregator | Claude Code | MERGED | agent/cc/pr-002-uzen-snapshot-aggregator | docs/superpowers/reviews/PR-002-codex-review.md |
| PR-003 | UZEN Analysis And Markdown Renderer | Claude Code | MERGED | agent/cc/pr-003-uzen-markdown-renderer | docs/superpowers/reviews/PR-003-codex-review.md |
| PR-004 | UZEN CLI Workflow | Claude Code | MERGED | agent/cc/pr-004-uzen-cli-workflow | docs/superpowers/reviews/PR-004-codex-review.md |
| PR-005 | UZEN Mode Profiles | Claude Code | MERGED | agent/cc/pr-005-uzen-mode-profiles | docs/superpowers/reviews/PR-005-codex-review.md |
| PR-006 | UZEN Interface Documentation | Claude Code | MERGED | agent/cc/pr-006-uzen-interface-docs | docs/superpowers/reviews/PR-006-codex-review.md |

## Skill Protocol Phase 1 PR Queue

| PR | Title | Owner | Status | Branch | Review |
| --- | --- | --- | --- | --- | --- |
| PR-SKILL-001 | UZEN Deep Analysis Protocol | Claude Code | MERGED | agent/cc/pr-skill-001-uzen-deep-analysis-protocol | docs/superpowers/reviews/PR-SKILL-001-codex-review.md |
| PR-SKILL-002 | UZEN Investor Panel Protocol | Claude Code | MERGED | agent/cc/pr-skill-002-uzen-investor-panel-protocol | docs/superpowers/reviews/PR-SKILL-002-codex-review.md |
| PR-SKILL-003 | UZEN Trap Detector Protocol | Claude Code | MERGED | agent/cc/pr-skill-003-uzen-trap-detector-protocol | docs/superpowers/reviews/PR-SKILL-003-codex-review.md |
| PR-SKILL-004 | UZEN LHB Analyzer Protocol | Claude Code | MERGED | agent/cc/pr-skill-004-uzen-lhb-analyzer-protocol | docs/superpowers/reviews/PR-SKILL-004-codex-review.md |

## Runtime Phase 2 PR Queue

| PR | Title | Owner | Status | Branch | Review |
| --- | --- | --- | --- | --- | --- |
| PR-RUNTIME-001 | UZEN Mode Execution Profiles | Claude Code | MERGED | agent/cc/pr-runtime-001-uzen-mode-execution-profiles | docs/superpowers/reviews/PR-RUNTIME-001-codex-review.md |
| PR-RUNTIME-002 | UZEN Source Quality Records | Claude Code | MERGED | agent/cc/pr-runtime-002-uzen-source-quality-records | docs/superpowers/reviews/PR-RUNTIME-002-codex-review.md |
| PR-RUNTIME-003 | UZEN Markdown Report Contract | Claude Code | MERGED | agent/cc/pr-runtime-003-uzen-markdown-report-contract | docs/superpowers/reviews/PR-RUNTIME-003-codex-review.md |
| PR-RUNTIME-004 | UZEN Runtime Docs Sync | Claude Code | REVIEW_READY | agent/cc/pr-runtime-004-uzen-runtime-docs-sync | docs/superpowers/reviews/PR-RUNTIME-004-codex-review.md |

## Status Values

TODO -> IN_PROGRESS -> REVIEW_READY -> CHANGES_REQUESTED -> APPROVED -> MERGED

## Workflow Gates

- Claude Code may move only the current assigned PR from TODO/CHANGES_REQUESTED to IN_PROGRESS and then REVIEW_READY.
- Codex is the only role that may set APPROVED, CHANGES_REQUESTED, REJECTED, or MERGED.
- A PR may start only when every dependency listed in the ticket is APPROVED or MERGED on this board.
- After writing the implementation report and committing current PR changes, Claude Code must stop and wait for Codex review.
- Later PRs must not be read, implemented, committed, or status-updated without a new Codex handoff.

## Notes

- Skill Protocol Phase 1 is complete. PR-SKILL-001 through PR-SKILL-004 are merged.
- Runtime Phase 2 is planned. PR-RUNTIME-001 is the only ticket currently authorized for Claude Code.
- Use `cc-implementer` for one ticket at a time. Codex reviews each ticket before moving to the next.

## Blockers

- None currently.
