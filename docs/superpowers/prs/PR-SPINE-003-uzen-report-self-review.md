# PR-SPINE-003: UZEN Report Self Review

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-spine-003-uzen-report-self-review`

## Design

`docs/superpowers/plans/2026-06-15-uzen-research-spine-phase5.md`

## Goal

Add deterministic `analysis["report_review"]` checks so UZEN can audit its own JSON and Markdown artifact contract without using natural-language evaluation.

## Scope

- Add report review helper.
- Attach JSON-level review in analysis.
- Add Markdown-level checks in `run_analysis()` if needed.
- Test required sections, disclaimer, raw dict avoidance, unsupported feature wording, and mode section alignment.

## Out of Scope

- No LLM evaluator.
- No HTML validation.
- No new data provider.
- No synthesis behavior changes except consuming existing synthesis if useful.
- No docs sync outside implementation report and board status.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-SPINE-003-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

`analysis["report_review"]` shape:

```json
{
  "status": "passed|warnings",
  "checks": [
    {"name": "required_analysis_sections", "status": "passed", "warnings": []}
  ],
  "warnings": []
}
```

Checks should be deterministic and non-blocking in this PR.

## Acceptance Criteria

- [ ] JSON artifact includes `analysis["report_review"]`.
- [ ] Review checks required analysis sections.
- [ ] Review checks disclaimer presence where Markdown is available.
- [ ] Review checks raw dict repr avoidance where Markdown is available.
- [ ] Review does not fail report generation in this PR.
- [ ] Existing tests pass.

## Test Requirements

- [ ] Add report review schema test.
- [ ] Add required analysis sections test.
- [ ] Add Markdown disclaimer/raw dict check test.
- [ ] Add mode section alignment test.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- PR-SPINE-002 approved or merged.

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

Revert the PR commit. UZEN returns to synthesis output without report self-review.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-SPINE-002 review.
