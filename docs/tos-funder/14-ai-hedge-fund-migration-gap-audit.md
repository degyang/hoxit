# AI Hedge Fund Migration Gap Audit

Date: 2026-06-10

Scope: compare `Reference/ai-hedge-fund` against current `skills-tos-funder/tos-funder` command and reference coverage. This audit treats the existing migration strategy as skill-first: preserve investment workflows and data contracts where useful, but do not port LangGraph, the original web app, or the Financial Datasets runtime unless explicitly planned.

## Source Inventory

Original project areas reviewed:

| Area | Path | Migration relevance |
|---|---|---|
| Main analyst graph | `Reference/ai-hedge-fund/src/main.py`, `src/utils/analysts.py`, `src/agents/*.py` | Primary source for analyst/persona workflows. |
| Data API helpers | `Reference/ai-hedge-fund/src/tools/api.py` | Source API surface to replace with hoxit/iWencai/mootdx equivalents. |
| Backtesting v1 | `Reference/ai-hedge-fund/src/backtesting/*`, `src/backtester.py` | Simulation, metrics, execution, portfolio history. |
| Web app | `Reference/ai-hedge-fund/app/*` | FastAPI + React flow builder, API key storage, runs, backtests. |
| v2 quant stack | `Reference/ai-hedge-fund/v2/*` | Work-in-progress quantitative stack: event study, validation, portfolio optimization, execution simulation. |

Current skill areas reviewed:

| Area | Path | Coverage role |
|---|---|---|
| Skill entry | `tos-funder/SKILL.md` | Routing, source policy, action boundaries. |
| Commands | `tos-funder/commands/*.md` | User-facing skill workflows. |
| References | `tos-funder/references/*.md` | Strategy knowledge base and data contracts. |
| Migration docs | `docs/00-overview.md`, `01-interface-coverage.md`, `03-build-plan.md`, validation docs | Plan, interface coverage, accepted PR evidence. |

## Executive Finding

The migration is complete for a compressed A-share research workflow, not for all original `ai-hedge-fund` capabilities.

Implemented command families cover:

- Value: Buffett, Graham.
- Growth: Fisher, Lynch, growth aggregator.
- Quant: fundamentals, price-series, technicals, sentiment.
- Tactical/risk/macro: catalyst proxy, tail-risk proxy, tactical synthesis, macro top-down proxy, risk manager.
- Portfolio/workspace: portfolio synthesizer, analyze router, preflight, stock research workspace.

Material gaps remain:

- Missing value-persona commands: Munger, Michael Burry, Mohnish Pabrai.
- Missing growth-persona command: Cathie Wood.
- Missing tactical/persona commands: Bill Ackman, Stanley Druckenmiller, Rakesh Jhunjhunwala, Nassim Taleb as persona-level workflows.
- Missing valuation personas/modules: Aswath Damodaran and standalone Valuation Analyst.
- Missing distinct original generic analyst commands: original `growth_agent`, `news_sentiment`, and standalone Financial Datasets-style `sentiment` are only partially represented through A-share proxies.
- Not migrated by design: LangGraph runtime, web app, model-provider UI, API-key service, original Financial Datasets client.
- Not yet migrated: v1/v2 backtesting engine, event study, CPCV/PBO validation, portfolio optimizer, execution simulation.

## Analyst Coverage Matrix

Original analyst registry source: `Reference/ai-hedge-fund/src/utils/analysts.py`.

