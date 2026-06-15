# PR-SPINE-002: UZEN Synthesis Layer

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-spine-002-uzen-synthesis-layer`

## Design

`docs/superpowers/plans/2026-06-15-uzen-research-spine-phase5.md`

## Goal

Add deterministic `analysis["synthesis"]` so UZEN can express a concise stance, confidence, drivers, risks, conflicts, and followups from existing hoxit analysis only.

## Scope

- Add synthesis helper.
- Attach `analysis["synthesis"]` in `analyze_snapshot()`.
- Render compact `## 综合研判` Markdown section.
- Add tests for schema, deterministic content, data-needed behavior, and Markdown rendering.

## Out of Scope

- No agent-authored synthesis.
- No LLM calls.
- No new data provider.
- No report self-review.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-SPINE-002-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

`analysis["synthesis"]` shape:

```json
{
  "basis": "deterministic_hoxit_analysis",
  "stance": "bullish|neutral|bearish|data_needed",
  "confidence": "high|medium|low",
  "drivers": [],
  "risks": [],
  "conflicts": [],
  "followups": []
}
```

Synthesis must use only:

- `analysis["panel"]`
- `analysis["market_risk"]`
- `analysis["dcf"]`
- `analysis["comps"]`
- `analysis["lhb"]`
- `analysis["dimensions"]`
- `snapshot["data_quality"]`

## Acceptance Criteria

- [ ] JSON artifact includes `analysis["synthesis"]`.
- [ ] Synthesis does not fabricate facts outside existing analysis objects.
- [ ] Markdown includes `## 综合研判`.
- [ ] Markdown does not include raw dict repr.
- [ ] Existing tests pass.

## Test Requirements

- [ ] Add synthesis schema test.
- [ ] Add bullish/neutral/bearish or data-needed deterministic behavior tests as feasible from fixtures.
- [ ] Add Markdown synthesis section test.
- [ ] Add test that synthesis remains low confidence when data quality is incomplete.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-SPINE-001 approved or merged.

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Board row moved to REVIEW_READY
- [ ] Current branch committed
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert the PR commit. UZEN returns to Phase 5 dimension output without synthesis.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-SPINE-001 review.
