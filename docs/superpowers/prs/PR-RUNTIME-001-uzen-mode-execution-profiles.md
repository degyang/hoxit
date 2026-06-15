# PR-RUNTIME-001: UZEN Mode Execution Profiles

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-runtime-001-uzen-mode-execution-profiles`

## Design

`docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`

## Goal

Make `hoxit uzen <mode>` control which provider calls run, instead of only recording mode metadata.

## Scope

Implement mode-specific source selection in `hoxit/uzen.py` while keeping the JSON source keys stable.

## Out of Scope

- Do not redesign `UzenDataProvider`.
- Do not add new external data APIs.
- Do not change CLI arguments.
- Do not rewrite Markdown rendering.
- Do not add DCF, comps, investor persona, or LHB seat analysis logic.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/PR-RUNTIME-001-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `hoxit/signals.py`
- `hoxit/market.py`
- `docs/API_DEVLOG.md`
- `uzen-skills/skills/*/SKILL.md`

## Required Behavior

Add an internal mode execution profile map for:

- `analyze-stock`: full current call graph.
- `quick-scan`: quote, metrics, valuation, fundamentals, concept, fund_flow, and lightweight risk context only.
- `panel-only`: quote, metrics, valuation, fundamentals, finance.
- `scan-trap`: quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger.
- `lhb-analyzer`: quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup.
- `dcf`: quote, metrics, valuation, fundamentals, finance.
- `comps`: quote, metrics, fundamentals, industry.

Skipped top-level sources must still exist with neutral defaults:

- mapping-like sources: `{}`
- list-like sources: `[]`
- skipped signal keys: `[]`

## Acceptance Criteria

- [ ] `quick-scan` no longer calls heavy providers such as reports and filings.
- [ ] `analyze-stock` retains the full current provider coverage.
- [ ] Focused modes call only their required provider groups.
- [ ] Existing JSON source keys remain present.
- [ ] Existing CLI behavior and artifact paths remain compatible.
- [ ] Unknown mode falls back to `analyze-stock` behavior.

## Test Requirements

- [ ] Add a call-recording fake provider to `tests/test_uzen.py`.
- [ ] Test skipped providers are not called for `quick-scan`.
- [ ] Test `analyze-stock` calls full provider coverage.
- [ ] Test `panel-only`, `scan-trap`, `lhb-analyzer`, `dcf`, and `comps` call the expected subsets.
- [ ] Test skipped sources use stable neutral defaults.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-001-implementation.md
```

## Dependencies

Depends on:

- PR-SKILL-001 MERGED
- PR-SKILL-002 MERGED
- PR-SKILL-003 MERGED
- PR-SKILL-004 MERGED

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Current PR status moved to REVIEW_READY
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update PR-RUNTIME-002 or any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert this PR to restore the current behavior where all modes run the full provider call graph.

## Handoff Notes for Claude Code

Follow this ticket exactly. Do not expand scope. Before starting, confirm dependencies are MERGED in `docs/superpowers/status/board.md`. If blocked, write a blocker report instead of changing architecture.
