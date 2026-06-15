# PR-ANALYTICS-005 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

The PR is correctly docs-only and the updated command/interface docs mostly describe Phase 3 behavior accurately. However, the related skill protocol files were not synchronized, leaving stale runtime contracts for `scan-trap` and `panel-only`.

Because `PR-ANALYTICS-005` explicitly covers relevant `uzen-skills/skills/*/SKILL.md` when runtime behavior changes their contracts, these inconsistencies must be fixed before approval.

## Review Object

Base: `2091e6c` (`origin/agent/cc/pr-analytics-004-uzen-investor-panel-signals`)

Head: `ce371d6`

Diff command:

```bash
git diff origin/agent/cc/pr-analytics-004-uzen-investor-panel-signals...HEAD
```

## Spec Compliance

Fail

## Scope Compliance

Pass

## Acceptance Criteria Check

- [x] Docs are mostly Chinese-first.
- [x] Important analytical terms use Chinese labels with optional English in parentheses.
- [x] Docs do not claim UZI full parity.
- [x] Docs match current CLI command names and output paths in command docs.
- [x] `hoxit uzen --help` works.
- [ ] Relevant skill protocol docs match current runtime contracts.

## Test Evidence

```bash
.venv/bin/hoxit uzen --help
# command help rendered successfully

git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
# no output
```

## Issues

### Critical

None.

### Important

1. `uzen-skills/skills/deep-analysis/SKILL.md` still routes `scan-trap` to `trap_risk` and still omits the new Phase 3 analysis objects from the expected artifact schema.
   - Current stale text: command table says `scan-trap` primary section is `trap_risk`.
   - Current stale JSON sample includes `panel` and `trap_risk`, but not `market_risk`, `dcf`, `comps`, or panel `signals`/`vote_distribution`.
   - Required fix: update this protocol to reflect `market_risk` as the primary section, include the split `market_risk`/`trap_risk` shape, and include the Phase 3 analysis objects at least at the schema/contract level.

2. `uzen-skills/skills/trap-detector/SKILL.md` still describes outdated current output and execution flow.
   - It says missing core signal data marks risk level as `data_needed`, but current runtime uses `market_risk.level` as `low|medium|high` and `trap_risk.status` as `unsupported`.
   - It shows current schema as only `{ "level": "low", "flags": [...] }`, which no longer matches runtime.
   - It says `analyze_snapshot()` computes `_trap_risk()`, but current runtime computes `_market_risk()` plus unsupported `_trap_risk()`.
   - Required fix: make current schema match `analysis["market_risk"]` and `analysis["trap_risk"]`, and preserve UZI social-evidence requirements as deferred behavior.

3. `uzen-skills/skills/investor-panel/SKILL.md` still describes the old scalar-only panel as current behavior.
   - It still says current output is only `score`, `verdict`, and `reasons`.
   - It describes the signal schema as target rather than current foundation, with field names that do not match runtime (`investor_name`, `evidence`, `weight` versus runtime `name`, `group`, `score`, `reasoning`).
   - It says the first version uses lightweight deterministic scoring, not the current 5 deterministic investor archetypes.
   - Required fix: update current behavior and schema to match `signals` and `vote_distribution`, while still clearly saying this is not full UZI 65-investor parity.

### Minor

- `uzen-skills/commands/analyze-stock.md` uses compact placeholder arrays such as `"signals": ["..."]`; acceptable as an example, but clearer object-shaped samples would reduce ambiguity.
- `uzen-skills/README.md` still uses English-only signal labels inside a compact inline list. This is acceptable because labels are runtime enum values, but the Chinese gloss should remain nearby.

## Required Fixes for Claude Code

1. Update `uzen-skills/skills/deep-analysis/SKILL.md` for Phase 3 runtime contracts.
2. Update `uzen-skills/skills/trap-detector/SKILL.md` so current risk output matches `market_risk` and `trap_risk`.
3. Update `uzen-skills/skills/investor-panel/SKILL.md` so current panel output matches `signals` and `vote_distribution`.
4. Keep the docs Chinese-first where user-facing, and use bilingual labels only for important terms.
5. Do not change production code or tests for this fix unless needed to correct executable examples.
6. Rerun:

```bash
.venv/bin/hoxit uzen --help
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers
```

## Merge Decision

Do not merge until the Important issues are resolved.
