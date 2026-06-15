# PR-ANALYTICS-003: UZEN Risk Model Split

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-analytics-003-uzen-risk-model-split`

## Design

`docs/superpowers/plans/2026-06-15-uzen-analytical-models-phase3.md`

## Goal

Separate deterministic market-data risk flags from unsupported future trap/social-risk evidence so `scan-trap` remains honest and A-share-safe.

## Scope

- Add `analysis["market_risk"]` for current market-data-based flags.
- Add `analysis["trap_risk"]` as a separate schema for social/manipulation evidence status.
- Keep backward compatibility where practical for existing consumers.
- Update Markdown risk wording so it does not imply social trap evidence.
- Add unit tests for both objects and Markdown wording.

## Out of Scope

- No social media scraping.
- No evidence URL collection.
- No new hoxit provider.
- No DCF, comps, or panel changes.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-ANALYTICS-003-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `pyproject.toml`
- `uzen-skills/`
- `docs/INTERFACES.md`
- later PR tickets

## Required Behavior

The risk output should include:

```python
"market_risk": {
    "level": "low" | "medium" | "high",
    "basis": "market_data",
    "flags": list[str],
},
"trap_risk": {
    "status": "unsupported" | "data_needed" | "computed",
    "basis": "social_evidence",
    "evidence": list[dict],
    "warnings": list[str],
}
```

Markdown should clearly say current checks are market-data checks unless social evidence exists.

## Acceptance Criteria

- [ ] `scan-trap` includes both `market_risk` and `trap_risk`.
- [ ] Markdown no longer presents market-data flags as social/manipulation proof.
- [ ] Existing tests that expect `trap_risk` are updated or compatibility-covered.
- [ ] No new network dependency is introduced.

## Test Requirements

- [ ] Add market-risk flag test.
- [ ] Add trap-risk unsupported/data-needed test.
- [ ] Add Markdown wording regression test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-ANALYTICS-002 approved or merged.

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

Revert the PR commit. The previous combined risk object can be restored without data model migration.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-ANALYTICS-002 review.
