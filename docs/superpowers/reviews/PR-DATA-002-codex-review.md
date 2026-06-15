# PR-DATA-002 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

PR-DATA-002 correctly wires the PR-DATA-001 interfaces into `UzenDataProvider`, `default_provider()`, analyze-stock mode sources, `collect_snapshot()`, and focused snapshot tests. It stays within the intended file scope and does not change synthesis or Markdown.

However, the current wiring uses `_map_or_skip()` unchanged for the new `governance`, `business`, and `event` sources. That helper marks any truthy dict as `quality: "full"`. PR-DATA-001's new interfaces return non-empty neutral dicts with `status: "data_needed"` on empty rows or provider errors they catch internally. As a result, a real no-data response from `governance_summary()`, `business_summary()`, or `event_summary()` will be recorded as `full` instead of `missing` or `partial/data_needed`. This violates the PR-DATA-002 acceptance criterion that `data_quality.sources` distinguishes `full`, `missing`, `error`, and `skipped`.

## Review Object

Base:

`origin/agent/cc/pr-data-001-hoxit-a-share-governance-events-interfaces`

Head:

`HEAD` (`2e8b9eb feat: wire governance/business/event into UZEN snapshot collection`)

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

Partial.

- Pass: `UzenDataProvider` has optional `governance`, `business`, and `event` callables.
- Pass: `default_provider()` wires the PR-DATA-001 hoxit interfaces.
- Pass: `analyze-stock` collects the new sources.
- Pass: other modes skip the new sources.
- Pass: no synthesis or Markdown behavior was changed.
- Fail: `data_quality.sources` can misclassify `status: "data_needed"` payloads as `quality: "full"`.

## Scope Compliance

Pass.

The PR does not touch `hoxit/cli.py`, `docs/INTERFACES.md`, `uzen-skills/`, or later tickets. The only non-code status issue is the board using `✅ REVIEW_READY` instead of the canonical `REVIEW_READY` enum.

## Acceptance Criteria Check

- [x] Snapshot JSON includes new source objects under stable keys.
- [x] Existing provider tests can omit new callables or use neutral defaults.
- [x] Mode profiles skip heavy sources where appropriate.
- [ ] `data_quality.sources` correctly distinguishes `full`, `missing`, `error`, and `skipped` for PR-DATA-001-style `data_needed` payloads.
- [x] Existing Phase 5 tests still pass.

## Test Evidence

```bash
.venv/bin/python -m pytest tests/test_fundamentals.py tests/test_signals.py tests/test_news.py tests/test_cli.py -v
```

Result: `45 passed`.

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
```

Result: `127 passed`.

```bash
.venv/bin/hoxit --help
```

Result: passed.

```bash
git diff --check -- hoxit tests docs
```

Result: passed.

Additional regression check:

```bash
.venv/bin/python -m pytest
```

Result: `233 passed, 26 skipped`.

## Issues

### Critical

None.

### Important

1. PR-DATA-001 `data_needed` payloads are marked as `quality: "full"` in UZEN.

   `fundamentals.governance_summary()`, `fundamentals.business_summary()`, and `signals.event_summary()` return non-empty dicts like:

   ```json
   {
     "status": "data_needed",
     "warnings": ["治理数据不足"]
   }
   ```

   PR-DATA-002 routes these through `_map_or_skip()`:

   ```python
   "governance": _map_or_skip("governance", provider.governance, code),
   "business": _map_or_skip("business", provider.business, code),
   "event": _map_or_skip("event", provider.event, code),
   ```

   `_map_or_skip()` currently treats any non-empty result as `quality: "full"`, so the actual no-data contract from PR-DATA-001 becomes a false full-quality source in `data_quality.sources`.

   Required behavior: if a mapping result has `status in {"data_needed", "missing"}` or equivalent neutral status, quality should be `missing` or another non-full value already supported by the project. Its warnings should be propagated into the source quality record.

### Minor

- Board status uses `✅ REVIEW_READY`; the board's own enum is `REVIEW_READY`. Codex can normalize this while recording the requested-changes verdict.

## Required Fixes for Claude Code

1. Update UZEN source quality handling for mapping-style source payloads so `status: "data_needed"` does not become `quality: "full"`.

2. Add a regression test where `governance`, `business`, and `event` return PR-DATA-001-style non-empty `data_needed` dicts and assert:

   - snapshot preserves the returned dict;
   - `data_quality.sources[<key>]["quality"]` is not `full`;
   - warnings from the payload appear in the source quality warnings.

3. Keep the fix scoped to PR-DATA-002. Do not change synthesis, Markdown, CLI, docs sync, or PR-DATA-003 behavior.

4. Re-run:

   ```bash
   .venv/bin/python -m pytest tests/test_uzen.py -v
   .venv/bin/hoxit uzen --help
   git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
   ```

5. Commit, push, and stop for Codex review.

## Merge Decision

Do not merge until `data_needed` source payloads are no longer recorded as `quality: "full"`.
