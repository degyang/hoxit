# PR-RUNTIME-004 Codex Review

Verdict: CHANGES_REQUESTED

Date: 2026-06-15
Branch: `agent/cc/pr-runtime-004-uzen-runtime-docs-sync`
Reviewed commit: current `HEAD` on branch
Base: `main` at `34db1d5`

## Review Scope

Reviewed the branch diff against `main`:

- `docs/INTERFACES.md`
- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`
- `docs/superpowers/status/PR-RUNTIME-004-implementation.md`
- `docs/superpowers/status/board.md`

This is a documentation-only PR, as required. No production code, tests, API devlog, or skill protocol files were modified.

## Findings

### 1. `scan-trap` command doc overclaims lockup input

Severity: Important

File: `uzen-skills/commands/scan-trap.md`

The doc says Data Providers calls 8 providers:

```text
quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger
```

That list matches current runtime. But the later Data Inputs section also says:

```text
Lockup expiry from hoxit.signals.lockup_expiry
```

Current `scan-trap` mode does not call `lockup`; lockup is currently wired for `analyze-stock` and `lhb-analyzer`, not `scan-trap`.

Required change:

- Remove lockup from `scan-trap` current Data Inputs, or move it to an "available in other modes / future runtime enhancement" note.
- Keep the current provider list aligned with `hoxit.uzen._MODE_SOURCES["scan-trap"]`.

### 2. `comps` command doc mentions iwencai fallback that is not wired into UZEN comps

Severity: Important

File: `uzen-skills/commands/comps.md`

The Notes section says:

```text
Use hoxit industry data first and iwencai fallback through `hoxit.iwencai` when needed.
```

Current `comps` mode calls only:

```text
quote, metrics, fundamentals, industry
```

There is no UZEN comps runtime call to `hoxit.iwencai` in `collect_snapshot()`.

Required change:

- Rewrite this as current behavior using `hoxit.signals.industry_comparison`.
- If iwencai peer fallback is desired later, mark it explicitly as deferred/not wired.

## Verification

Codex reran:

```bash
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers/status/PR-RUNTIME-004-implementation.md
.venv/bin/hoxit uzen --help
```

Result:

- `git diff --check`: passed with no output.
- CLI help displayed the expected `hoxit uzen` commands.

## Decision

CHANGES_REQUESTED.

The PR is close, but the docs must not claim unavailable runtime behavior. Fix the two current-behavior mismatches and update the implementation report before requesting review again.
