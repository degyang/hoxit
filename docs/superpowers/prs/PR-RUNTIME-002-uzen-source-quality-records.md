# PR-RUNTIME-002: UZEN Source Quality Records

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-runtime-002-uzen-source-quality-records`

## Design

`docs/superpowers/plans/2026-06-15-uzen-runtime-phase2.md`

## Goal

Add structured per-source quality records so UZEN can distinguish full, partial, missing, error, and skipped data.

## Scope

Extend `hoxit/uzen.py` data quality output while preserving existing `data_quality.complete` and `data_quality.warnings`.

## Out of Scope

- Do not change provider interfaces.
- Do not change CLI arguments.
- Do not rewrite Markdown rendering.
- Do not implement DCF/comps/panel runtime models.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/PR-RUNTIME-002-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `hoxit/signals.py`
- `docs/API_DEVLOG.md`
- `uzen-skills/skills/*/SKILL.md`

## Required Behavior

Add `snapshot["data_quality"]["sources"]` with records shaped like:

```json
{
  "quote": {
    "label": "quote",
    "quality": "full",
    "source": "provider.quote",
    "warnings": [],
    "required": true,
    "optional_missing": []
  }
}
```

Allowed quality values:

- `full`
- `partial`
- `missing`
- `error`
- `skipped`

Rules:

- Provider exceptions produce `error`.
- Empty required sources produce `missing`.
- Unsupported F10 status produces `partial`.
- Mode-skipped sources produce `skipped`.
- Skipped sources must not make top-level `complete` false.
- Keep top-level `warnings` for backward compatibility.

## Acceptance Criteria

- [ ] Per-source quality records exist for top-level sources and signal sources.
- [ ] Provider exceptions are visible in the relevant source quality record.
- [ ] Mode-skipped sources are marked `skipped`.
- [ ] F10 unsupported is marked `partial`, with warnings preserved.
- [ ] Existing tests expecting `data_quality.warnings` still pass.

## Test Requirements

- [ ] Test full source quality.
- [ ] Test provider exception quality is `error`.
- [ ] Test skipped source quality after PR-RUNTIME-001.
- [ ] Test F10 unsupported quality is `partial`.
- [ ] Test skipped sources do not make `complete` false by themselves.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers/status/PR-RUNTIME-002-implementation.md
```

## Dependencies

Depends on:

- PR-RUNTIME-001 APPROVED or MERGED

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Current PR status moved to REVIEW_READY
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update PR-RUNTIME-003 or any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert this PR to remove structured source quality records while preserving existing warning-only quality.

## Handoff Notes for Claude Code

Follow this ticket exactly. Do not expand scope. If PR-RUNTIME-001 is not approved or merged, stop and report the dependency blocker.
