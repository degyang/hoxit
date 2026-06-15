# PR-REPORT-002: UZEN Agent Analysis Envelope

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-report-002-uzen-agent-analysis-envelope`

## Design

`docs/superpowers/plans/2026-06-15-uzen-report-envelope-phase4.md`

## Goal

Add an optional declared agent-analysis envelope so qualitative judgment can be included without modifying raw data or deterministic hoxit analysis.

## Scope

- Add `analysis["agent_analysis"]` with `provided` and `not_provided` states.
- Add optional `agent_analysis` parameter to `run_analysis()`.
- Add `--agent-analysis <json-file>` to UZEN CLI subcommands.
- Render a compact Markdown section only when an envelope is provided.
- Add tests for default absence, provided envelope, invalid file/JSON, and artifact output.

## Out of Scope

- No LLM calls.
- No prompt generation.
- No mutation of `sources`, `data_quality`, DCF, Comps, panel, or risk objects.
- No non-JSON formats.

## Files Likely to Change

- `hoxit/uzen.py`
- `hoxit/cli.py`
- `tests/test_uzen.py`
- `tests/test_cli.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-REPORT-002-implementation.md`

## Must Not Change

- `docs/INTERFACES.md`
- `uzen-skills/`
- later PR tickets

## Required Behavior

Default envelope:

```json
{
  "status": "not_provided",
  "basis": "agent_qualitative_input",
  "thesis": "",
  "assumptions": [],
  "conflicts": [],
  "followups": [],
  "warnings": []
}
```

Provided envelope:

```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "string",
  "assumptions": ["string"],
  "conflicts": ["string"],
  "followups": ["string"],
  "warnings": []
}
```

Invalid JSON or non-object JSON must fail clearly and not create misleading artifacts.

## Acceptance Criteria

- [ ] `run_analysis()` works unchanged when no envelope is provided.
- [ ] JSON artifact includes `analysis["agent_analysis"]`.
- [ ] Markdown includes agent analysis only when provided.
- [ ] CLI accepts `--agent-analysis` for all UZEN subcommands.
- [ ] Invalid JSON input is tested.

## Test Requirements

- [ ] Add unit tests for default and provided envelopes.
- [ ] Add CLI parser/run tests for valid and invalid `--agent-analysis`.
- [ ] Keep tests network-free.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py docs/superpowers
```

## Dependencies

Depends on:

- PR-REPORT-001 approved or merged.

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

Revert the PR commit. Existing UZEN runs should return to deterministic-only artifacts.

## Handoff Notes for Claude Code

Do not start this ticket until Codex explicitly assigns it after PR-REPORT-001 review.
