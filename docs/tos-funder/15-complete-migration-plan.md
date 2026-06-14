# Complete Migration Plan

Date: 2026-06-10

Objective: move `skills-tos-funder` from a compressed A-share adaptation of `Reference/ai-hedge-fund` to a complete, explicit migration of the original project capabilities that are useful in a Claude Code skill environment.

This plan is based on `docs/tos-funder/14-ai-hedge-fund-migration-gap-audit.md`.

Execution rule: follow `docs/tos-funder/17-incremental-skill-migration-design.md`. The full plan below is a capability map, not permission to create duplicate runtimes or parallel registries.

## Simplified Execution Plan

The framework is already in place. Use this reduced plan as the active execution model:

1. **Agent Parity**: every original `src/agents/*.py` analyst has a routed command or explicit proxy replacement. Verified by hoxit test `tests/test_tos_funder_migration.py`.
2. **Analytical Depth**: each newly added command gets real A-share validation samples, scoring refinements, and documented data gaps.
3. **Orchestration Integration**: `/tos-funder-analyze`, `/tos-funder-stock-research`, and `/tos-funder-portfolio` consume the expanded signal set without prose parsing.
4. **Quant Lab**: backtesting, event study, validation, optimizer, and execution simulation are added after signal schemas stabilize.

The detailed phases below are retained as implementation notes, not as a large sequential dependency chain.

## Definition of Complete Migration

Complete migration means:

1. Every original `src/agents` analyst has either:
   - a dedicated `tos-funder` command, or
   - an explicit documented replacement command with schema-compatible output and a clear reason why one-to-one migration is not useful.
2. Every original `src/tools/api.py` data capability has an A-share replacement path, fallback rule, and missing-data behavior.
3. Portfolio synthesis consumes all migrated signal families without prose parsing.
4. Backtesting and v2 quant-lab capabilities are either implemented as separate commands/tools or explicitly classified as out of scope with rationale.
5. Runtime/app features are treated deliberately: skill-native replacements first, UI/runtime ports only if needed.

Complete migration does not mean copying original Python/LangGraph/web code verbatim. The target architecture remains skill-first and hoxit-powered.

## Migration Tracks

| Track | Purpose | Output type |
|---|---|---|
| A. Parity Governance | Lock inventory, status, schemas, and routing docs | docs/reference updates |
| B. Persona Analyst Parity | Add all missing original analyst workflows | command + reference docs |
| C. Valuation and Data Parity | Add standalone valuation, Damodaran, and stronger data adapters | command + reference docs |
| D. Signal Integration | Make analyze/portfolio consume all new signals safely | command/reference updates |
| E. Backtesting and Quant Lab | Port original simulation/v2 research stack where feasible | commands and optional helper scripts |
| F. Runtime/App Decision | Decide whether web/runtime features need skill-native equivalents | docs and optional app plan |

## Phase 0: Governance Reset

Goal: make the migration state impossible to misread.

Deliverables:

- Update `docs/03-build-plan.md` to point to this complete plan as the current master plan.
- Update `tos-funder/references/agent-taxonomy.md` with exact per-agent status: `covered`, `missing`, `proxy`, `deferred`, `excluded`.
- Update `docs/01-interface-coverage.md` with an `Actual command exists?` column.
- Add a `docs/tos-funder/16-migration-status-board.md` checklist that tracks all original agents, APIs, backtesting modules, v2 modules, and app/runtime features.

Acceptance:

- A new contributor can answer “what remains unmigrated?” from one status board.
- No doc says an agent is implemented unless a command file exists or an explicit proxy replacement is named.

## Phase 1: Value Persona Completion

Goal: finish the original value-family analyst parity.

Commands to add:

- `/tos-funder-value-munger`
- `/tos-funder-value-burry`
- `/tos-funder-value-pabrai`

Reference updates:

- Expand `tos-funder/references/value-investors.md` with Munger, Burry, and Pabrai sections.
- Add output examples to `tos-funder/references/output-schema-examples.md` or document that these commands use the shared value signal schema.
- Update `/tos-funder-analyze` value routing.
- Update `/tos-funder-portfolio` thesis layer weights.

Implementation intent:

| Command | Core lens | A-share data route |
|---|---|---|
| Munger | quality compounder, moat, management quality, behavioral risk | finance, basicinfo, announcements, reports |
| Burry | contrarian cheapness, stress, downside/catalyst awareness | valuation, balance sheet, risk events, price-series |
| Pabrai | low downside/high upside, simple business, margin of safety | valuation, cash/debt, FCF, announcements |

Acceptance:

- Each command has deterministic scoring, missing-data behavior, A-share action constraints, and one validated sample.
- Portfolio synthesis can consume these signals without breaking existing Buffett/Graham behavior.

## Phase 2: Valuation Core and Damodaran

Goal: stop scattering valuation logic across persona commands.

Commands to add:

- `/tos-funder-quant-valuation`
- `/tos-funder-quant-valuation-damodaran`

Reference updates:

- Add `tos-funder/references/valuation-models.md`.
- Update `quant-systematic.md`, `portfolio-synthesis.md`, and output schema examples.

