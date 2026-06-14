# Migration Status Board

Date: 2026-06-10

Master plan: `docs/tos-funder/15-complete-migration-plan.md`

Execution binding: `docs/tos-funder/18-hoxit-execution-binding.md`

Status enum:

- `covered`: implemented as a command/reference and routable.
- `proxy`: represented by a broader A-share proxy, not one-to-one parity.
- `missing`: not implemented.
- `planned`: in the complete migration plan.
- `excluded`: deliberately out of skill scope.

Important: `covered` means POS skill parity, not standalone executable parity. hoxit executable binding is tracked separately in `18-hoxit-execution-binding.md`.

## Analyst Parity

| Original module | Original key | Target command / replacement | Status | Target phase |
|---|---|---|---|---|
| `warren_buffett.py` | `warren_buffett` | `/tos-funder-value-buffett` | covered | done |
| `ben_graham.py` | `ben_graham` | `/tos-funder-value-graham` | covered | done |
| `charlie_munger.py` | `charlie_munger` | `/tos-funder-value-munger` | covered | done |
| `michael_burry.py` | `michael_burry` | `/tos-funder-value-burry` | covered | done |
| `mohnish_pabrai.py` | `mohnish_pabrai` | `/tos-funder-value-pabrai` | covered | done |
| `phil_fisher.py` | `phil_fisher` | `/tos-funder-growth-fisher` | covered | done |
| `peter_lynch.py` | `peter_lynch` | `/tos-funder-growth-lynch` | covered | done |
| `cathie_wood.py` | `cathie_wood` | `/tos-funder-growth-cathie-wood` | covered | done |
| `bill_ackman.py` | `bill_ackman` | `/tos-funder-tactical-ackman` | covered | done |
| `stanley_druckenmiller.py` | `stanley_druckenmiller` | `/tos-funder-macro-druckenmiller` | covered | done |
| `rakesh_jhunjhunwala.py` | `rakesh_jhunjhunwala` | `/tos-funder-macro-jhunjhunwala` | covered | done |
| `nassim_taleb.py` | `nassim_taleb` | `/tos-funder-tactical-taleb` | covered | done |
| `aswath_damodaran.py` | `aswath_damodaran` | `/tos-funder-quant-valuation-damodaran` | covered | done |
| `valuation.py` | `valuation_analyst` | `/tos-funder-quant-valuation` | covered | done |
| `fundamentals.py` | `fundamentals_analyst` | `/tos-funder-quant-fundamentals` | covered | done |
| `growth_agent.py` | `growth_analyst` | `/tos-funder-growth` or `/tos-funder-quant-growth` | proxy | Phase 3 decision |
| `technicals.py` | `technical_analyst` | `/tos-funder-quant-technicals` | covered | done |
| `sentiment.py` | `sentiment_analyst` | `/tos-funder-quant-sentiment` | proxy | Phase 5 |
| `news_sentiment.py` | `news_sentiment_analyst` | `/tos-funder-news-sentiment` | proxy | done |
| `risk_manager.py` | `risk_manager` | `/tos-funder-risk-manager` | covered | done |
| `portfolio_manager.py` | `portfolio_manager` | `/tos-funder-portfolio` | covered | done |

## Current Command Inventory

| Command | Status | Notes |
|---|---|---|
| `/tos-funder-preflight` | covered | A-share addition. |
| `/tos-funder-stock-research` | covered | Skill-native workspace replacement for run persistence. |
| `/tos-funder-analyze` | covered | Needs expansion after new persona commands. |
| `/tos-funder-portfolio` | covered | Needs expanded signal consumption after new persona commands. |
| `/tos-funder-value-buffett` | covered | Original persona parity. |
| `/tos-funder-value-graham` | covered | Original persona parity. |
| `/tos-funder-growth` | proxy | Aggregates growth family; not one-to-one original `growth_agent.py` parity. |
| `/tos-funder-growth-fisher` | covered | Original persona parity. |
| `/tos-funder-growth-lynch` | covered | Original persona parity. |
| `/tos-funder-quant-fundamentals` | covered | Original generic analyst parity. |
| `/tos-funder-quant-price-series` | covered | Replacement for original price API and normalizer. |
| `/tos-funder-quant-technicals` | covered | Original generic analyst parity. |
| `/tos-funder-quant-sentiment` | proxy | Announcement/report sentiment, not full news/insider parity. |
| `/tos-funder-risk-manager` | covered | Original risk manager parity with A-share additions. |
| `/tos-funder-tactical` | proxy | A-share tactical synthesis, not original persona parity. |
| `/tos-funder-tactical-catalyst` | proxy | Infrastructure for Ackman/Burry/Druckenmiller-style catalysts. |
| `/tos-funder-tactical-tail-risk` | proxy | Infrastructure for Taleb/risk workflows. |
| `/tos-funder-macro-topdown` | proxy | Conservative macro context, not full Druckenmiller parity. |

## Data API Parity

| Original API | Replacement | Status | Follow-up |
|---|---|---|---|
| `get_prices` | `/tos-funder-quant-price-series`, hoxit market bars | covered | Keep corporate-action checks current. |
| `get_financial_metrics` | iWencai finance/market/basicinfo packs | covered | Maintain field caveats. |
| `search_line_items` | iWencai finance narrow queries | covered | Keep mapping in `01-interface-coverage.md`. |
| `get_market_cap` | iWencai basicinfo/market | covered | Use dated value when available. |
| `get_insider_trades` | announcement/management proxy | proxy | Needs announcement text mining for stronger parity. |
| `get_company_news` | announcement/report search | proxy | Add external news route before claiming full news sentiment. |
| `prices_to_df`, `get_price_data` | price-series command protocol | covered | Optional helper script if backtesting needs code reuse. |

## Backtesting and Quant Lab

| Original area | Target | Status | Target phase |
|---|---|---|---|
| `src/backtesting/engine.py` | `/tos-funder-backtest` | planned | Phase 7 |
| `src/backtesting/metrics.py` | `/tos-funder-backtest-metrics` | planned | Phase 7 |
| `src/backtesting/benchmarks.py` | `/tos-funder-backtest-benchmark` | planned | Phase 7 |
| `src/backtesting/portfolio.py`, `trader.py` | backtest helper scripts | planned | Phase 7 |
| `v2/event_study` | `/tos-funder-event-study` | planned | Phase 8 |
| `v2/validation` | `/tos-funder-signal-validate` | planned | Phase 8 |
| `v2/portfolio` | `/tos-funder-portfolio-optimize` | planned | Phase 8 |
| `v2/pipeline` | `/tos-funder-execution-sim` | planned | Phase 8 |

## Runtime and App

| Original feature | Skill treatment | Status | Notes |
|---|---|---|---|
| LangGraph runtime | skill command orchestration | excluded | Do not port unless runtime-first architecture is requested. |
| CLI analyst selector | slash command routing | covered | Expand as new commands land. |
| FastAPI backend | no skill port | excluded | Reassess only if UI/API is requested. |
| React flow builder | no skill port | excluded | Could be replaced by diagram output later. |
| API key/model UI/Ollama manager | env/hoxit config | excluded | Not needed for skill-first workflow. |
| Flow run persistence | stock research workspace | proxy | Covered for notes/files, not app DB state. |
