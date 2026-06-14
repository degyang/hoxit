# UZEN Skill Protocol Phase 1 Plan

Date: 2026-06-15
Status: ready for PR execution

## Goal

Bring the UZEN skill instruction layer closer to UZI-Skill for A-share use, without changing production hoxit code in this phase.

## Non-Goals

- No production changes under `hoxit/`.
- No test changes unless a doc lint command requires them.
- No provider-chain migration from UZI.
- No claim of full 65-investor panel parity.
- No non-A-share support.
- No HTML/share-card implementation.

## PR Sequence

| PR | Title | Dependency | Purpose |
| --- | --- | --- | --- |
| PR-SKILL-001 | Deep Analysis Protocol | None | Establish master A-share workflow and gates |
| PR-SKILL-002 | Investor Panel Protocol | PR-SKILL-001 | Define panel schema and current-vs-target behavior |
| PR-SKILL-003 | Trap Detector Protocol | PR-SKILL-001 | Separate supported market risk from social trap evidence |
| PR-SKILL-004 | LHB Analyzer Protocol | PR-SKILL-001 | Define LHB seat and board reasoning contract |

## Execution Rules For Claude Code

- Implement exactly one PR ticket per run.
- Use the branch named in the ticket.
- Stay inside the ticket's file scope.
- Write or update the implementation report named in the ticket.
- Commit the PR work.
- Stop after the commit and wait for Codex review.
- Do not inspect, implement, or status-update later PR tickets without a new Codex handoff.

## Verification

Because this phase is documentation/protocol only, required verification is:

```bash
git diff --check -- uzen-skills docs/superpowers
```

If cc edits Markdown tables, also visually inspect the rendered source for broken table structure.
