# PR-SKILL-003: UZEN Trap Detector Protocol

Owner: Claude Code
Status: TODO
Branch: `agent/cc/pr-skill-003-uzen-trap-detector-protocol`
Depends on: PR-SKILL-001 approved or merged

## Goal

Rewrite `uzen-skills/skills/trap-detector/SKILL.md` so it separates supported hoxit market-risk checks from deferred UZI-style social/manipulation trap evidence.

## Scope

Allowed files:

- `uzen-skills/skills/trap-detector/SKILL.md`
- `uzen-skills/commands/scan-trap.md`
- `docs/superpowers/status/PR-SKILL-003-implementation.md`

Do not edit:

- `hoxit/`
- `tests/`
- other skill files unless Codex explicitly expands scope.

## Required Content

The rewritten protocol must cover:

- distinction between `market_risk` and `trap_risk`;
- supported hoxit inputs such as block trades, margin data, holder changes, fund flow, concept heat, and LHB data;
- UZI-style social/manipulation evidence categories that remain deferred or data-needed;
- evidence URL and keyword requirements when trap evidence is available;
- output states for `clear`, `watch`, `risk`, and `data_needed`;
- no-fabrication rule for social sentiment and manipulation claims.

## Acceptance Criteria

- The skill no longer presents hoxit market-risk flags as full UZI trap detection.
- Missing social evidence is explicitly represented.
- The protocol is A-share-first and hoxit-first.
- Implementation report records summary, files changed, verification command, and deferred gaps.

## Verification

Run:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-003-implementation.md
```

## Stop Condition

After committing this PR, stop and wait for Codex review. Do not start PR-SKILL-004.
