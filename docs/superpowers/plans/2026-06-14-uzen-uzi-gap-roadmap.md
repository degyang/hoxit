# UZEN/UZI Gap Roadmap

Date: 2026-06-14
Status: draft for review

## Goal

Convert the UZI-Skill gap audit into an executable, reviewable roadmap for hoxit/UZEN.

This roadmap assumes the merged UZEN v1 is the stable baseline and should not be discarded. The next work should improve semantic correctness and report usefulness before attempting deep UZI parity.

## Non-Goals

- Do not import UZI's provider chain directly into hoxit.
- Do not add one-off scrapers under `uzen-skills/`.
- Do not add non-A-share support in this phase.
- Do not implement HTML/share images before Markdown and JSON contracts are stable.
- Do not claim 65-investor panel parity until the rule/persona layer exists.

## Milestone 0: Documentation Truth Fix

Purpose: make the merged project state and product language honest.

### PR-GAP-001: Update Status And Scope Language

Goal:

- Update `docs/superpowers/status/uzen-final-handoff.md` from approved branch state to merged main state.
- Update `uzen-skills/README.md` and command docs to mark placeholder capabilities explicitly.

Scope:

- Clarify that `panel-only`, `dcf`, `comps`, `scan-trap`, and `lhb-analyzer` are first-version hoxit-native approximations.
- Keep command names unchanged.
- Do not change runtime behavior.

Acceptance:

- Docs no longer imply UZI parity.
- Docs distinguish JSON data artifact from Markdown human report.
- `git diff --check` passes.

## Milestone 1: Mode Semantics

Purpose: make `quick-scan` and focused modes actually change execution behavior.

### PR-GAP-002: Add Mode Execution Profiles

Goal:

- Replace metadata-only `_mode_profile()` with a profile that controls provider calls and report sections.

Scope:

- Add an internal profile structure in `hoxit/uzen.py`.
- Implement call selection for:
  - `quick-scan`
  - `analyze-stock`
  - `panel-only`
  - `scan-trap`
  - `lhb-analyzer`
  - `dcf`
  - `comps`
- Keep provider interface injectable.

Initial proposed call graph:

| Mode | Required calls |
|---|---|
| `quick-scan` | quote, metrics, valuation, fundamentals, concept, fund_flow, limited news, market risk flags |
| `analyze-stock` | full current call graph |
| `panel-only` | quote, metrics, valuation, fundamentals, finance |
| `scan-trap` | quote, bars, concept, fund_flow, filings, margin_trading, block_trade, holder_num, dragon_tiger |
| `lhb-analyzer` | quote, concept, dragon_tiger, daily/industry if later available |
| `dcf` | quote, valuation, fundamentals, finance, reports optional |
| `comps` | quote, metrics, fundamentals, industry, iwencai/peer source when available |

Acceptance:

- Tests prove `quick-scan` does not call heavy providers such as reports/filings/full dividend list.
- Tests prove `analyze-stock` retains broad coverage.
- Existing CLI behavior and artifact paths remain compatible.

## Milestone 2: Markdown Report Contract

Purpose: convert Markdown from debug dump into a readable human report.

### PR-GAP-003: Add Markdown Summary Renderers

Goal:

- Stop directly printing large dicts, DataFrame strings, and nested concept payloads.

Scope:

- Add formatting helpers for quote, valuation, fundamentals, finance, concept, reports/news/filings, capital flow, risk.
- Preserve full raw data in JSON.
- Markdown should show compact tables or bullet summaries.
- Limit list output:
  - concepts: top 5-8 names
  - reports/news/filings: count plus top 3 titles when available
  - warnings: grouped and de-duplicated

Acceptance:

- Smoke Markdown for `600519 quick-scan` is short enough to read.
- Tests assert that raw dict reprs are not emitted for quote/concept.
- Tests assert stable section order remains.

## Milestone 3: Data Quality Model

Purpose: borrow the useful part of UZI's DimResult/Quality model without copying its whole pipeline.

### PR-GAP-004: Add UZEN Source Quality Records

Goal:

- Replace coarse warning-only quality with structured per-source quality.

Scope:

- Add a lightweight internal shape:

```json
{
  "label": "valuation",
  "quality": "full|partial|missing|error|skipped",
  "source": "hoxit.valuation.full_valuation",
  "warnings": [],
  "required": [],
  "optional_missing": []
}
```

- Keep top-level `data_quality.warnings` for backward compatibility.
- Mark skipped providers in mode profiles as `skipped`, not missing.

Acceptance:

- Provider exceptions are visible per source.
- `quick-scan` skipped heavy sources do not make completeness false by themselves.
- Tests cover full, error, skipped, and unsupported F10 states.

## Milestone 4: Hoxit-Native DCF And Comps

Purpose: make `dcf` and `comps` command names meaningful before any persona work.