| Original analyst key | Original role | Current skill coverage | Status | Gap / action |
|---|---|---|---|---|
| `warren_buffett` | Quality value / moat | `/tos-funder-value-buffett`, `references/value-investors.md` | Covered | Keep as core value thesis input. |
| `ben_graham` | Defensive deep value | `/tos-funder-value-graham`, `references/value-investors.md` | Covered | Keep as margin-of-safety input. |
| `charlie_munger` | Quality compounders, management, insider/behavioral lens | Mentioned in taxonomy and interface coverage only | Missing command | Add `/tos-funder-value-munger`; use quality moat + management/incentive proxy; do not depend on dead management insider route. |
| `michael_burry` | Contrarian value, downside/catalyst awareness | Mentioned in taxonomy and interface coverage only | Missing command | Add `/tos-funder-value-burry`; combine cheapness, balance-sheet stress, bearish/catalyst evidence, crowding/overvaluation checks. |
| `mohnish_pabrai` | Dhandho value, low downside/high upside | Mentioned in taxonomy and interface coverage only | Missing command | Add `/tos-funder-value-pabrai`; focus on downside protection, cash/debt, simple thesis, asymmetric payoff. |
| `phil_fisher` | Growth quality / scuttlebutt | `/tos-funder-growth-fisher`, `references/growth-investors.md` | Covered with A-share proxy | Already adapted to announcements/reports and deterministic financials. |
| `peter_lynch` | GARP / PEG | `/tos-funder-growth-lynch`, `references/growth-investors.md` | Covered | Already includes PEG reliability gate. |
| `cathie_wood` | Disruptive innovation / TAM | Future note in `growth-investors.md` and taxonomy | Missing command | Add `/tos-funder-growth-cathie-wood`; source from reports, concept/industry themes, R&D intensity, revenue runway, valuation cap. |
| `bill_ackman` | Activist/catalyst quality | Tactical catalyst proxy partially replaces it | Partial | Add persona command or document as intentionally folded into `/tos-funder-tactical-catalyst`. |
| `stanley_druckenmiller` | Macro/top-down trend | `/tos-funder-macro-topdown` proxy partially replaces it | Partial | Add `/tos-funder-macro-druckenmiller` only if true macro/sector trend workflow is needed; current proxy is deliberately conservative. |
| `rakesh_jhunjhunwala` | Emerging-market/domestic growth + macro | Mentioned in taxonomy and interface coverage only | Missing command | Add `/tos-funder-macro-jhunjhunwala` or fold into Cathie/growth plus macro-topdown; current skill has no specific workflow. |
| `nassim_taleb` | Tail risk / antifragility | `/tos-funder-tactical-tail-risk` partially replaces it | Partial | Add persona-level Taleb command if antifragility/barbell/asymmetry thesis is desired; current command is downside risk proxy only. |
| `aswath_damodaran` | Intrinsic valuation / DCF | Mentioned in quant taxonomy and interface coverage only | Missing command | Add `/tos-funder-quant-valuation-damodaran`; define DCF/FCFF assumptions, WACC substitutes, terminal value sensitivity. |
| `valuation_analyst` | Generic valuation models | No standalone command; valuation is embedded in value/growth/quant fundamentals | Partial | Add `/tos-funder-quant-valuation` as shared valuation layer consumed by value/growth/portfolio. |
| `fundamentals_analyst` | Deterministic financial statement analysis | `/tos-funder-quant-fundamentals` | Covered | Good baseline quant thesis input. |
| `growth_analyst` | Generic growth factors | `/tos-funder-growth` aggregator and `/tos-funder-quant-fundamentals` growth dimension | Partial | If parity is required, add `/tos-funder-quant-growth` or document aggregator as replacement. |
| `technical_analyst` | Technical indicators | `/tos-funder-quant-technicals`, `/tos-funder-quant-price-series` | Covered | Current A-share implementation is stronger than original because it uses mootdx OHLCV locally. |
| `sentiment_analyst` | Insider/news sentiment | `/tos-funder-quant-sentiment` | Partial | A-share replacement is announcement/report based; original insider-trade sentiment is not equivalent. |
| `news_sentiment_analyst` | News-only sentiment | Folded into `/tos-funder-quant-sentiment` | Partial | Add separate `/tos-funder-news-sentiment` only if external Chinese news source is added. |
| `risk_manager` | Position/risk constraints | `/tos-funder-risk-manager`, portfolio constraints | Covered | Current command includes adjustment/data-quality gates. |
| `portfolio_manager` | Final action selection | `/tos-funder-portfolio` | Covered | Current command is the only final-action boundary. |

## Command Coverage Matrix

Current command set: 18 files.

