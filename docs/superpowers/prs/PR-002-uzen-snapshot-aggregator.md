# PR-002: UZEN Snapshot Aggregator

## Owner

Claude Code

## Status

APPROVED

## Branch

`agent/cc/pr-002-uzen-snapshot-aggregator`

## Design

`docs/superpowers/specs/2026-06-14-uzen-skills-design.md`

## Plan

`docs/superpowers/plans/2026-06-14-uzen-skills.md`

## Goal

Add the deterministic `hoxit.uzen` snapshot collection layer with injectable data providers and no live-network default tests.

## Scope

- Create `hoxit/uzen.py`.
- Create `tests/test_uzen.py`.
- Add `UzenDataProvider`, `default_provider()`, `collect_snapshot()`, and safe-call behavior.
- Include under-documented existing signal helpers in the provider contract.
- Preserve structured F10 unsupported warnings without failing the whole snapshot.

## Out of Scope

- CLI integration.
- Markdown rendering.
- Mode-specific behavior.
- New external data endpoints.
- `uzen-skills/` docs edits unless PR-001 left a typo that blocks tests.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Must Not Change

- `hoxit/cli.py`
- `docs/INTERFACES.md`
- `docs/API_DEVLOG.md`
- `uzen-skills/`

## Acceptance Criteria

- [ ] `collect_snapshot("600000", provider=fake_provider)` returns `market == "A"`.
- [ ] Snapshot contains quote, bars, metrics, valuation, fundamentals, finance, F10, reports, news, filings, and signals.
- [ ] Provider calls are injectable and unit tests do not hit the network.
- [ ] F10 unsupported warnings are included in `data_quality.warnings`.
- [ ] Exceptions from provider functions are converted to warnings and default empty data.

## Test Requirements

- [ ] Add `tests/test_uzen.py`.
- [ ] Cover normal snapshot assembly.
- [ ] Cover F10 unsupported warning.
- [ ] Cover one provider exception path.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

## Dependencies

Depends on:

- PR-001 approved or merged.

## Definition of Done

- [ ] Implementation complete.
- [ ] Tests pass.
- [ ] Verification commands pass.
- [ ] Commit created on branch `agent/cc/pr-002-uzen-snapshot-aggregator`.
- [ ] Implementation report written to `docs/superpowers/status/PR-002-implementation.md`.
- [ ] Codex review approved.

## Rollback Notes

Revert this PR to remove `hoxit/uzen.py` and `tests/test_uzen.py` snapshot coverage.

## Handoff Notes for Claude Code

Follow Task 2 in the implementation plan. Use TDD: write failing tests first, then implement only enough snapshot behavior to pass.
