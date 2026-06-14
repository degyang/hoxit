# PR-SKILL-004: UZEN LHB Analyzer Protocol

Owner: Claude Code
Status: TODO
Branch: `agent/cc/pr-skill-004-uzen-lhb-analyzer-protocol`
Depends on: PR-SKILL-001 approved or merged

## Goal

Rewrite `uzen-skills/skills/lhb-analyzer/SKILL.md` so it defines an A-share dragon-tiger-board reasoning protocol and identifies missing reusable hoxit APIs for later runtime parity.

## Scope

Allowed files:

- `uzen-skills/skills/lhb-analyzer/SKILL.md`
- `uzen-skills/commands/lhb-analyzer.md`
- `docs/superpowers/status/PR-SKILL-004-implementation.md`

Do not edit:

- `hoxit/`
- `tests/`
- other skill files unless Codex explicitly expands scope.

## Required Content

The rewritten protocol must cover:

- required input code and optional trade date;
- supported current hoxit LHB data boundary;
- target seat schema;
- institution vs hot-money classification;
- buy/sell seat interpretation;
- board and peer leadership comparison;
- fallback when only partial LHB data exists;
- explicit deferred list for seat database and peer ranking APIs if hoxit does not yet expose them.

## Acceptance Criteria

- The skill no longer only states the CLI command.
- It defines a concrete analysis contract for future implementation.
- It does not claim seat identity coverage unless hoxit data exists.
- Implementation report records summary, files changed, verification command, and deferred gaps.

## Verification

Run:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-004-implementation.md
```

## Stop Condition

After committing this PR, stop and wait for Codex review.
