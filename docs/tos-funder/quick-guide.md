# Trading Funder Quick Guide

Updated: 2026-06-03 13:45:00 Asia/Shanghai

This guide is the fast re-entry document for continuing the `tos-funder` project after context loss.

## Current Role Split

Codex acts as project manager, architect, and reviewer.

Responsibilities:

- define PR scope and acceptance criteria
- write CC instruction files under `docs/tos-funder/audit/`
- review CC delivery without directly changing implementation unless explicitly asked
- append review findings to the relevant audit file
- preserve architecture consistency across commands, references, schemas, and validation docs

CC acts as implementation agent.

Responsibilities:

- read the instruction file
- implement commands/references/validation docs
- run required `rg` checks
- append or report delivery summary
- respond to review findings with fix summaries

## Working Pattern

1. Codex creates an instruction file:
   - location: `docs/tos-funder/audit/`
   - filename format: `pr<id>-<short-topic>-instruction-<timestamp>.md`

2. User gives that instruction to CC.

3. CC implements and reports completion.

4. Codex reviews:
   - inspect files with `rg`, `sed`, and targeted reads
   - do not directly fix implementation during review
   - write findings to:
     `docs/tos-funder/audit/pr<id>-<short-topic>-review-<timestamp>.md`
   - if fixes are needed, include exact CC fix instructions in the review file

5. CC fixes.

6. Codex appends re-audit notes to the same review file.

7. PR is accepted only when:
   - command logic matches reference logic
   - schema is consumable downstream
   - validation examples match command rules
   - no dead routes are used
   - no new enum drift appears
   - data-quality artifacts are not treated as real market signals

## Current Progress

Accepted (all PRs):

- PR1 interface coverage correction
- PR2A Buffett/Graham validation and fixes
- PR5B growth aggregate fixes
- PR6A price-series/technicals using mootdx/TDX
- PR8A tactical catalyst proxy
- PR9A tactical tail-risk proxy
- PR9B tactical synthesizer
- PR10A macro/top-down proxy
- PR10B portfolio/decision synthesizer
- PR11 final hardening
- PR12 stock research workspace
- PR13 explicit preflight screening

Important accepted audit files:

- `docs/tos-funder/audit/pr5b-20260603-001015.md`
- `docs/tos-funder/audit/pr8a-tactical-catalyst-review-20260603-002834.md`
- `docs/tos-funder/audit/pr9a-tactical-tail-risk-review-20260603-084817.md`
- `docs/tos-funder/audit/pr9b-tactical-synthesizer-review-20260603-102419.md`
- `docs/tos-funder/audit/pr10a-macro-topdown-proxy-review-20260603-110349.md`
- `docs/tos-funder/audit/pr10b-portfolio-decision-synthesizer-review-20260603-114954.md`
- `docs/tos-funder/audit/pr11-final-hardening-instruction-20260603-124127.md`
- `docs/tos-funder/audit/pr13-preflight-screening-instruction-20260605-000000.md`

Current delivery:

- PR13 Explicit Preflight Screening — completed
- Next action: use `/tos-funder-preflight` before expensive stock research when cost control is desired; otherwise `/tos-funder-stock-research` keeps PR12 default behavior.

## Completed PR Roadmap

---

### PR13 Explicit Preflight Screening

Purpose:

- add an explicit low-cost screening command before expensive multi-agent research
- produce `skip`, `watch`, `deep_dive`, or `blocked` routing decisions
- preserve reusable price-series, fundamentals, and sentiment outputs for later full research
- keep `/tos-funder-stock-research` default behavior unchanged

Expected files:

- `tos-funder/commands/tos-funder-preflight.md`
- `tos-funder/references/preflight-screening.md`
- `docs/tos-funder/validation-pr13.md`

Status:

- accepted

### PR9A Tactical Tail-Risk Proxy

Purpose:

- add downside-risk/event-risk layer
- complement PR8A catalyst opportunity layer
- produce `tail_risk_signal`
- no `final_action`

Status:

- accepted

### PR9B Tactical Synthesizer

Purpose:

- combine `tactical_catalyst_signal` and `tail_risk_signal`
- produce a tactical-level synthesis
- avoid duplicate tactical conclusions across commands
- still no final portfolio action

Expected files:

- `tos-funder/references/tactical-synthesis.md`
- `tos-funder/commands/tos-funder-tactical.md`
- `docs/tos-funder/validation-pr9b.md`

