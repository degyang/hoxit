# Hoxit Execution Binding

Date: 2026-06-10

Purpose: make the POS `skills-tos-funder` commands auditable against existing hoxit executable routes. This file is the incremental migration contract: POS commands may orchestrate or score, but every data collection step must bind to a hoxit CLI/API route that exists in this repository.

Status enum:

- `direct`: command primarily calls one or more hoxit routes.
- `proxy`: command uses an A-share substitute route because the original `ai-hedge-fund` data source does not have one-to-one hoxit parity.
- `orchestrator`: command consumes other tos-funder command outputs and only calls hoxit indirectly.

## Route Inventory

Current hoxit executable routes used by tos-funder:

| Route | Purpose |
|---|---|
| `hoxit market bars` | OHLCV bars from mootdx/TDX, with `--adjust raw/qfq/hfq`. |
| `hoxit market quote` | Real-time quote from mootdx, Tencent fallback only. |
| `hoxit market metrics` | Tencent PE/PB/market-cap/turnover style valuation metrics. |
| `hoxit iwc query` | iWencai query2data route for basicinfo, market, finance, management, and other structured facts. |
| `hoxit iwc search` | iWencai comprehensive search route for announcements and reports. |
| `hoxit signals dividend` | Corporate-action cross-check for suspected adjustment distortions. |
| `hoxit signals fund-flow` | Fund-flow history for tactical/risk context. |
| `hoxit signals dragon-tiger` | Individual stock dragon-tiger board data. |
| `hoxit signals daily-dragon-tiger` | Market-wide dragon-tiger board data. |
| `hoxit signals margin-trading` | Margin trading details. |
| `hoxit signals block-trade` | Block trade details. |
| `hoxit signals holder-num` | Holder-number changes. |
| `hoxit signals lockup` | Lock-up expiry checks. |
| `hoxit signals concept` | Concept/sector context. |
| `hoxit signals industry` | Industry comparison context. |
| `hoxit valuation full` | Existing single-stock valuation workflow. |
| `hoxit fundamentals info` | Individual stock profile. |
| `hoxit fundamentals finance` | mootdx finance snapshot. |
| `hoxit fundamentals f10` | mootdx F10 sections. |
| `hoxit reports iwencai` | iWencai report search adapter. |
| `hoxit reports eastmoney` | Eastmoney report list. |
| `hoxit news stock` | Stock news route. |
| `hoxit filings cninfo` | CNINFO filing search. |

## Command Binding Matrix

