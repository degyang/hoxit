# CC Collaboration Plan

This project should be implemented as a sequence of small PRs. Codex acts as architect and validator. Claude Code can be used as implementation worker for command/reference expansion and adapter tests.

## Roles

| Role | Responsibility |
|---|---|
| Codex architect/validator | Own architecture, review scope, verify interface coverage, reject over-porting, run final acceptance. |
| Claude Code implementer | Implement assigned PR tasks, follow docs, create/update commands and references, run requested validation cases. |
| User | Approve priorities, evaluate practical usefulness in real workflow. |

## Coordination Rules

- Do not ask CC to port LangGraph, FastAPI, React, or the original CLI platform.
- Give CC one PR-sized task at a time.
- Every CC task must name exact files to touch.
- Every CC output must include changed files, validation cases, missing fields, and unresolved questions.
- Every CC task must require reading `docs/tos-funder/07-cc-working-constitution.md` before implementation.
- Codex reviews against `docs/tos-funder/01-interface-coverage.md` and `tos-funder/references/skill-workflow.md`.

## PR Plan

### PR 1: Interface Adapter Matrix and Query Packs

Goal: Make iWencai coverage executable and testable.

Files:

- `docs/tos-funder/01-interface-coverage.md`
- `tos-funder/references/iwencai-adapter.md`

Tasks:

- Verify each query pack on the five sample A-share cases.
- Record missing fields and query rewrites.
- Mark each original API field as A/B/C/D.

Acceptance:

- Each sample has route list, returned fields, missing fields, and fallback recommendation.
- No unsupported field is silently treated as available.

### PR 2: Value Investor Commands

Goal: Implement the value family as skill commands.

Files:

- `tos-funder/commands/tos-funder-value-buffett.md`
- `tos-funder/commands/tos-funder-value-graham.md`
- `tos-funder/commands/tos-funder-value-munger.md`
- `tos-funder/commands/tos-funder-value-pabrai.md`
- `tos-funder/commands/tos-funder-value-burry.md`
- `tos-funder/references/value-investors.md`

Tasks:

- Extract scoring and persona prompts from source.
- Map data requirements to iWencai query packs.
- Define missing-data behavior.
- Provide one sample output for each command.

Acceptance:

- Each command separates deterministic facts from persona reasoning.
- Each command uses A-share action verbs.
- Buffett remains consistent with the source 27-point model.

### PR 3: Quant Fundamentals and Valuation

Goal: Implement deterministic factor commands that other agents can consume.

Files:

- `tos-funder/commands/tos-funder-quant-fundamentals.md`
- `tos-funder/commands/tos-funder-quant-valuation.md`
- `tos-funder/references/quant-systematic.md`

Tasks:

- Port formulas, not runtime.
- Add sector-adjusted valuation notes.
- Validate against 宁波银行、贵州茅台、比亚迪.

Acceptance:

- Deterministic outputs are auditable.
- No LLM persona prompt is used except Damodaran when later added.

### PR 4: Insider/Event/News Proxy Layer

Goal: Replace `get_insider_trades` and `get_company_news` with A-share-native proxies.

Files:

- `tos-funder/references/iwencai-adapter.md`
- `tos-funder/references/sentiment-event-proxy.md`
- optional commands under `tos-funder/commands/tos-funder-quant-sentiment.md`

Tasks:

- Define insider proxy scoring.
- Define announcement/report sentiment scoring.
- Separate official facts from analyst opinions.

Acceptance:

- Munger/Fisher/Lynch/Burry/Taleb can consume proxy fields.
- Output labels proxy confidence.

### PR 5: Growth and Tactical Families

Goal: Implement persona commands that depend on PR 4 proxies.

Files:

- Growth commands and references.
- Tactical commands and references.

Tasks:

- Implement Fisher, Lynch, Cathie Wood.
- Implement Ackman, Druckenmiller, Jhunjhunwala.
- Leave Taleb blocked or partial until price-series support is accepted.

Acceptance:

- Every command declares data coverage and missing fields.
- Catalyst and macro claims use announcement/report/market route evidence.

### PR 6: TDX Price-Series Adapter and Technical/Risk Commands

Goal: Implement technical/risk workflows on top of hoxit `mootdx`/TDX price series.

Files:

- `tos-funder/references/price-series.md`
- `tos-funder/commands/tos-funder-quant-price-series.md`
- `tos-funder/commands/tos-funder-quant-technicals.md`
- `tos-funder/commands/tos-funder-portfolio.md`

Tasks:

- Use `.venv/bin/hoxit market bars <CODE> --category 4 --offset 250 --adjust qfq` as the daily OHLCV source.
- Use weekly/monthly/minute categories when needed by tactical or kanpan workflows.
- Canonicalize `mootdx` rows into `{date, datetime, open, high, low, close, volume, amount}`.
- Compute RSI, MACD, MA, ATR, volatility, drawdown, and correlation locally from OHLCV.
- Keep iWencai OHLCV as fallback only and label it `source: iwencai_fallback`.

Acceptance:

- Technicals and risk manager work on TDX price series or explicitly return `blocked`.
- Commands do not rely on iWencai precomputed RSI/MACD as the primary signal source.

### PR 7: Portfolio Synthesis

Goal: Combine analyst outputs into A-share-compatible actions.

Files:

- `tos-funder/commands/tos-funder-portfolio.md`
- `tos-funder/references/portfolio-synthesis.md`

Tasks:

- Define signal aggregation.
- Define allowed actions.
- Add risk caps and conflict handling.

Acceptance:

- No unsupported `short/cover` default.
- Portfolio output includes allowed actions and rejected actions with reasons.

## CC Task Template

Use this prompt shape when delegating to Claude Code:

```text
You are implementing PR <N> for hoxit tos-funder.

Read:
- docs/tos-funder/07-cc-working-constitution.md
- <specific docs>
- <specific source agent files>

Touch only:
- <specific files>

Deliver:
1. Code/doc changes.
2. A short implementation note.
3. Validation on <sample stocks>.
4. Missing iWencai fields and fallback proposal.
5. Self-review against `docs/tos-funder/07-cc-working-constitution.md`.

Constraints:
- Do not port LangGraph/FastAPI/React/original CLI.
- Use skill/commands/references only.
- Use iWencai first for fundamentals/announcements/reports; use hoxit `market bars` first for OHLCV/technical/risk data.
- Separate deterministic facts from persona reasoning.
- Do not introduce new primary signal enums; use `signal + strength`.
- Do not turn degraded metrics into hard vetoes without a data-quality check.
```

## Review Checklist for Codex

- Scope stayed within assigned files.
- No platform migration slipped in.
- Data-source coverage is explicit: iWencai for fundamentals/events, TDX/mootdx for prices.
- Missing fields are documented.
- A-share semantics are respected.
- Output schema matches `skill-workflow.md`.
- Sample validation is reproducible.
