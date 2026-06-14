# PR-002 Codex Review

## Verdict

APPROVED

## Summary

PR-002 adds the `hoxit.uzen` snapshot aggregation layer and focused unit tests. The implementation stays within the ticket scope: no CLI integration, no Markdown rendering, no mode-specific behavior, and no new external endpoint behavior.

The new code follows hoxit's current structural conventions: third-party and data modules are imported lazily inside `default_provider()`, execution is testable through injected callables, default tests do not hit the network, and the public function returns a plain dictionary.

## Review Object

Base: `origin/agent/cc/pr-001-uzen-skill-skeleton`

Head: `agent/cc/pr-002-uzen-snapshot-aggregator`

Diff command:

```bash
git diff origin/agent/cc/pr-001-uzen-skill-skeleton...HEAD
```

Reviewed changed files:

- `docs/superpowers/prs/PR-002-uzen-snapshot-aggregator.md`
- `docs/superpowers/status/PR-002-implementation.md`
- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Spec Compliance

Pass.

The implementation adds the deterministic execution layer described by the approved design without moving into later PR responsibilities.

## Scope Compliance

Pass.

The branch diff for PR-002 only changes the ticket status, implementation report, `hoxit/uzen.py`, and `tests/test_uzen.py`.

## Acceptance Criteria Check

- [x] `collect_snapshot("600000", provider=fake_provider)` returns `market == "A"`.
- [x] Snapshot contains quote, bars, metrics, valuation, fundamentals, finance, F10, reports, news, filings, and signals.
- [x] Provider calls are injectable and unit tests do not hit the network.
- [x] F10 unsupported warnings are included in `data_quality.warnings`.
- [x] Exceptions from provider functions are converted to warnings and default empty data.

## hoxit Structure Check

- [x] No top-level imports of `requests`, `pandas`, `mootdx`, or other optional data dependencies.
- [x] Existing hoxit modules are imported lazily inside `default_provider()`.
- [x] Network-facing behavior is reachable through injectable provider callables.
- [x] Return shape is a plain `dict`.
- [x] No CLI changes were made in this PR, preserving the existing argparse command structure for PR-004.

## Test Evidence

Implementation report records:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
# Output: 3 passed

.venv/bin/python -m pytest -q
# Output: 93 passed, 26 skipped

git diff --check -- hoxit/uzen.py tests/test_uzen.py
# Output: no whitespace errors
```

Codex independently reran:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
.venv/bin/python -m pytest -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

Results:

- `tests/test_uzen.py`: `3 passed`
- full default suite: `93 passed, 26 skipped`
- diff check: no whitespace errors

## Issues

### Critical

None.

### Important

None.

### Minor

None.

## Required Fixes for Claude Code

None.

## Merge Decision

Approved for merge or for moving to PR-003 according to the project workflow.