Status:

- accepted

### PR10A Macro/Top-Down Proxy

Purpose:

- lightweight A-share top-down proxy
- use index trend, sector strength, market breadth, style rotation, risk appetite
- do not attempt full macro prediction because current data infrastructure lacks reliable macro APIs

Expected stance:

- implement after PR9A/PR9B
- keep Druckenmiller-style logic constrained by available data

Expected files:

- `tos-funder/references/macro-topdown.md`
- `tos-funder/commands/tos-funder-macro-topdown.md`
- `docs/tos-funder/validation-pr10a.md`

Status:

- accepted

### PR10B Portfolio/Decision Synthesizer

Purpose:

- unify value, growth, quant, sentiment, tactical, risk, and portfolio consumption
- clarify conflict resolution and confidence caps
- enforce data-quality veto vs risk veto separation

Expected files:

- update `tos-funder/commands/tos-funder-portfolio.md`
- update `tos-funder/references/portfolio-synthesis.md`
- update `tos-funder/references/output-schema-examples.md`
- create `docs/tos-funder/validation-pr10b.md`

Status:

- accepted

### PR12 Stock Research Workspace

Purpose:

- add persistent per-stock research workspaces
- support full redundant, incremental, and refresh analysis modes
- write structured per-layer reports to `outputs/stocks/<股票名>-<代码>/`
- maintain `_state.json`, `_index.md`, and per-run `_manifest.json`

Expected files:

- `tos-funder/commands/tos-funder-stock-research.md`
- `tos-funder/references/stock-research-workspace.md`
- `docs/tos-funder/validation-pr12.md`

Status:

- accepted

### PR11 Final Hardening

Purpose:

- full schema/routing/validation cleanup
- check enum consistency
- check command frontmatter
- check dead-route usage
- check iWencai vs mootdx boundary
- consolidate documentation and audit trail

Expected files:

- update `tos-funder/SKILL.md` if routing gaps are found
- update `tos-funder/commands/*.md` only for active contradictions
- update `tos-funder/references/*.md` only for schema/routing/data-boundary contradictions
- update `docs/tos-funder/quick-guide.md`
- create `docs/tos-funder/validation-pr11.md`

Status:

- completed

## Architecture Principles

1. Skills are orchestration and context.
2. Commands carry executable workflow logic.
3. References carry reusable frameworks, schemas, and strategy theory.
4. Validation docs prove behavior against samples.
5. Audit docs preserve PM/architect review history and CC instructions.

## Data Source Boundaries

iWencai is primary for:

- fundamentals
- valuation fields
- announcements
- research reports
- broad A-share natural-language queries

mootdx/TDX is primary for:

- OHLCV
- technical indicators
- risk metrics
- correlation/portfolio price-series workflows

iWencai OHLCV is fallback only.

Dead or blocked routes:
- `business`
- `event query2data`
- `management` insider fields: 高管持股 / 质押 / 减持 / 股权激励

Allowed validated `management` fields:
- 分红
- 股本
- 股东人数
- 回购 / 总股本 / 流通A股 where already documented in accepted value/fundamental commands

Rule:
- Do not use management for insider/pledge/reduction/incentive fields.
- Narrow validated management queries are allowed when already documented in accepted commands.

## Review Checklist For Every PR

Run targeted checks:

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder docs/tos-funder
rg -n "query2data|query -r event|query -r business|query -r management" tos-funder/commands
rg -n "final_action" tos-funder/commands/<new-command>.md
rg -n "confidence\": \\{" tos-funder/references/output-schema-examples.md tos-funder/commands
```

Check manually:

- Does command frontmatter declare consumed and produced schema?
- Does `output-schema-examples.md` have a matching anchor?
- Does `skill-workflow.md` route the schema?
- Does `SKILL.md` expose the command?
- Does `tos-funder-analyze.md` know when to use it?
- Do validation samples use `source_status`?
- Are assumptions separated from live or accepted validation?
- Are data-quality artifacts separated from real signals?

## Next Action

Use tos-funder in practice and collect issues into the next improvement PR.

See `docs/tos-funder/usage-strategy.md` for the full practical usage strategy and command cheatsheet.
See `docs/tos-funder/scan-workflow-strategy.md` for the proposed scan workflow (redundant/incremental analysis with output persistence).