| Current command | Main original equivalent | Status |
|---|---|---|
| `/tos-funder-analyze` | `src/main.py` orchestration, simplified | Covered as skill router, not LangGraph runtime. |
| `/tos-funder-preflight` | No exact original equivalent | A-share-specific addition. |
| `/tos-funder-value-buffett` | `warren_buffett.py` | Covered. |
| `/tos-funder-value-graham` | `ben_graham.py` | Covered. |
| `/tos-funder-growth-fisher` | `phil_fisher.py` | Covered. |
| `/tos-funder-growth-lynch` | `peter_lynch.py` | Covered. |
| `/tos-funder-growth` | `growth_agent.py` plus growth family synthesis | Partial replacement / A-share aggregator. |
| `/tos-funder-quant-fundamentals` | `fundamentals.py` | Covered. |
| `/tos-funder-quant-price-series` | `get_prices`, price adapter | Covered with mootdx replacement. |
| `/tos-funder-quant-technicals` | `technicals.py` | Covered. |
| `/tos-funder-quant-sentiment` | `sentiment.py`, `news_sentiment.py` | Partial A-share proxy. |
| `/tos-funder-risk-manager` | `risk_manager.py` | Covered. |
| `/tos-funder-tactical-catalyst` | Ackman/Burry/Druckenmiller event/catalyst fragments | Partial proxy, not persona parity. |
| `/tos-funder-tactical-tail-risk` | `nassim_taleb.py`, risk fragments | Partial proxy, not persona parity. |
| `/tos-funder-tactical` | Tactical synthesis | A-share addition / partial replacement. |
| `/tos-funder-macro-topdown` | `stanley_druckenmiller.py`, macro fragments | Partial proxy. |
| `/tos-funder-portfolio` | `portfolio_manager.py` | Covered as final-action synthesizer. |
| `/tos-funder-stock-research` | No exact original equivalent | A-share-specific workspace orchestrator. |

Missing command candidates:

- `/tos-funder-value-munger`
- `/tos-funder-value-burry`
- `/tos-funder-value-pabrai`
- `/tos-funder-growth-cathie-wood`
- `/tos-funder-tactical-ackman`
- `/tos-funder-macro-druckenmiller`
- `/tos-funder-macro-jhunjhunwala`
- `/tos-funder-tactical-taleb`
- `/tos-funder-quant-valuation`
- `/tos-funder-quant-valuation-damodaran`
- Optional after data source upgrade: `/tos-funder-news-sentiment`

## Data API Coverage

Original data API source: `Reference/ai-hedge-fund/src/tools/api.py`.

| Original API | Current replacement | Status | Notes |
|---|---|---|---|
| `get_prices` | `/tos-funder-quant-price-series` via `hoxit market bars --adjust qfq` | Covered | Current path is primary for technical/risk. |
| `get_financial_metrics` | iWencai finance/market/basicinfo packs | Covered with field caveats | Good for many profitability/growth/valuation fields; documented in `01-interface-coverage.md`. |
| `search_line_items` | iWencai finance queries split into narrow packs | Covered with field caveats | Some line items require compute/fallback. |
| `get_market_cap` | iWencai basicinfo/market | Covered | Use dated market cap when available. |
| `get_insider_trades` | Announcement/management proxy | Partial / weak | A-share equivalent is not structured; management route validated dead. Needs announcement text mining. |
| `get_company_news` | Announcement/report search | Partial | Official announcements/reports covered; generic external news source not covered. |
| `prices_to_df`, `get_price_data` | Local normalization in price-series workflow | Covered conceptually | No direct Python adapter port; represented as command protocol. |

Important data gaps already documented:

- `event` route is blocked/dead for structured event data.
- `business` route is blocked/dead in validation.
- Management/insider structured fields are not reliable.
- Generic news coverage is missing unless a Chinese news adapter is added.
- Some debt/cash/EV/EBITDA fields are partial and require assumptions.

## Runtime / App Coverage

| Original capability | Current skill status | Recommendation |
|---|---|---|
| LangGraph analyst workflow | Explicitly not ported | Keep excluded unless the project changes from skill-first to runtime-first. |
| CLI analyst selection | Replaced by slash-style command routing | Covered at skill level. |
| `--show-reasoning`, analyst graph visualization | Not migrated | Optional only; could be approximated in output trace fields. |
| FastAPI backend | Not migrated | Keep excluded from skill unless a local web UI is desired. |
| React/Vite flow builder | Not migrated | Keep excluded. |
| API key storage / model provider UI / Ollama management | Not migrated | Keep excluded; skill uses Claude Code and hoxit env. |
| Flow run persistence | Partially replaced by `/tos-funder-stock-research` workspace | Covered for research notes, not app state. |

## Backtesting and v2 Quant Gaps

