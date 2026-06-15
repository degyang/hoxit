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

### 3. UZEN skill-facing docs should remain Chinese-first

Severity: Important

Files:

- `uzen-skills/README.md`
- `uzen-skills/commands/*.md`

The migrated UZEN skill docs are user-facing workflow instructions. They should follow the original UZI/UZEN style: Chinese first, with important terms and principles optionally shown as Chinese-English pairs.

Required change:

- Keep command docs and UZEN README primarily in Chinese.
- Important terms may use bilingual labels, for example `数据质量（Data Quality）`, `模式执行配置（Mode Execution Profile）`, `延迟能力（Deferred Capability）`.
- Do not leave broad sections as English-only prose when they are user-facing UZEN skill docs.

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

The PR is close, but the docs must not claim unavailable runtime behavior and should preserve Chinese-first UZEN skill documentation style. Fix the current-behavior mismatches, convert user-facing command/README prose to Chinese-first wording, and update the implementation report before requesting review again.

## Second Review

Date: 2026-06-15

Reviewed current branch state after the user reported changes complete.

Status:

- The `scan-trap` lockup overclaim is fixed.
- The `comps` iwencai fallback overclaim is fixed.
- The Chinese-first documentation requirement is not fixed.

Blocking remaining issue:

- `uzen-skills/README.md` and `uzen-skills/commands/*.md` still contain broad English-only user-facing sections such as `Runtime Behavior`, `Mode Execution Profiles`, `Data Providers`, `Current Behavior`, `Limitations`, and English prose bodies.

Required change:

- Convert UZEN README and command docs to Chinese-first wording.
- Keep command names and code identifiers in English where they are literal CLI/API names.
- Use bilingual terms only where helpful, for example:
  - `运行时行为（Runtime Behavior）`
  - `模式执行配置（Mode Execution Profile）`
  - `数据质量（Data Quality）`
  - `延迟能力（Deferred Capability）`
- Update the implementation report to mention this language-style fix.

Verdict remains: CHANGES_REQUESTED.

## Third Review

Date: 2026-06-15

Reviewed current branch state after the second reported fix.

Status:

- The `scan-trap` lockup overclaim remains fixed.
- The `comps` iwencai fallback overclaim remains fixed.
- Most prose in `uzen-skills/README.md` and `uzen-skills/commands/*.md` has been converted to Chinese-first wording.

Blocking remaining issue:

- Several user-facing command document headings remain English-only, especially `Data Providers` and `Mode Profile` across `uzen-skills/commands/*.md`.

Required change:

- Convert these headings to Chinese-first or bilingual labels, for example:
  - `## 数据提供方（Data Providers）`
  - `## 模式配置（Mode Profile）`
- Keep literal provider names, CLI commands, JSON keys, and mode names in English.
- Update the implementation report to mention the heading cleanup.

Verification rerun:

```bash
git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers/status/PR-RUNTIME-004-implementation.md
.venv/bin/hoxit uzen --help
```

Result:

- `git diff --check`: passed with no output.
- CLI help displayed the expected `hoxit uzen` commands.

Verdict remains: CHANGES_REQUESTED.
