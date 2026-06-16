# PR-DATA-002 Codex Review

## Verdict

APPROVED

## Summary

PR-DATA-002 wires the PR-DATA-001 interfaces into UZEN snapshot collection and data quality records. `UzenDataProvider` now has optional `governance`, `business`, and `event` callables; `default_provider()` connects them to hoxit; `analyze-stock` collects the new sources; other modes skip them with neutral defaults.

The prior review blocker is fixed. PR-DATA-001-style non-empty payloads with `status: "data_needed"` or `status: "missing"` are now recorded as `quality: "missing"` instead of `quality: "full"`, source dicts are preserved, and payload warnings are propagated into `data_quality.sources`.

## Review Object

Base:

`origin/agent/cc/pr-data-001-hoxit-a-share-governance-events-interfaces`

Head:

`HEAD` (`f9822c7 fix: data_needed payloads recorded as quality 'missing' not 'full'`)

Diff command:

```bash
git diff origin/agent/cc/pr-data-001-hoxit-a-share-governance-events-interfaces...HEAD
```

Files reviewed:

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/PR-DATA-002-implementation.md`
- `docs/superpowers/status/board.md`

## Spec Compliance

Pass.

- Pass: `UzenDataProvider` has optional `governance`, `business`, and `event` callables.
- Pass: `default_provider()` wires the PR-DATA-001 hoxit interfaces.
- Pass: `analyze-stock` collects the new sources.
- Pass: other modes skip the new sources.
- Pass: new sources have stable snapshot keys.
- Pass: `data_quality.sources` distinguishes `full`, `missing`, `error`, and `skipped`, including PR-DATA-001 `data_needed` payloads.
- Pass: no synthesis or Markdown behavior was changed.

## Scope Compliance

Pass.

The PR does not touch `hoxit/cli.py`, `docs/INTERFACES.md`, `uzen-skills/`, or later tickets. It stays within snapshot/data-quality wiring and focused tests.

## Acceptance Criteria Check

- [x] Snapshot JSON includes new source objects under stable keys.
- [x] Existing provider tests can omit new callables or use neutral defaults.
- [x] Mode profiles skip heavy sources where appropriate.
- [x] `data_quality.sources` distinguishes `full`, `missing`, `error`, and `skipped`.
- [x] Existing Phase 5 tests still pass.

## Test Evidence

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
```

Result: `128 passed`.

```bash
.venv/bin/hoxit uzen --help
```

Result: passed.

```bash
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

Result: passed.

Additional regression check:

```bash
.venv/bin/python -m pytest
```

Result: `241 passed, 26 skipped`.

## Issues

### Critical

None.

### Important

None.

Resolved from prior review:

- PR-DATA-001 `data_needed` payloads were previously recorded as `quality: "full"`. Commit `f9822c7` records those payloads as `quality: "missing"` and propagates payload warnings.

### Minor

None.

## Required Fixes for Claude Code

None.

## Merge Decision

Approved for the next PR to build on branch `agent/cc/pr-data-002-uzen-snapshot-data-coverage`.

Continue with PR-DATA-003 after this approval. Do not start PR-DATA-004 until PR-DATA-003 is reviewed.
