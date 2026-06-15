# PR-DATA-004: UZEN Data-Aware Synthesis And Markdown

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-data-004-uzen-data-aware-synthesis-markdown`

## Design

- `docs/superpowers/specs/2026-06-16-uzen-phase6-a-share-data-gap-review.md`
- `docs/superpowers/plans/2026-06-16-uzen-a-share-data-coverage-phase6.md`

## Goal

Make UZEN synthesis and Markdown consume the new A-share data coverage facts without fabricating unsupported research conclusions.

## Scope

- Extend `analysis["synthesis"]` drivers/risks/followups from new deterministic source summaries.
- Add compact Markdown bullets for governance, events, business/context, and LHB detail where data exists.
- Preserve mode-specific section visibility.
- Keep social/trap evidence wording explicit as unsupported unless evidence schema is populated by a real provider.
- Add tests for no raw dict rendering and non-fabrication boundaries.

## Out of Scope

- No new provider calls.
- No agent-authored narrative generation.
- No HTML rendering.
- No persona panel rewrite.
- No LHB seat identity classification.

## Must Not Change

- `hoxit/cli.py`
- Provider modules
- `uzen-skills/`
- Later PR tickets

## Acceptance Criteria

- [ ] Synthesis uses only existing snapshot/analysis objects.
- [ ] New data can produce concrete drivers, risks, or followups.
- [ ] Markdown renders human-readable Chinese summaries.
- [ ] Markdown has no raw dict/list repr.
- [ ] Unsupported social trap and LHB identity claims remain guarded.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on PR-DATA-003 approved or merged.

## Stop Condition

After implementation, verification, implementation report, commit, and push, stop for Codex review. Do not begin PR-DATA-005.

## Rollback Notes

Revert the PR commit. UZEN keeps enriched coverage objects without rendering/synthesis consumption.
