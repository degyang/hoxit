# UZEN Skills A-Share Migration Design

Date: 2026-06-14
Status: approved design draft

## Context

The reference project is `Reference/UZI-Skill`, a symlink to `/Users/mac/Developments/UZI-Skill`. It is a full stock research plugin rather than a simple data-query skill set. Its current shape includes:

- `run.py` as the user-facing runner.
- `commands/` with stock analysis commands such as `analyze-stock`, `quick-scan`, `dcf`, `comps`, `scan-trap`, `panel-only`, and `lhb-analyzer`.
- `skills/deep-analysis/` with the main workflow, personas, report assets, fetchers, scoring, synthesis, and rendering code.
- Additional skills: `investor-panel`, `lhb-analyzer`, and `trap-detector`.
- A provider chain that relies heavily on `akshare`, `baostock`, `efinance`, `tushare`, browser fallback, and web search.

The hoxit project is an A-share data toolkit with seven data layers and a testable Python API/CLI. The migration must use hoxit as the primary data substrate. If hoxit cannot cover an A-share capability that is required by the migrated workflow, the capability should be added to hoxit first, then consumed by `uzen-skills`.

## Goal

Create `uzen-skills/` in the current hoxit repository as an A-share-first migration of UZI-Skill's core stock research experience.

The first version must:

- Support A-share stock analysis only.
- Prefer hoxit Python APIs and CLI behavior over UZI's original provider chain.
- Produce JSON and Markdown outputs first.
- Preserve UZI's useful analysis workflow assets: command intent, skill instructions, investor panel concept, trap checks, and research-report structure.
- Record deferred UZI capabilities clearly so they are not lost.

## Non-Goals For The First Version

These are explicitly out of scope for the first implementation, but must remain visible as follow-up work:

- Hong Kong stocks, US stocks, futures, macro-only workflows, ETF/LOF, convertible bonds, and portfolio-level analysis.
- HTML report rendering, share-card images, war-report images, and front-end assets.
- Cloudflare tunnel or remote sharing.
- Automatic dependency installation.
- Playwright or browser fallback as a required data-repair path.
- UZI's provider chain as the primary path.
- Full role-play of all UZI investor personas before the deterministic data path is stable.
- Copying platform packaging files such as `.claude-plugin`, `.cursor-plugin`, `.opencode`, and Gemini extension manifests unless a later packaging task requires them.

## Proposed Directory Layout

```text
uzen-skills/
  README.md
  AGENTS.md
  commands/
    analyze-stock.md
    quick-scan.md
    dcf.md
    comps.md
    panel-only.md
    scan-trap.md
    lhb-analyzer.md
  skills/
    deep-analysis/
      SKILL.md
      references/
      personas/
    investor-panel/
      SKILL.md
    lhb-analyzer/
      SKILL.md
    trap-detector/
      SKILL.md
  reports/
    .gitkeep
  cache/
    .gitkeep
```

The repository should also gain a deterministic execution module:

```text
hoxit/uzen.py
tests/test_uzen.py
```

`uzen-skills/` is the skill and command layer. `hoxit/uzen.py` is the testable Python implementation layer.

## Architecture

The first version uses a thin skill layer over hoxit:

```text
uzen command or skill
  -> hoxit.uzen.run_analysis(code, mode=...)
  -> hoxit market / valuation / fundamentals / reports / news / filings / signals / iwencai
  -> normalized snapshot
  -> scoring, panel summary, risk checks
  -> JSON and Markdown report
```

Skill Markdown files must not contain duplicated HTTP request code. They should describe when to use the workflow, how to invoke it, what data sources are used, and how to interpret the output.

The Python execution layer should follow hoxit's existing rules:

- Network IO remains injectable where practical.
- Heavy third-party packages are imported lazily.
- Return types are `dict` or `list[dict]`.
- Default unit tests do not require network access.
- External interface changes are logged in `docs/API_DEVLOG.md`.

## First-Version Commands

The first version should migrate these commands:

- `analyze-stock`: complete A-share report, JSON plus Markdown.
- `quick-scan`: smaller report focused on quote, valuation, trend, capital flow, hot themes, and risk flags.
- `dcf`: light valuation section based on hoxit valuation data and available forward estimates.
- `comps`: peer and industry comparison using hoxit industry data and iwencai fallback.
- `panel-only`: investor-panel vote summary without a full report.
- `scan-trap`: trap/risk scan using ST signals, abnormal capital flow, topic heat, filings, shareholder changes, block trades, margin trading, and dragon-tiger data.
- `lhb-analyzer`: dragon-tiger-board focused report.

Commands from UZI that are not listed above remain deferred.

## Data Mapping

Use hoxit APIs first:

- Quote and K-line: `hoxit.market.mootdx_quote`, `hoxit.market.mootdx_bars`.
- Valuation metrics: `hoxit.market.tencent_metrics`, `hoxit.valuation.full_valuation`.
- Fundamentals: `hoxit.fundamentals.individual_info`, `hoxit.fundamentals.finance_snapshot`, `hoxit.fundamentals.f10`.
- Research: `hoxit.reports.eastmoney_reports`, `hoxit.reports.iwencai_search`.
- News: `hoxit.news.stock_news`.
- Filings: `hoxit.filings.cninfo_reports`.
- Signals: `hoxit.signals.ths_hot_reason`, `hoxit.signals.baidu_concept_blocks`, `hoxit.signals.baidu_fund_flow_history`, `hoxit.signals.dragon_tiger_board`, `hoxit.signals.daily_dragon_tiger`, `hoxit.signals.lockup_expiry`, `hoxit.signals.industry_comparison`.
- Existing but under-documented signal helpers: `hoxit.signals.margin_trading`, `hoxit.signals.block_trade`, `hoxit.signals.holder_num_change`, `hoxit.signals.dividend_history`.
- General fallback: `hoxit.iwencai.query_rows`, `hoxit.iwencai.search_rows`.

When `fundamentals.f10()` returns a structured unsupported result, UZEN should continue with available alternative sources instead of failing the whole report.

## Missing Capability Policy

Missing capabilities must be handled in this order:

1. Use an existing hoxit API if one exists.
2. Use `hoxit.iwencai` if an existing route covers the query.
3. Add an A-share-focused hoxit business API, CLI help, tests, and interface documentation if the capability is core to the report.
4. Mark the section as deferred if the capability is outside the first-version A-share scope.

`uzen-skills` should not grow one-off scrapers that bypass hoxit's data boundary.

## Snapshot Schema

`hoxit.uzen` should normalize inputs into a single snapshot dictionary. A first-version shape:

```json
{
  "code": "600519",
  "market": "A",
  "mode": "analyze-stock",
  "generated_at": "2026-06-14T00:00:00+08:00",
  "data_quality": {
    "complete": false,
    "warnings": []
  },
  "sources": {
    "quote": {},
    "bars": [],
    "valuation": {},
    "fundamentals": {},
    "reports": [],
    "news": [],
    "filings": [],
    "signals": {}
  },
  "analysis": {
    "summary": {},
    "valuation": {},
    "industry": {},
    "panel": {},
    "trap_risk": {},
    "followups": []
  }
}
```

The schema is intentionally simple so Markdown and later HTML rendering can share the same artifact.

## Markdown Report

The first report renderer should produce stable Markdown with these sections:

1. Core conclusion.
2. Data completeness and caveats.
3. Market and valuation.
4. Fundamentals and financials.
5. Research, news, and filings.
6. Capital flow, dragon-tiger board, and hot themes.
7. Industry and peer comparison.
8. Investor panel summary.
9. Trap and risk checks.
10. Follow-up watchlist.

Markdown wording should avoid unsupported investment advice. It should describe evidence, risks, and scenarios.

## Testing Strategy

Default tests must not access live network endpoints.

Required coverage:

- Snapshot assembly with injected/mock data functions.
- Missing-data behavior, including unsupported F10 responses.
- Markdown section presence and stable ordering.
- `quick-scan` calling only the smaller data set.
- `scan-trap` risk scoring with deterministic fixtures.
- `panel-only` output shape.
- Command/skill docs reference existing APIs.
- Any new hoxit external interface gets parser tests and a `docs/API_DEVLOG.md` entry.

Live endpoint tests can be added only behind the existing `HOXIT_LIVE_TESTS=1` convention.

## Deferred Backlog

These items are intentionally recorded for later phases:

- HTML report migration using UZI templates and assets.
- Share-card and war-report image rendering.
- Browser/Playwright data repair.
- Cloudflare remote report hosting.
- Full UZI investor persona migration, including YAML-backed flagship personas.
- Full 22-dimension UZI scoring parity.
- Deep DCF, Comps, LBO, IC Memo, earnings preview, model update, segmental model, DD checklist, catalysts, and thesis tracking.
- Portfolio commands: returns attribution and rebalance.
- Cross-market support: Hong Kong stocks, US stocks, futures, macro, ETF/LOF, convertible bonds.
- Optional packaging as a Claude/Codex/Cursor/Gemini plugin.
- Provider-chain fallback if hoxit and iwencai cannot cover a later non-core source.

## PR Decomposition

Recommended implementation tickets:

1. Add `uzen-skills` skeleton, command docs, skill docs, README, and this design-linked scope.
2. Add `hoxit.uzen` snapshot aggregator and Markdown/JSON renderers with unit tests.
3. Implement `quick-scan` and minimal `analyze-stock` paths.
4. Implement `panel-only` with a lightweight A-share panel summary.
5. Implement `scan-trap` and `lhb-analyzer`.
6. Sync docs: `docs/INTERFACES.md`, `docs/API_DEVLOG.md` if new external behavior is added, and command examples.

## Open Risks

- hoxit currently has a dirty worktree with unrelated user changes. Implementation must avoid reverting or overwriting them.
- Some hoxit CLI capabilities are present but under-documented. The implementation phase should decide whether to update `docs/INTERFACES.md` in the same PR as UZEN or in a separate documentation PR.
- Peer comparison, moat, supply-chain, raw-material, and policy dimensions may need iwencai fallback or later dedicated hoxit APIs.
- UZI's original reports are much richer than the first Markdown output. The first version must communicate that it is a stable data-and-analysis foundation, not full UZI parity.