Implementation intent:

| Command | Role | Required outputs |
|---|---|---|
| Quant valuation | Shared deterministic valuation layer | PE/PB/PS/PEG/FCF yield, EV fallback, sector-relative valuation, confidence |
| Damodaran | DCF/intrinsic valuation methodology | revenue/cash-flow assumptions, WACC proxy, terminal value, sensitivity table, fair value band |

Key constraints:

- If cash/debt/EV fields are missing, output `valuation_status=partial`, not false precision.
- DCF output must show assumption bands, not a single fake-precise target price.
- For financials, use sector-specific valuation logic; do not force industrial FCFF models onto banks.

Acceptance:

- `/tos-funder-portfolio` can optionally consume valuation as a thesis input.
- Buffett/Graham/Munger/Pabrai commands can reference valuation output instead of duplicating all valuation logic.

## Phase 3: Growth Persona Completion

Goal: finish original growth family parity.

Commands to add:

- `/tos-funder-growth-cathie-wood`
- Optional: `/tos-funder-quant-growth` if generic `growth_agent.py` needs standalone parity beyond current `/tos-funder-growth` aggregator.

Reference updates:

- Expand `growth-investors.md` Cathie Wood section from future note to full command spec.
- Update `/tos-funder-growth` aggregator to optionally consume Cathie Wood and generic quant-growth signals.

Implementation intent:

| Command | Core lens | A-share substitutions |
|---|---|---|
| Cathie Wood | disruptive innovation, TAM, exponential adoption, R&D intensity | concepts/themes, reports, R&D, revenue growth, industry context |
| Quant growth | generic growth factor model | revenue/EPS/FCF growth, margin expansion, reinvestment, PEG reliability |

Acceptance:

- Growth aggregator records consumed sub-signals and conflict resolution across Fisher, Lynch, Cathie Wood, quant fundamentals, quant sentiment.
- Cathie Wood cannot override valuation/data-quality hard gates by narrative alone.

## Phase 4: Tactical and Macro Persona Completion

Goal: decide and implement persona parity instead of leaving proxies ambiguous.

Commands to add:

- `/tos-funder-tactical-ackman`
- `/tos-funder-macro-druckenmiller`
- `/tos-funder-macro-jhunjhunwala`
- `/tos-funder-tactical-taleb`

Existing proxies remain:

- `/tos-funder-tactical-catalyst`
- `/tos-funder-tactical-tail-risk`
- `/tos-funder-tactical`
- `/tos-funder-macro-topdown`

Implementation intent:

| Command | Core lens | Relationship to existing proxy |
|---|---|---|
| Ackman | activist catalyst, governance, concentrated quality | consumes catalyst proxy plus fundamentals/valuation |
| Druckenmiller | macro trend, liquidity, sector leadership | consumes macro-topdown plus price-series/sector strength |
| Jhunjhunwala | domestic growth, macro tailwind, emerging-market compounding | consumes macro-topdown plus growth/fundamentals |
| Taleb | fragility, convexity, barbell, via negativa | consumes tail-risk proxy plus balance sheet/optionality |

Acceptance:

- Proxies remain deterministic infrastructure; persona commands produce analyst signals.
- `/tos-funder-tactical` can either stay proxy synthesis or be upgraded to consume persona tactical signals.
- Portfolio can distinguish `macro_context`, `tactical_proxy`, and `persona_tactical` signals.

## Phase 5: Sentiment and News Parity

Goal: make sentiment parity honest rather than treating announcement/report search as full news coverage.

Commands/options:

- Keep `/tos-funder-quant-sentiment` as official announcement/report sentiment.
- Add `/tos-funder-news-sentiment` if hoxit has or gains a reliable Chinese company-news source.
- Add `sentiment_source_coverage` and `news_coverage_status` fields to sentiment outputs.

Reference updates:

- Expand `sentiment-event-proxy.md` with distinction between:
  - official disclosure sentiment,
  - research-report opinion,
  - external media/news,
  - insider/management proxy.

Acceptance:

- No output claims full news sentiment unless external news is actually queried.
- Portfolio confidence is capped when sentiment only covers official announcements/reports.

## Phase 6: Analyze and Portfolio Full Integration

Goal: upgrade the orchestration layer after all major signal families exist.

Updates:

- `/tos-funder-analyze` supports all original analysts by name and family.
- `/tos-funder-stock-research` full mode runs the expanded command list with configurable depth.
- `/tos-funder-portfolio` consumes:
  - value: Buffett, Graham, Munger, Burry, Pabrai
  - growth: Fisher, Lynch, Cathie Wood, growth aggregate
  - quant: fundamentals, valuation, Damodaran, technicals, sentiment/news
  - tactical: Ackman, Taleb, catalyst, tail-risk, tactical synthesis
  - macro: Druckenmiller, Jhunjhunwala, macro-topdown
  - risk: risk manager

Acceptance:

- The expanded portfolio command has required/optional input rules.
- Missing optional personas degrade confidence but do not block.
- Missing risk manager still blocks final action.
- At least one full research workspace sample validates the expanded run order.

