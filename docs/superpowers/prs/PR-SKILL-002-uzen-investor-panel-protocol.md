# PR-SKILL-002: UZEN Investor Panel Protocol

Owner: Claude Code
Status: TODO
Branch: `agent/cc/pr-skill-002-uzen-investor-panel-protocol`
Depends on: PR-SKILL-001 approved or merged

## Goal

Rewrite `uzen-skills/skills/investor-panel/SKILL.md` so it defines an A-share investor-panel protocol instead of only pointing at `hoxit uzen panel-only`.

## Scope

Allowed files:

- `uzen-skills/skills/investor-panel/SKILL.md`
- `uzen-skills/commands/panel-only.md`
- `docs/superpowers/status/PR-SKILL-002-implementation.md`

Do not edit:

- `hoxit/`
- `tests/`
- other skill files unless Codex explicitly expands scope.

## Required Content

The rewritten protocol must cover:

- current lightweight hoxit panel behavior;
- target investor signal schema;
- `pass`, `fail`, `neutral`, and `data_needed` semantics;
- score, confidence, evidence, and reasoning fields;
- A-share data inputs available from hoxit;
- explicit statement that full UZI 65-investor parity is deferred;
- recommended first deterministic investor groups for future runtime work.

## Acceptance Criteria

- The skill no longer implies that current `panel-only` equals UZI's full investor panel.
- The target schema is concrete enough for later implementation and tests.
- Unsupported fields are described as `data_needed` or deferred, not invented.
- Implementation report records summary, files changed, verification command, and deferred gaps.

## Verification

Run:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-002-implementation.md
```

## Stop Condition

After committing this PR, stop and wait for Codex review. Do not start PR-SKILL-003.
