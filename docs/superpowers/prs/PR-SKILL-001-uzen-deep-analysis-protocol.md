# PR-SKILL-001: UZEN Deep Analysis Protocol

Owner: Claude Code
Status: TODO
Branch: `agent/cc/pr-skill-001-uzen-deep-analysis-protocol`
Depends on: none

## Goal

Rewrite `uzen-skills/skills/deep-analysis/SKILL.md` into the master A-share UZEN workflow protocol, adapted from UZI-Skill but honest about current hoxit capabilities.

## Scope

Allowed files:

- `uzen-skills/skills/deep-analysis/SKILL.md`
- `uzen-skills/README.md`
- `uzen-skills/AGENTS.md`
- `docs/superpowers/status/PR-SKILL-001-implementation.md`

Do not edit:

- `hoxit/`
- `tests/`
- `docs/API_DEVLOG.md`
- other `uzen-skills/skills/*/SKILL.md`

## Required Content

The rewritten skill must cover:

- A-share-only boundary;
- hoxit-first data boundary;
- role of the agent as analyst and protocol executor;
- command/mode routing for `analyze-stock`, `quick-scan`, `dcf`, `comps`, `panel-only`, `scan-trap`, and `lhb-analyzer`;
- execution order from input validation through artifact review;
- hard gates for missing code, unsupported market, missing output artifacts, and unsupported data;
- current capability vs deferred UZI parity;
- rule that raw hoxit data must not be fabricated;
- rule that qualitative judgment must be separated from raw data;
- current JSON/Markdown output contract;
- relationship to specialized skills.

## Acceptance Criteria

- `deep-analysis/SKILL.md` is no longer a placeholder.
- It gives cc and Codex enough protocol detail to run A-share UZEN work consistently.
- It does not claim full UZI parity.
- It does not instruct agents to use UZI's provider chain directly.
- It preserves hoxit's CLI-first workflow.
- Implementation report records summary, files changed, verification command, and any deferred gaps.

## Verification

Run:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-001-implementation.md
```

## Stop Condition

After committing this PR, stop and wait for Codex review. Do not start PR-SKILL-002.
