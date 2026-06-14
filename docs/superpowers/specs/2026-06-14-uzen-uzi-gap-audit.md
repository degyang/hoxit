# UZEN vs UZI-Skill Gap Audit

Date: 2026-06-14
Status: draft for review

## Purpose

This audit compares the reference project `Reference/UZI-Skill` with the current hoxit/UZEN implementation now merged into `main`.

The goal is not to chase full UZI parity immediately. The goal is to identify the real differences, classify which differences matter for an A-share-first hoxit-native product, and define a staged plan that preserves hoxit's architecture instead of importing UZI's provider chain wholesale.

## Source Material Reviewed

Reference project:

- `Reference/UZI-Skill/README.md`
- `Reference/UZI-Skill/run.py`
- `Reference/UZI-Skill/commands/*.md`
- `Reference/UZI-Skill/skills/deep-analysis/SKILL.md`
- `Reference/UZI-Skill/skills/investor-panel/SKILL.md`
- `Reference/UZI-Skill/skills/trap-detector/SKILL.md`
- `Reference/UZI-Skill/skills/lhb-analyzer/SKILL.md`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/run_real_test.py`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/lib/pipeline/*.py`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/lib/fin_models.py`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/lib/investor_evaluator.py`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/assemble_report.py`
- `Reference/UZI-Skill/skills/deep-analysis/scripts/lib/self_review.py`
- UZI persona, reference, provider, report, and test directories.

Current hoxit/UZEN:

- `hoxit/uzen.py`
- `hoxit/cli.py`
- `tests/test_uzen.py`
- `tests/test_cli.py`
- `uzen-skills/`
- `docs/INTERFACES.md`
- `docs/superpowers/specs/2026-06-14-uzen-skills-design.md`
- `docs/superpowers/status/uzen-final-handoff.md`
- Smoke output:
  - `/Users/mac/Projects/POS/90-Inbox/uzen-smoke/600519-quick-scan.json`
  - `/Users/mac/Projects/POS/90-Inbox/uzen-smoke/600519-quick-scan.md`

## Executive Finding

Current UZEN is not a functional lightweight clone of UZI-Skill. It is a hoxit-native data foundation and report skeleton inspired by UZI command names.

That is not a failure of v1; it matches the first-version constraint to use hoxit as the data substrate and avoid importing UZI's provider chain. But it means the next phase must stop treating command-name parity as product parity.

The biggest gaps are:

1. UZI's staged pipeline and quality gates are absent.
2. `quick-scan` does not actually use a lightweight call graph.
3. `panel-only` is a placeholder score, not an investor panel.
4. `scan-trap` is market-signal risk tagging, not UZI's social/manipulation trap detector.
5. `dcf` and `comps` are command labels over generic valuation/industry data, not institutional models.
6. Markdown output is a debug dump, not a research report.
7. UZI's agent-in-the-loop analysis and persona layer are not represented.

## Product Shape Comparison

| Area | UZI-Skill | Current hoxit/UZEN | Gap |
|---|---|---|---|
| Product boundary | Standalone stock research plugin across A/H/US | hoxit module and local skills directory for A-share only | Intentional narrowing, but must be explicit |
| User entry | Plugin commands plus `python run.py` | `hoxit uzen <mode> <code>` | Acceptable for hoxit-native workflow |
| Primary output | HTML report, Markdown/summary, share cards, remote links | JSON and Markdown files | Large product gap |
| Data source model | akshare, baostock, efinance, tushare, browser/web fallback, MX, cache | hoxit modules, mootdx, Tencent, Eastmoney, CNInfo, iwencai, Baidu, THS | Correct strategic shift, but coverage lower |
| Pipeline | stage1/stage2 and newer pipeline runner | single `collect_snapshot -> analyze_snapshot -> render_markdown` | Major architecture gap |
| Quality model | DimResult/Quality, self-review issues, hard gates | `data_quality.complete` and warning strings | Insufficient for UZI-like reliability |
| Agent role | Required qualitative agent analysis for full reports | None | Major analytical gap |
| Tests | broad pipeline/provider/render/regression suite | focused unit tests for UZEN and CLI | hoxit v1 adequate, UZI parity inadequate |

## Command Coverage

### Commands Migrated By Name

| Command | UZI behavior | Current UZEN behavior | Assessment |
|---|---|---|---|
| `analyze-stock` | Full deep workflow with many dimensions, panel, synthesis, HTML | Full hoxit snapshot and Markdown/JSON | Name covered, behavior partial |
| `quick-scan` | 4 core dimensions, Top 10 investors, trap scan, 1-2 minute target | Same full call graph as analyze mode, just mode profile metadata | Semantic mismatch |
| `dcf` | WACC, 2-stage FCF, terminal value, sensitivity table | hoxit valuation snapshot only | Placeholder |
| `comps` | peer multiples, percentile, implied target price | industry comparison rows only | Placeholder |
| `panel-only` | 65-person investor panel with group logic and Great Divide | simple PE/ROE score | Placeholder |
| `scan-trap` | 8 social/manipulation signals with evidence URLs and keyword boost | block trade, margin trading, holder change, fund flow flags | Different risk model |
| `lhb-analyzer` | seat recognition, hot-money identity, institution vs hot-money, peer board comparison | dragon tiger data count and broad risk flags | Partial data only |

### Commands Not Migrated

UZI has additional commands that are not in first-version UZEN:

- `ai-readiness`
- `catalysts`
- `dd`
- `earnings`
- `earnings-preview`
- `ic-memo`
- `initiate`
- `lbo`
- `model-update`
- `rebalance`
- `returns`
- `screen`
- `segmental-model`
- `thesis`

These should remain deferred unless hoxit first gains the required data and modeling primitives.

## Architecture Comparison

### UZI-Skill Architecture

UZI is built as a research pipeline:

1. Resolve ticker and market.
2. Run many fetchers, partly parallelized.
3. Normalize data into dimension outputs.
4. Score dimensions.
5. Generate investor panel.
6. Optionally run agent qualitative analysis.
7. Synthesize judgment.
8. Run self-review gates.
9. Render HTML and share artifacts.

Important internal components:

- `run.py`: user runner, environment handling, browser/remote serving.
- `run_real_test.py`: legacy stage1/stage2 workflow and fetcher map.
- `lib/pipeline/schema.py`: `DimResult`, `Quality`, `FetcherSpec`.
- `lib/pipeline/run.py`: collect, score, synthesize, render orchestration.
- `lib/fin_models.py`: DCF, comps, 3-statement, LBO, merger models.
- `lib/investor_evaluator.py`: rule-based investor scoring.
- `skills/deep-analysis/personas/*.yaml`: persona definitions.
- `assemble_report.py`: HTML report renderer.
- `lib/self_review.py`: mechanical quality gate.

### Current hoxit/UZEN Architecture

Current UZEN is a single hoxit module:

```text
hoxit uzen <mode>
  -> hoxit.uzen.run_analysis()
  -> collect_snapshot()
  -> analyze_snapshot()
  -> render_markdown()
  -> write JSON and Markdown artifacts
```

Important components:

- `UzenDataProvider`: injectable provider boundary.
- `default_provider()`: hoxit module wiring.
- `_safe_call()`: warning-based failure isolation.
- `collect_snapshot()`: one broad snapshot call graph.
- `_panel_summary()`: small PE/ROE score.
- `_trap_risk()`: market-signal flags.
- `_mode_profile()`: mode labels only.
- `render_markdown()`: stable section renderer, currently raw-object heavy.

This architecture is simple, testable, and aligned with hoxit's module style. It is not yet a UZI-style research pipeline.

## Data Model Gap

### UZI Data Model

UZI's core model is dimension-oriented:

- dimension key, such as `1_financials`, `10_valuation`, `18_trap`
- explicit quality state: full, partial, missing, error
- data gaps per dimension
- source labels
- latency/cache metadata
- downstream scoring and renderer assumptions

This lets UZI answer:

- which dimension failed
- whether the report can proceed
- whether a failure is critical
- which fallback or agent action is needed

### Current UZEN Data Model

UZen uses a source-oriented snapshot:

```json
{
  "sources": {
    "quote": {},
    "bars": [],
    "valuation": {},
    "fundamentals": {},
    "signals": {}
  },
  "analysis": {
    "summary": {},
    "panel": {},
    "trap_risk": {},
    "mode_profile": {}
  },
  "data_quality": {
    "complete": false,
    "warnings": []
  }
}
```

This is a good hoxit boundary, but too coarse for UZI parity. It cannot distinguish "valuation partial but usable" from "trap scan missing social evidence" except through unstructured warning text.

## Data Source Gap

Current hoxit covers a useful A-share subset:

- market quote, K-line, transactions
- Tencent valuation metrics
- Eastmoney reports/news/fund flow/dragon tiger paths
- CNInfo filings
- iwencai fallback
- Baidu concept/fund flow
- THS hot reason/EPS forecast
- margin trading, block trade, holder number, dividends

UZI additionally expects or implements:

- broader fetchers for chain, macro, materials, futures, governance, moat, events, sentiment, contests, similar stocks, fund holders
- browser fallback and web search fill-ins
- data-source registry and network preflight logic
- cache/resume behavior
- market routing across A/H/US
- provider chain fallback outside hoxit's boundary

Decision: do not import UZI providers wholesale. Add only A-share reusable hoxit APIs when a missing source is required by an accepted UZEN mode.

## Report Output Gap

The smoke Markdown shows the current renderer is mostly a debug view:

- raw quote dict is printed directly
- raw valuation dict is printed directly
- finance can render as a DataFrame string
- concept data prints the full nested object
- reports/news/filings only show counts
- mode-specific structure is not reflected in the report body

This is acceptable as a first artifact writer, but not as a usable research report.

UZI's report layer is qualitatively different:

- dimension cards
- panel cards
- visual primitives
- institutional model sections
- self-review guardrails
- conflict-aware synthesis
- HTML and share image outputs

Decision: the next UZEN report work should first make Markdown a readable A-share report, then consider HTML.

## Agent Analysis Gap

UZI's full workflow depends on agent intervention:

- agent reads raw data, panel, and review issues
- agent writes `agent_analysis.json`
- agent qualitative analysis covers macro, industry, materials, futures, policy, events
- role-play persona layer reads investor YAML and references
- stage2 prioritizes agent analysis over stubs

Current UZEN has no equivalent. `analysis.panel` and `analysis.trap_risk` are deterministic heuristics only.

Decision: do not pretend the current output is UZI-style "deep analysis". Add an explicit optional analysis envelope later, after the data and report contracts are stable.

## Mode-Specific Gap

Current `_mode_profile()` only labels the mode:

```python
"quick-scan": {"depth": "lite", "primary_section": "summary"}
```

It does not change:

- provider calls
- output sections
- artifact shape
- runtime target
- tests for reduced call graph

This is the highest-confidence functional gap because UZI's `quick-scan` explicitly says it should run only core dimensions.

## Risk And Trap Detection Gap

UZI `scan-trap` is a social/manipulation detector. It scans:

1. low-quality account promotion
2. templated recommendation phrasing
3. paid group/live-room funnels
4. fundamentals vs heat mismatch
5. abnormal K-line coordination
6. teacher/guru persona promotion
7. cross-platform promotion
8. fake reports or rumors

Current UZEN `trap_risk` is a market-data risk tagger:

- block trades
- margin trading
- holder number changes
- fund flow missing

These are useful, but they are not the same product. They should be split into two concepts:

- `market_risk`: hoxit data-driven flags
- `trap_risk`: social/manipulation evidence scan, optional and evidence-backed

## Investor Panel Gap

UZI investor panel:

- 65 investor identities
- group-level methodology
- persona YAML for many investors
- rule engine
- market and style suitability
- hot-money seat range filtering
- vote distributions and Great Divide

Current UZEN:

- simple numeric score from PE and ROE
- no investor identities
- no rule engine
- no vote distribution

Decision: rename current concept internally as `lightweight_panel` or upgrade in stages. Do not call it equivalent to UZI investor-panel.

## Financial Modeling Gap

UZI contains institutional-style functions:

- two-stage DCF and WACC
- sensitivity table
- comps table
- 3-statement projection
- quick LBO
- accretion/dilution
- Tier-1 AI readiness, earnings preview, model update, returns attribution, rebalance

Current UZEN has:

- hoxit valuation snapshot
- forward PE/PEG helpers from hoxit valuation layer
- no DCF engine
- no comps statistics

Decision: DCF and comps command names should either be documented as "light view" or backed by hoxit-native modeling functions in future PRs.

## Testing Gap

Current hoxit test suite passes and UZEN has focused tests. This is enough for v1 integration.

But UZI parity would require new tests for:

- mode-specific provider call graphs
- dimension quality states
- report readability contracts
- trap/social evidence schema
- investor panel signal schema
- DCF/comps numerical invariants
- live smoke tests behind `HOXIT_LIVE_TESTS=1`

## Current Status Assessment

| Capability | Status |
|---|---|
| A-share hoxit data substrate | Strong foundation |
| UZEN CLI command surface | Present |
| JSON artifact output | Present |
| Markdown artifact output | Present but low readability |
| Mode profiles | Metadata only |
| quick-scan semantics | Not implemented |
| analyze-stock deep analysis | Skeleton only |
| DCF | Placeholder |
| Comps | Placeholder |
| Investor panel | Placeholder |
| Trap detector | Different risk model |
| LHB analyzer | Partial data only |
| Data quality model | Too coarse |
| Agent analysis loop | Missing |
| HTML/share artifacts | Deferred |
| Cross-market support | Deferred by design |

## Planning Principle

Future work should use this order:

1. Make current hoxit-native behavior honest and useful.
2. Add mode-specific execution semantics.
3. Improve Markdown report quality.
4. Add structured data quality and validation.
5. Only then migrate selected UZI analytical layers.

Do not import UZI's whole pipeline as-is. It conflicts with hoxit's design goals:

- hoxit keeps optional third-party imports lazy.
- hoxit prefers injectable network IO and unit tests without network.
- hoxit centralizes reusable A-share data APIs in flat modules.
- hoxit should not grow one-off provider chains inside `uzen-skills`.

## Recommended Direction

Proceed with a staged UZEN v1.0.1/v1.1 program:

- v1.0.1: make current command behavior truthful and readable.
- v1.1: add UZI-inspired hoxit-native modeling and risk primitives.
- v1.2: add optional agent analysis envelope.
- v2: consider HTML/share/report experience and broader UZI parity.

This keeps the project honest: UZEN is hoxit-native first, UZI-parity selective second.
