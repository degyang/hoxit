# PR-001: UZEN Skill Skeleton

## Owner

Claude Code

## Status

APPROVED

## Branch

`agent/cc/pr-001-uzen-skill-skeleton`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Create the `uzen-skills/` documentation and skill-command skeleton for the A-share-only first version.

## Scope

- Create `uzen-skills/` directories.
- Add README and AGENTS guardrails.
- Add command docs for the first-version commands.
- Add skill docs for deep analysis, investor panel, LHB analyzer, and trap detector.
- Add `.gitkeep` files for cache and reports.

## Out of Scope

- No production Python code.
- No CLI integration.
- No copied UZI provider chain.
- No HTML/assets/share-card migration.
- No non-A-share workflows.

## Files Likely to Change

- `uzen-skills/README.md`
- `uzen-skills/AGENTS.md`
- `uzen-skills/commands/analyze-stock.md`
- `uzen-skills/commands/quick-scan.md`
- `uzen-skills/commands/dcf.md`
- `uzen-skills/commands/comps.md`
- `uzen-skills/commands/panel-only.md`
- `uzen-skills/commands/scan-trap.md`
- `uzen-skills/commands/lhb-analyzer.md`
- `uzen-skills/skills/deep-analysis/SKILL.md`
- `uzen-skills/skills/investor-panel/SKILL.md`
- `uzen-skills/skills/lhb-analyzer/SKILL.md`
- `uzen-skills/skills/trap-detector/SKILL.md`
- `uzen-skills/cache/.gitkeep`
- `uzen-skills/reports/.gitkeep`

## Must Not Change

- `hoxit/`
- `tests/`
- `docs/API_DEVLOG.md`
- `docs/INTERFACES.md`

## Acceptance Criteria

- [ ] `uzen-skills/` exists with all files listed above.
- [ ] Docs mention all first-version commands: `analyze-stock`, `quick-scan`, `dcf`, `comps`, `panel-only`, `scan-trap`, `lhb-analyzer`.
- [ ] Docs explicitly defer HTML, share images, Playwright repair, remote hosting, cross-market support, portfolio commands, and full UZI parity.
- [ ] Docs forbid one-off scrapers under `uzen-skills`.

## Test Requirements

- [ ] No automated tests required for this documentation-only PR.
- [ ] Run file listing verification.

## Verification Commands

```bash
find uzen-skills -maxdepth 4 -type f | sort
git diff --check -- uzen-skills
```

## Dependencies

Depends on:

- Approved design: `docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Definition of Done

- [ ] Skeleton complete.
- [ ] Verification commands pass.
- [ ] Commit created on branch `agent/cc/pr-001-uzen-skill-skeleton`.
- [ ] Implementation report written to `docs/superpowers/status/PR-001-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove only `uzen-skills/` skeleton files.

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Handoff Notes for Claude Code

Follow Task 1 in `docs/superpowers/plans/2026-06-14-uzen-skills.md`. Do not implement Python behavior in this PR.
