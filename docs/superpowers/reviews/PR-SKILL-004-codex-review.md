# PR-SKILL-004 Codex Review

Verdict: CHANGES_REQUESTED

Date: 2026-06-15
Branch: `agent/cc/pr-skill-004-uzen-lhb-analyzer-protocol`
Reviewed commit: `6b0b6f2 docs: rewrite uzen lhb analyzer protocol`
Base: `main` at `d856dfd`

## Review Scope

Reviewed the branch diff against `main`:

- `uzen-skills/skills/lhb-analyzer/SKILL.md`
- `uzen-skills/commands/lhb-analyzer.md`
- `docs/superpowers/status/PR-SKILL-004-implementation.md`

This matches the PR ticket scope. No production code, tests, or other skill files were modified.

## Findings

### 1. Current command behavior overclaims `daily_dragon_tiger` wiring

Severity: Important

Files:

- `uzen-skills/skills/lhb-analyzer/SKILL.md`
- `uzen-skills/commands/lhb-analyzer.md`

The docs list `hoxit.signals.daily_dragon_tiger` as part of current LHB data inputs/current behavior. `daily_dragon_tiger` exists in `hoxit.signals`, but current `hoxit.uzen.default_provider()` does not expose it and `collect_snapshot()` does not collect it for `lhb-analyzer`.

Current UZEN wiring only collects:

- `signals.dragon_tiger_board` through provider field `dragon_tiger`
- `signals.lockup_expiry`
- `signals.block_trade`
- `signals.margin_trading`
- `signals.baidu_fund_flow_history`
- `signals.industry_comparison`

Because this PR's purpose is to make the skill protocol honest about current capability versus future parity, the command docs must not say the current `hoxit uzen lhb-analyzer` path uses market-wide daily LHB data unless the runtime actually does.

Required change:

- In both `SKILL.md` and `commands/lhb-analyzer.md`, distinguish:
  - currently wired into `hoxit.uzen lhb-analyzer`;
  - available somewhere in hoxit but not yet wired into UZEN;
  - deferred APIs.
- Move `daily_dragon_tiger` into the "available in hoxit, not yet wired into UZEN" or future-wiring section unless production code is explicitly changed in a later runtime PR.

### 2. Implementation report still has minor metadata issues

Severity: Minor

Files:

- `docs/superpowers/status/PR-SKILL-004-implementation.md`

The report date is `2026-06-14`, while this review is on `2026-06-15`, and the report does not record the actual commit hash `6b0b6f2`.

Required change:

- Update the implementation report with the actual commit hash.
- Correct the date if this report was produced in the current session on 2026-06-15.

## Verification

Codex reran:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-004-implementation.md
```

Result: passed with no output.

## Decision

CHANGES_REQUESTED.

The protocol is close, but it must accurately separate current UZEN command behavior from hoxit APIs that exist but are not wired into UZEN yet.
