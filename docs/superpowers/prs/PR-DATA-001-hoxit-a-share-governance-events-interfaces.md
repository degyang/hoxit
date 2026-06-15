# PR-DATA-001: hoxit A股治理与事件接口

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-data-001-hoxit-a-share-governance-events-interfaces`

## Design

- `docs/superpowers/specs/2026-06-16-uzen-phase6-a-share-data-gap-review.md`
- `docs/superpowers/plans/2026-06-16-uzen-a-share-data-coverage-phase6.md`

## Goal

Add small reusable hoxit A-share data interfaces needed by UZEN Phase 6 before wiring them into UZEN.

## Scope

- Add hoxit functions for:
  - governance/ownership summary using iwencai `management` route where practical;
  - business/supply-chain summary using iwencai `business` route where practical;
  - event/catalyst summary using iwencai `event` route where practical.
- Place functions in existing modules that fit hoxit boundaries:
  - `fundamentals.py` for governance/business if appropriate;
  - `signals.py` or `news.py` for event/catalyst if appropriate.
- Add CLI subcommands only if they match existing hoxit CLI structure and remain small.
- Add unit tests with injected/mocked iwencai responses.
- Append `docs/API_DEVLOG.md` with source routes, behavior, verification, and follow-up risks.

## Out of Scope

- No UZEN runtime wiring in this PR.
- No new provider dependency.
- No live network requirement in unit tests.
- No social trap conclusion.
- No LHB seat classification.

## Must Not Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `uzen-skills/`
- Later PR tickets

## Acceptance Criteria

- [ ] New functions return `dict` or `list[dict]` only.
- [ ] Network IO is injectable or uses existing iwencai injectable helpers.
- [ ] Missing/empty iwencai rows return neutral empty structures, not crashes.
- [ ] CLI additions, if any, follow existing argparse structure.
- [ ] Unit tests cover normal rows, empty rows, and malformed row tolerance.
- [ ] `docs/API_DEVLOG.md` records interface additions.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_fundamentals.py tests/test_signals.py tests/test_news.py tests/test_cli.py -v
.venv/bin/hoxit --help
git diff --check -- hoxit tests docs
```

## Dependencies

Depends on Phase 5 merged to `main`.

## Stop Condition

After implementation, verification, implementation report, commit, and push, stop for Codex review. Do not begin PR-DATA-002.

## Rollback Notes

Revert the PR commit. UZEN remains on Phase 5 behavior.
