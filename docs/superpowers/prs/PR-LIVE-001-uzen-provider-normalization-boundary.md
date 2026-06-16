# PR-LIVE-001: UZEN Provider Normalization Boundary

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-001-uzen-provider-normalization-boundary`

## Goal

Introduce a deterministic UZEN provider normalization boundary so report logic consumes stable dict/list structures even when live hoxit providers return pandas DataFrame-like objects or nested provider mappings.

## Scope

- Add UZEN normalization helpers in `hoxit/uzen.py`.
- Normalize at least these live shapes:
  - quote mapping from hoxit quote providers.
  - finance DataFrame-like or dict.
  - concept dict `{total, boards, concept_tags}` and list forms.
  - dragon_tiger dict `{records, seats, institution}` and list forms.
  - empty/missing provider results without pandas truthiness errors.
- Preserve existing snapshot keys and backward compatibility.
- Add unit tests using fake live-shaped objects, no network.

## Out of Scope

- No new hoxit provider calls.
- No new external data source.
- No bank-specific metrics.
- No visual output.
- No broad refactor of UZEN analysis models.

## Files Likely To Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/API_DEVLOG.md`

## Must Not Change

- `hoxit/cli.py`
- provider modules except if a tiny compatibility alias is absolutely required and documented first.
- `uzen-skills/` docs.
- PR-LIVE-002 through PR-LIVE-005 ticket files.

## Acceptance Criteria

- `collect_snapshot()` does not fail when a provider returns a DataFrame-like object with `.empty` and ambiguous `__bool__`.
- Markdown rendering accepts concept dict and list forms.
- Markdown rendering accepts dragon_tiger dict `records` and list forms.
- Existing UZEN JSON and Markdown public structure remains compatible.
- Tests include realistic provider-shape fixtures.

## Required Tests

- Add unit tests for DataFrame-like finance.
- Add unit tests for concept dict normalization.
- Add unit tests for dragon_tiger dict normalization.
- Add regression test that no raw dict repr appears in Markdown for these shapes.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md
```

## Dependencies

Depends on `main` after Phase 6 and current live fixes.

## Definition Of Done

- Tests pass.
- `docs/API_DEVLOG.md` records live provider contract hardening.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-001-implementation.md`.
- Board marks PR-LIVE-001 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. UZEN returns to previous provider-shape handling.
