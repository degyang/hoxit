# PR-004: UZEN CLI Workflow

## Owner

Claude Code

## Status

REVIEW_READY

## Branch

`agent/cc/pr-004-uzen-cli-workflow`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Expose UZEN through `hoxit uzen ...` commands and write JSON/Markdown artifacts.

## Scope

- Add `run_analysis()` to `hoxit/uzen.py`.
- Add `uzen` parser group to `hoxit/cli.py`.
- Add CLI dispatch to `hoxit.cli.run()`.
- Add parser tests and artifact-writing tests.

## Out of Scope

- Mode-specific tuning beyond passing the mode through.
- Documentation updates.
- New external endpoints.
- Live endpoint tests.

## Files Likely to Change

- `hoxit/uzen.py`
- `hoxit/cli.py`
- `tests/test_uzen.py`
- `tests/test_cli.py`

## Must Not Change

- `docs/INTERFACES.md`
- `docs/API_DEVLOG.md`
- `uzen-skills/`

## Required Behavior

The CLI must support:

- `hoxit uzen analyze-stock <code>`
- `hoxit uzen quick-scan <code>`
- `hoxit uzen dcf <code>`
- `hoxit uzen comps <code>`
- `hoxit uzen panel-only <code>`
- `hoxit uzen scan-trap <code>`
- `hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD`

Each command accepts `--output-dir` and writes `<code>-<mode>.json` and `<code>-<mode>.md`.

## Acceptance Criteria

- [ ] `run_analysis()` writes JSON and Markdown artifacts.
- [ ] `run_analysis()` returns artifact paths and the analyzed snapshot.
- [ ] CLI parser handles all seven first-version commands.
- [ ] CLI dispatch calls `run_analysis()` with `mode=args.action`.
- [ ] Tests use injected provider or parser-only assertions and do not hit network.

## Test Requirements

- [ ] Extend `tests/test_uzen.py` for artifact writing.
- [ ] Extend `tests/test_cli.py` for parser coverage.
- [ ] Run existing CLI tests.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -q
.venv/bin/python -m pytest -q
git diff --check -- hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py
```

## Dependencies

Depends on:

- PR-003 approved or merged.

## Definition of Done

- [ ] Implementation complete.
- [ ] Tests pass.
- [ ] Verification commands pass.
- [ ] Commit created on branch `agent/cc/pr-004-uzen-cli-workflow`.
- [ ] Implementation report written to `docs/superpowers/status/PR-004-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove CLI exposure and artifact-writing behavior while leaving snapshot and renderer functions intact if needed.

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Handoff Notes for Claude Code

Follow Task 4 in the implementation plan. Do not add docs in this PR; PR-006 handles public docs.