### PR-GAP-005: Add Light DCF Model

Goal:

- Add a hoxit-native simplified DCF function with traceable assumptions.

Scope:

- Use hoxit valuation/fundamentals/finance data.
- Include WACC assumptions, terminal growth, explicit forecast, intrinsic per-share value, sensitivity table.
- Avoid unsupported precision; show data-quality caveats.

Acceptance:

- Pure unit tests for DCF math.
- `hoxit uzen dcf` includes DCF section in JSON and Markdown.

### PR-GAP-006: Add Comparable Company Summary

Goal:

- Add hoxit-native comps summary using available industry and peer data.

Scope:

- First pass can use industry comparison and iwencai peer query if configured.
- Produce multiples table only when data exists.
- Otherwise produce explicit "peer data insufficient" result.

Acceptance:

- Tests cover peer data available and missing.
- `hoxit uzen comps` no longer only reports generic industry rows.

## Milestone 5: Risk Model Split

Purpose: prevent market-risk signals from being mislabeled as UZI-style trap detection.

### PR-GAP-007: Split Market Risk And Trap Risk

Goal:

- Separate deterministic hoxit market-risk flags from social/manipulation trap detection.

Scope:

- Rename current internal risk object to `market_risk`.
- Keep CLI `scan-trap`, but output should state which signals are market-data-based.
- Add optional `trap_risk` schema for future evidence URLs.

Acceptance:

- Markdown no longer implies social trap evidence when only market data was checked.
- Tests cover risk object names and backward-compatible summary.

## Milestone 6: Investor Panel Foundation

Purpose: move from placeholder PE/ROE scoring toward a real panel without importing all UZI persona complexity in one PR.

### PR-GAP-008: Define Lightweight Investor Signal Schema

Goal:

- Add a stable panel signal schema before implementing many investors.

Scope:

- Define signal fields:
  - investor_id
  - name
  - group
  - signal
  - score
  - confidence
  - reasoning
  - pass/fail
- Implement 3-5 deterministic A-share baseline investors first:
  - value
  - growth
  - quality
  - technical
  - hot-money suitability

Acceptance:

- `panel-only` returns a vote distribution, not one scalar score.
- Tests assert schema and vote aggregation.

### PR-GAP-009: Migrate Selected Persona Rules

Goal:

- Migrate a small subset of UZI persona/rule logic after the schema exists.

Scope:

- Start with 10 investors matching UZI quick-scan Top 10 concept.
- Do not role-play with LLM yet.
- Use deterministic rules only.

Acceptance:

- Each investor has method-specific pass/fail evidence.
- `quick-scan` can include Top 10 panel summary.

## Milestone 7: Agent Analysis Envelope

Purpose: support UZI-style agent qualitative input without forcing it into every run.

### PR-GAP-010: Add Optional Agent Analysis Input

Goal:

- Let `run_analysis()` accept or load an optional agent-analysis JSON artifact.

Scope:

- Define schema for:
  - qualitative commentary
  - bull/bear arguments
  - risks
  - followups
  - data gap acknowledgements
- Renderer includes the section only when provided.

Acceptance:

- No network or LLM required in tests.
- Invalid schema produces a warning, not a crash.

## Milestone 8: Report Experience

Purpose: only after Markdown and data contracts are stable, consider richer output.

### PR-GAP-011: HTML Report Spike

Goal:

- Evaluate whether UZI's HTML report concepts can be adapted to UZEN artifacts.

Scope:

- Create a minimal static HTML renderer from UZEN JSON.
- No remote hosting, no share cards, no browser fallback.

Acceptance:

- HTML generated from fixture JSON.
- Does not add heavy runtime dependencies.

## Recommended Immediate Next Work

The next executable work should be PR-GAP-001 through PR-GAP-003 only.

Reason:

- These close the gap between current behavior and current public docs.
- They do not require new external data sources.
- They make smoke outputs useful.
- They reduce the risk of building persona/modeling layers on an unclear artifact contract.

## Suggested First PR Ticket

Title:

`PR-GAP-001: UZEN Scope Truth And Status Cleanup`

Branch:

`agent/cc/pr-gap-001-uzen-scope-truth`

Scope:

- Update UZEN docs to state first-version approximation status.
- Update final handoff status from pre-merge approval language to merged main language.
- Add a short gap audit pointer to `uzen-skills/README.md`.

Must not change:

- `hoxit/`
- `tests/`
- CLI behavior

Verification:

```bash
git diff --check -- uzen-skills docs/superpowers/status docs/superpowers/specs docs/superpowers/plans
```

## Review Gates

Do not start PR-GAP-002 until PR-GAP-001 is approved.

Do not start DCF/comps/panel/trap upgrades until:

- mode execution profiles are implemented
- Markdown report contract is readable
- source quality records are structured

This keeps later analytical migration grounded in stable hoxit artifacts.