## Phase 7: Backtesting v1 Migration

Goal: port useful original backtesting capabilities into a hoxit/A-share workflow.

Commands to add:

- `/tos-funder-backtest`
- `/tos-funder-backtest-metrics`
- `/tos-funder-backtest-benchmark`

Possible helper code:

- `tos-funder/scripts/backtest.py`
- `tos-funder/scripts/metrics.py`

Original sources:

- `Reference/ai-hedge-fund/src/backtesting/engine.py`
- `metrics.py`
- `portfolio.py`
- `trader.py`
- `benchmarks.py`
- `controller.py`

Implementation constraints:

- Do not use future fundamentals unless hoxit can provide point-in-time data.
- Start with price-only / signal-file backtesting.
- Use A-share trading constraints: T+1, lot size, limit up/down, suspension handling where data permits.
- Benchmark against CSI300/CSI500/industry index when available.

Acceptance:

- Can replay saved signal files and produce return, max drawdown, volatility, Sharpe-like metric, turnover, win/loss, and benchmark-relative performance.
- Clearly labels whether backtest is signal-only, price-only, or point-in-time fundamental-safe.

## Phase 8: v2 Quant Lab Migration

Goal: migrate the original v2 research stack as optional quant-lab capability.

Commands/modules:

- `/tos-funder-event-study`
- `/tos-funder-signal-validate`
- `/tos-funder-portfolio-optimize`
- `/tos-funder-execution-sim`

Original sources:

- `Reference/ai-hedge-fund/v2/event_study/*`
- `v2/validation/*`
- `v2/portfolio/*`
- `v2/pipeline/*`
- `v2/signals/*`

Implementation order:

1. Event study: announcement/event window CARs using hoxit price bars.
2. Signal validation: purged splits only after signal history is available.
3. Portfolio optimizer: risk parity and simple mean-variance before Black-Litterman.
4. Execution sim: liquidity/capacity approximation from volume/amount.

Acceptance:

- Each quant-lab command states data assumptions and leakage controls.
- No command presents research results as live investment advice without validation status.

## Phase 9: Runtime and App Decision

Goal: decide whether original app/runtime features belong in this skill.

Default stance:

- Do not port LangGraph.
- Do not port React/FastAPI web app into the skill.
- Prefer skill-native command orchestration and stock workspaces.

Possible skill-native replacements:

- Graph visualization as markdown/Excalidraw flow output.
- Run history through `outputs/stocks/<name-code>/`.
- API/model settings via existing environment variables and hoxit configuration.

Escalation trigger for app migration:

- Only consider a UI if the workflow requires interactive flow editing, multi-run dashboards, or non-Codex users.

Acceptance:

- Runtime/app status is explicitly documented as `excluded`, `replaced`, or `planned`.

## Global Acceptance Checklist

Complete migration is done when:

- All original 20 analyst modules are represented by commands or explicit replacements.
- All current and new commands have frontmatter, command usage, data collection, scoring, output schema, missing-data behavior, and validation sample.
- `agent-taxonomy.md`, `01-interface-coverage.md`, `03-build-plan.md`, `docs/tos-funder/14-ai-hedge-fund-migration-gap-audit.md`, and status board agree.
- `/tos-funder-analyze`, `/tos-funder-stock-research`, and `/tos-funder-portfolio` route all implemented commands correctly.
- Backtesting and v2 modules have either working skill-native commands or explicit out-of-scope decisions.
- No command depends on dead routes (`event`, broad `business`, management insider structured fields) without fallback or warning.

## Suggested PR Sequence

| PR | Scope | Files |
|---|---|---|
| PR14 | Governance reset and status board | docs + taxonomy only |
| PR15 | Munger command | value reference, command, schemas, validation |
| PR16 | Burry command | value reference, command, schemas, validation |
| PR17 | Pabrai command | value reference, command, schemas, validation |
| PR18 | Quant valuation command | valuation reference, command, portfolio optional input |
| PR19 | Damodaran command | valuation reference, command, sensitivity schema |
| PR20 | Cathie Wood command | growth reference, command, growth aggregator |
| PR21 | Tactical persona commands I | Ackman, Taleb |
| PR22 | Macro persona commands | Druckenmiller, Jhunjhunwala |
| PR23 | Sentiment/news parity cleanup | sentiment reference, optional news command |
| PR24 | Expanded analyze/portfolio/workspace integration | orchestration commands |
| PR25 | Backtesting v1 minimal port | backtest commands/scripts |
| PR26 | Event study quant-lab | event-study command/script |
| PR27 | Validation/optimizer/execution quant-lab | optional advanced commands |
| PR28 | Final parity audit | docs, status board, end-to-end sample |

## Immediate Next Step

Start with PR14. It is a documentation-only control PR that makes the remaining work explicit before adding more commands.

Minimum PR14 edits:

1. Add `docs/tos-funder/16-migration-status-board.md`.
2. Update `docs/03-build-plan.md` to reference this complete plan.
3. Update `agent-taxonomy.md` with exact current status.
4. Update `01-interface-coverage.md` with actual command status.