| POS command | Binding | Hoxit routes | Notes |
|---|---|---|---|
| `/tos-funder-analyze` | orchestrator | `hoxit iwc query`, `hoxit market bars` | Routes to selected analyst commands; direct hoxit use is limited to missing shared facts. |
| `/tos-funder-preflight` | orchestrator | `hoxit iwc query`, `hoxit market bars`, `hoxit iwc search` | Low-cost screen that should call shared primitive commands first when outputs already exist. |
| `/tos-funder-stock-research` | orchestrator | `hoxit iwc query`, `hoxit market bars`, `hoxit iwc search` | Workspace runner; persists command outputs rather than introducing new analysis code. |
| `/tos-funder-quant-price-series` | direct | `hoxit market bars`, `hoxit signals dividend` | Canonical OHLCV source and corporate-action cross-check. |
| `/tos-funder-quant-technicals` | orchestrator | `hoxit market bars` | Computes indicators from `/tos-funder-quant-price-series`; no iWencai indicator dependency. |
| `/tos-funder-risk-manager` | orchestrator | `hoxit market bars`, `hoxit market quote`, `hoxit signals dividend` | Computes risk from price-series output; quote and dividend are validation helpers. |
| `/tos-funder-quant-fundamentals` | direct | `hoxit iwc query`, `hoxit fundamentals info`, `hoxit fundamentals finance` | Deterministic fundamentals over iWencai finance/basicinfo/market packs. |
| `/tos-funder-quant-valuation` | direct | `hoxit iwc query`, `hoxit market metrics`, `hoxit valuation full` | Shared valuation layer; use `valuation full` when existing output is sufficient. |
| `/tos-funder-quant-valuation-damodaran` | proxy | `hoxit iwc query`, `hoxit market metrics`, `hoxit valuation full` | Intrinsic valuation assumptions are skill-side; facts come from hoxit. |
| `/tos-funder-quant-sentiment` | proxy | `hoxit iwc search`, `hoxit iwc query` | Announcement/report proxy for sentiment and event classification. |
| `/tos-funder-news-sentiment` | proxy | `hoxit iwc search`, `hoxit news stock`, `hoxit reports iwencai` | Uses announcement/report proxy unless a reliable external Chinese news route is explicitly needed. |
| `/tos-funder-growth-fisher` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics` | Persona overlay on deterministic growth/fundamental facts. |
| `/tos-funder-growth-lynch` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics` | Persona overlay on PEG/GARP facts. |
| `/tos-funder-growth-cathie-wood` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics` | Disruption proxy from A-share growth, R&D, reports, and event facts. |
| `/tos-funder-growth` | orchestrator | `hoxit iwc query`, `hoxit iwc search` | Aggregates Fisher, Lynch, quant-fundamentals, and quant-sentiment outputs. |
| `/tos-funder-value-buffett` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit valuation full` | Persona overlay on durable-quality and valuation facts. |
| `/tos-funder-value-graham` | proxy | `hoxit iwc query`, `hoxit market metrics`, `hoxit valuation full` | Deep-value proxy with A-share data substitutions. |
| `/tos-funder-value-munger` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit valuation full` | Quality-compounder overlay over deterministic facts. |
| `/tos-funder-value-burry` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit signals holder-num` | Contrarian value proxy; insider-style signals use holder/announcement substitutes. |
| `/tos-funder-value-pabrai` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit valuation full` | Low-downside/high-upside overlay. |
| `/tos-funder-tactical-catalyst` | proxy | `hoxit iwc search`, `hoxit signals fund-flow`, `hoxit signals dragon-tiger`, `hoxit signals block-trade`, `hoxit signals holder-num` | A-share event-catalyst proxy. |
| `/tos-funder-tactical-tail-risk` | proxy | `hoxit market bars`, `hoxit iwc search`, `hoxit signals lockup`, `hoxit signals margin-trading`, `hoxit signals dividend` | Tail-risk proxy from event, liquidity, leverage, and adjustment facts. |
| `/tos-funder-tactical` | orchestrator | `hoxit iwc search`, `hoxit market bars` | Synthesizes catalyst and tail-risk outputs; no final portfolio action. |
| `/tos-funder-tactical-ackman` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit signals holder-num` | Activist-style proxy; A-share governance evidence comes from announcements/holder changes. |
| `/tos-funder-tactical-taleb` | proxy | `hoxit market bars`, `hoxit iwc search`, `hoxit signals margin-trading`, `hoxit signals lockup` | Fragility/convexity proxy based on price and event-risk facts. |
| `/tos-funder-macro-topdown` | proxy | `hoxit iwc query`, `hoxit signals concept`, `hoxit signals industry`, `hoxit market bars` | Top-down market/sector proxy with hoxit-available routes. |
| `/tos-funder-macro-druckenmiller` | proxy | `hoxit iwc query`, `hoxit market bars`, `hoxit signals fund-flow`, `hoxit signals industry` | Macro trend and sector leadership proxy. |
| `/tos-funder-macro-jhunjhunwala` | proxy | `hoxit iwc query`, `hoxit iwc search`, `hoxit market metrics`, `hoxit signals concept` | Domestic-growth and macro-tailwind proxy. |
| `/tos-funder-portfolio` | orchestrator | `hoxit market quote`, `hoxit market bars`, `hoxit signals dividend` | Final action synthesizer; hoxit routes are validation helpers, not a separate portfolio runtime. |

## Incremental Rule

When a POS command needs a route not listed above:

1. Add the hoxit function or CLI/API route first.
2. Add offline tests for parsing, schema, and failure behavior.
3. Add live tests only behind `HOXIT_LIVE_TESTS=1`.
4. Update this binding matrix and the relevant POS command.
5. Run the migration parity tests.

Do not mark a command as execution-complete unless this file points to real hoxit routes and the command's data collection section uses those routes or consumes another command that does.

## Run Lessons

- 2026-06-10 宁波银行 full run: see `docs/tos-funder/19-ningbo-bank-run-lessons.md`.
- `mode=full` must not stop at the 11-layer core spine; it must include expanded migrated layers before final portfolio synthesis.
