# PR-004 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

PR-004 adds `run_analysis()` artifact writing and wires a new `hoxit uzen ...` CLI group into the existing argparse structure. The implementation is largely aligned with hoxit conventions: parser setup follows the existing layer/action pattern, dispatch uses a delayed import of `run_analysis`, tests avoid network by using an injected provider for artifact writing, and no docs or external endpoints are changed.

One acceptance criterion is not yet protected by tests: CLI dispatch must call `run_analysis()` with `mode=args.action`. Current tests cover parser shape and direct `run_analysis()` behavior, but not `hoxit.cli.run()` dispatch.

## Review Object

Base: `origin/agent/cc/pr-003-uzen-markdown-renderer`

Head: `agent/cc/pr-004-uzen-cli-workflow`

Diff command:

```bash
git diff origin/agent/cc/pr-003-uzen-markdown-renderer...HEAD
```

Reviewed changed files:

- `docs/superpowers/prs/PR-004-uzen-cli-workflow.md`
- `docs/superpowers/status/PR-004-implementation.md`
- `hoxit/cli.py`
- `hoxit/uzen.py`
- `tests/test_cli.py`
- `tests/test_uzen.py`

## Spec Compliance

Pass with test gap.

The implementation adds the planned CLI workflow and artifact-writing function without implementing mode profiles, documentation, live tests, or new external endpoints.

## Scope Compliance

Pass.

No public docs, API devlog, `uzen-skills`, live endpoint tests, or mode-specific tuning were changed.

## Acceptance Criteria Check

- [x] `run_analysis()` writes JSON and Markdown artifacts.
- [x] `run_analysis()` returns artifact paths and the analyzed snapshot.
- [x] CLI parser handles all seven first-version commands.
- [ ] CLI dispatch calls `run_analysis()` with `mode=args.action` and relevant CLI arguments.
- [x] Tests use injected provider or parser-only assertions and do not hit network.

## hoxit CLI Structure Check

- [x] `uzen` is registered as a top-level layer, consistent with existing `market`, `reports`, `signals`, `valuation`, and `iwc` groups.
- [x] Subcommands use `dest="action"` like the rest of the CLI.
- [x] Dispatch uses a delayed import inside `run()`.
- [x] No optional data dependencies are imported at CLI module import time.
- [x] CLI result remains JSON-printable through existing `_print_json()`.

## Test Evidence

Implementation report records:

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -q
# Output: 12 passed

.venv/bin/python -m pytest -q
# Output: 97 passed, 26 skipped

git diff --check -- hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py
# Output: no whitespace errors
```

Codex independently reran:

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -q
.venv/bin/python -m pytest -q
git diff --check -- hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py
```

Results:

- `tests/test_uzen.py tests/test_cli.py`: `12 passed`
- full default suite: `97 passed, 26 skipped`
- diff check: no whitespace errors

## Issues

### Critical

None.

### Important

1. Missing test for `hoxit.cli.run()` dispatch into `hoxit.uzen.run_analysis()`.

   File: `tests/test_cli.py`

   The PR ticket explicitly requires “CLI dispatch calls `run_analysis()` with `mode=args.action`.” Current tests only parse CLI args. A regression in `run()` could pass these tests while breaking actual command execution or dropping `trade_date`/`output_dir`.

### Minor

None.

## Required Fixes for Claude Code

1. Add a focused no-network dispatch test in `tests/test_cli.py`. Example:

   ```python
   def test_cli_uzen_dispatch_calls_run_analysis(monkeypatch):
       from hoxit import cli, uzen

       calls = []

       def fake_run_analysis(code, **kwargs):
           calls.append((code, kwargs))
           return {"ok": True}

       monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)
       parser = cli.build_parser()
       args = parser.parse_args([
           "uzen",
           "lhb-analyzer",
           "600000",
           "--trade-date",
           "2026-06-14",
           "--output-dir",
           "tmp/reports",
       ])

       assert cli.run(args) == {"ok": True}
       assert calls == [
           (
               "600000",
               {
                   "mode": "lhb-analyzer",
                   "output_dir": "tmp/reports",
                   "trade_date": "2026-06-14",
               },
           )
       ]
   ```

2. Rerun:

   ```bash
   .venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -q
   .venv/bin/python -m pytest -q
   git diff --check -- hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py
   ```

3. Update `docs/superpowers/status/PR-004-implementation.md` with the added test evidence and mark PR-004 ready for review again.

## Merge Decision

Do not merge PR-004 until the Important issue is resolved.
