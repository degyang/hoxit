# Agent Work Board

## Current Feature

UZEN Skills A-share migration

## Design

- Spec: `docs/superpowers/specs/2026-06-14-uzen-skills-design.md`
- Plan: `docs/superpowers/plans/2026-06-14-uzen-skills.md`
- Status: DESIGN_APPROVED / PR_PLANNED

## PR Queue

| PR | Title | Owner | Status | Branch | Review |
| --- | --- | --- | --- | --- | --- |
| PR-001 | UZEN Skill Skeleton | Claude Code | APPROVED | agent/cc/pr-001-uzen-skill-skeleton | docs/superpowers/reviews/PR-001-codex-review.md |
| PR-002 | UZEN Snapshot Aggregator | Claude Code | APPROVED | agent/cc/pr-002-uzen-snapshot-aggregator | docs/superpowers/reviews/PR-002-codex-review.md |
| PR-003 | UZEN Analysis And Markdown Renderer | Claude Code | APPROVED | agent/cc/pr-003-uzen-markdown-renderer | docs/superpowers/reviews/PR-003-codex-review.md |
| PR-004 | UZEN CLI Workflow | Claude Code | APPROVED | agent/cc/pr-004-uzen-cli-workflow | docs/superpowers/reviews/PR-004-codex-review.md |
| PR-005 | UZEN Mode Profiles | Claude Code | TODO | agent/cc/pr-005-uzen-mode-profiles | - |
| PR-006 | UZEN Interface Documentation | Claude Code | TODO | agent/cc/pr-006-uzen-interface-docs | - |

## Status Values

TODO -> IN_PROGRESS -> REVIEW_READY -> CHANGES_REQUESTED -> APPROVED -> MERGED

## Workflow Gates

- Claude Code may move only the current assigned PR from TODO/CHANGES_REQUESTED to IN_PROGRESS and then REVIEW_READY.
- Codex is the only role that may set APPROVED, CHANGES_REQUESTED, REJECTED, or MERGED.
- A PR may start only when every dependency listed in the ticket is APPROVED or MERGED on this board.
- After writing the implementation report and committing current PR changes, Claude Code must stop and wait for Codex review.
- Later PRs must not be read, implemented, committed, or status-updated without a new Codex handoff.

## Notes

- Execute tickets in order. PR-001 is documentation/skeleton only. PR-002 starts production code.
- Use `cc-implementer` for one ticket at a time. Codex reviews each ticket before moving to the next.

## Blockers

- None currently.