Original areas not currently migrated:

| Original module | Capability | Current skill status | Gap |
|---|---|---|---|
| `src/backtesting/engine.py` | Historical simulation | Missing | No `/tos-funder-backtest`. |
| `src/backtesting/metrics.py` | Performance metrics | Missing | No CAGR/Sharpe/Sortino/drawdown report command. |
| `src/backtesting/portfolio.py`, `trader.py` | Portfolio accounting and trade execution | Missing | Portfolio command is decision synthesis only, not simulated execution. |
| `src/backtesting/benchmarks.py` | Benchmark comparison | Missing | No CSI300/industry benchmark workflow. |
| `v2/event_study` | CARs, event windows, bootstrap CI | Missing | Strong candidate for A-share event validation once announcement events are structured. |
| `v2/validation` | CPCV/PBO | Missing | No model validation workflow. |
| `v2/portfolio` | Optimization | Missing | No mean-variance/risk-parity/Black-Litterman workflow. |
| `v2/pipeline/execution.py` | Market impact/capacity simulation | Missing | No execution/capacity command. |

Recommendation: treat these as a separate “tos-funder-quant-lab” phase, not as missing analyst commands. They require code/tooling rather than reference-only skill docs.

## Documentation Inconsistencies Found

| File | Issue | Recommended fix |
|---|---|---|
| `docs/03-build-plan.md` | Phase 2/4 still lists many persona commands, but command set only implements Buffett/Graham/Fisher/Lynch plus proxies. | Mark missing persona commands explicitly or revise build plan to say they were folded into proxies. |
| `tos-funder/references/agent-taxonomy.md` | Value row says `tos-funder-value-*` but only Buffett/Graham exist; tactical row lists names whose persona commands do not exist. | Add per-agent status markers like Growth row already does. |
| `tos-funder/commands/tos-funder-analyze.md` | Value routing says “Munger/Burry/Pabrai when implemented”; tactical/macro routing hides the fact that Ackman/Druckenmiller/Jhunjhunwala/Taleb are proxy-only. | Add explicit “proxy coverage, not persona parity” note. |
| `docs/01-interface-coverage.md` | Agent-level coverage has “Initial implementation status” entries that read like future implementation status, not actual command inventory. | Add a separate “actual command exists?” column. |

## Recommended Migration Backlog

Priority 1: close explicit persona omissions that the existing plan still promises.

1. Add `/tos-funder-value-munger`.
2. Add `/tos-funder-value-burry`.
3. Add `/tos-funder-value-pabrai`.
4. Update `agent-taxonomy.md`, `03-build-plan.md`, and `01-interface-coverage.md` with actual command status.

Priority 2: add valuation layer used by multiple downstream commands.

1. Add `/tos-funder-quant-valuation`.
2. Add `/tos-funder-quant-valuation-damodaran` or fold Damodaran into the generic valuation command as a named methodology.
3. Update portfolio synthesis to optionally consume valuation as a separate thesis input.

Priority 3: decide whether tactical names should be personas or proxies.

1. Either add `/tos-funder-tactical-ackman`, `/tos-funder-macro-druckenmiller`, `/tos-funder-macro-jhunjhunwala`, `/tos-funder-tactical-taleb`.
2. Or explicitly document that current tactical/macro commands are A-share proxies replacing those persona agents, not one-to-one migrations.

Priority 4: add Cathie Wood only after report/concept data sourcing is stable.

1. Add `/tos-funder-growth-cathie-wood`.
2. Use concept/theme routes, R&D intensity, report narratives, industry growth, and valuation caps.

Priority 5: separate research workflow from quant lab.

1. Add `/tos-funder-backtest` only if hoxit can provide stable historical price/fundamental point-in-time data.
2. Add event-study workflow after announcement event extraction exists.
3. Leave web app/runtime migration out of scope unless a UI is explicitly requested.

## Bottom Line

The current skill is a strong A-share research workflow, but it is not a complete migration of `Reference/ai-hedge-fund`.

The most important missing skills are the persona workflows that the migration plan still names but did not implement: Munger, Burry, Pabrai, Cathie Wood, Ackman, Druckenmiller, Jhunjhunwala, Taleb, Damodaran, and standalone valuation. The largest non-persona gap is backtesting/v2 quant-lab functionality.
