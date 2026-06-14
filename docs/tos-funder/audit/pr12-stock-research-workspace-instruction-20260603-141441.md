# PR12 Instruction: Stock Research Workspace

Created: 2026-06-03 14:14:41 Asia/Shanghai

## Context

PR11 Final Hardening has been accepted.

The current `tos-funder` system has strong analysis commands, but it does not yet behave like a persistent stock research skill. PR12 should add the workspace orchestration layer.

Read first:

- `docs/tos-funder/12-stock-research-workspace.md`
- `docs/tos-funder/quick-guide.md`
- `tos-funder/references/skill-workflow.md`
- `tos-funder/references/output-schema-examples.md`
- `tos-funder/references/portfolio-synthesis.md`

## Objective

Implement the design in `docs/tos-funder/12-stock-research-workspace.md`.

Create a new command:

```text
/tos-funder-stock-research
```

This command should orchestrate existing `tos-funder` commands and maintain per-stock output workspaces under:

```text
outputs/stocks/<股票名>-<代码>/
```

It should support:

- first-run full redundant analysis
- later incremental tracking
- explicit partial refresh
- durable output files
- `_state.json`
- `_index.md`
- per-run `_manifest.json`

## Required Files

Create:

- `tos-funder/commands/tos-funder-stock-research.md`
- `tos-funder/references/stock-research-workspace.md`
- `docs/tos-funder/validation-pr12.md`

Update:

- `tos-funder/SKILL.md`
- `tos-funder/commands/tos-funder-analyze.md` if routing support is useful
- `tos-funder/references/skill-workflow.md`
- `tos-funder/references/output-schema-examples.md` if a new schema anchor is needed
- `docs/tos-funder/quick-guide.md`

Do not modify existing analyst commands unless there is a direct routing/schema contradiction.

## Command Requirements

### Frontmatter

`tos-funder/commands/tos-funder-stock-research.md` must have:

```yaml
---
name: tos-funder-stock-research
description: Orchestrate persistent A-share stock research workspaces. Runs full, incremental, or refresh analysis using existing tos-funder commands and writes per-stock outputs under outputs/stocks/<股票名>-<代码>/.
command: true
argument-hint: "<股票代码或名称> [mode=auto|full|incremental|refresh] [detail=redundant|normal|compact] [layers=...] [date=YYYY-MM-DD]"
type: command
---
```

### Modes

Implement these mode semantics in the command document:

```text
mode=auto
  if no workspace exists -> full
  if workspace exists -> incremental

mode=full
  run all layers and write all reports

mode=incremental
  read existing _state.json
  refresh high-change layers only by default

mode=refresh
  refresh requested layers only
```

### Detail Levels

```text
detail=redundant
  write every layer report with facts, scoring, assumptions, risks, opportunities, and expert/persona framing

detail=normal
  write updated layer reports and summary

detail=compact
  write delta summary and changed signals only
```

Default:

```text
mode=auto
detail=redundant if first full run, else normal
```

## Output Protocol

Base path:

```text
outputs/stocks/
```

Stock path:

```text
outputs/stocks/<股票名>-<代码>/
```

Required files:

```text
_index.md
_state.json
```

Run directory names:

```text
YYYY-MM-DD-full/
YYYY-MM-DD-incremental/
YYYY-MM-DD-refresh-<layers>/
```

Each run directory must include:

```text
_manifest.json
```

Full redundant run should write:

```text
00-summary.md
01-value-buffett.md
02-value-graham.md
03-growth.md
04-quant-fundamentals.md
05-price-series.md
06-quant-technicals.md
07-sentiment.md
08-risk-manager.md
09-tactical.md
10-macro-topdown.md
11-portfolio-decision.md
raw/
```

Incremental run should write:

```text
00-delta-summary.md
05-price-series-delta.md
06-quant-technicals-delta.md
07-sentiment-delta.md
08-risk-manager-delta.md
09-tactical-delta.md
10-macro-topdown-delta.md
11-portfolio-decision-delta.md
```

Do not overwrite older run directories.

If the same date/mode directory already exists, append a suffix:

```text
2026-06-03-full-2/
2026-06-03-incremental-2/
```

## State And Manifest

Document and use the schemas from:

```text
docs/tos-funder/12-stock-research-workspace.md
```

Minimum:

- `_state.json`
- `_manifest.json`
- `_index.md`

The command should describe how to update them after every run.

## Orchestration Rules

### Full Run

Planned command order:

1. Resolve target name/code.
2. `/tos-funder-quant-price-series`
3. `/tos-funder-value-buffett`
4. `/tos-funder-value-graham`
5. `/tos-funder-growth`
6. `/tos-funder-quant-fundamentals`
7. `/tos-funder-quant-technicals`
8. `/tos-funder-quant-sentiment`
9. `/tos-funder-risk-manager`
10. `/tos-funder-tactical`
11. `/tos-funder-macro-topdown`
12. `/tos-funder-portfolio`
13. Write final summary, index, state, manifest.

### Incremental Run

Planned command order:

1. Read `_state.json`.
2. Identify latest full run and latest run.
3. Refresh:
   - price-series
   - technicals
   - sentiment
   - risk-manager
   - tactical
   - macro-topdown
   - portfolio
4. Refresh fundamentals/value/growth only when triggered.
5. Write delta reports.
6. Update `_state.json`, `_index.md`, `_manifest.json`.

### Refresh Run

Only run requested layers.

If `layers` is missing, use:

```text
technicals,risk,sentiment,tactical,portfolio
```

## Important Boundaries

Do not create new analyst models.

Do not duplicate portfolio final decision logic inside stock-research. `/tos-funder-stock-research` should call or consume `/tos-funder-portfolio` output for final portfolio decision.

Do not make upstream analyst commands output final portfolio actions.

Do not change accepted signal/action enums:

```text
signal: bullish | neutral | bearish | blocked
strength: strong | medium | weak | flat
portfolio action: buy | hold | sell | reduce | watch | reject | blocked
```

Preserve PR11 data boundaries:

- iWencai: fundamentals, valuation, announcements, reports
- mootdx/TDX: OHLCV, technicals, risk
- iWencai OHLCV: fallback only
- `business`: blocked
- `event query2data`: blocked
- `management` insider fields: blocked
- validated management fields allowed: 分红, 股本, 股东人数, 回购 / 总股本 / 流通A股 when already documented

## Validation Requirements

Create `docs/tos-funder/validation-pr12.md`.

It must include at least these scenarios:

### Scenario 1: First Full Redundant Run — 宁波银行

Input:

```text
/tos-funder-stock-research 宁波银行 mode=auto detail=redundant
```

Assume no existing workspace.

Expected:

- chooses `mode=full`
- resolves `宁波银行-002142`
- creates stock directory
- writes full report set
- writes `_state.json`
- writes `_index.md`
- writes `_manifest.json`
- final decision comes from `/tos-funder-portfolio`, not stock-research itself

### Scenario 2: Second Run — 宁波银行 Incremental

Input:

```text
/tos-funder-stock-research 宁波银行
```

Assume `_state.json` exists.

Expected:

- chooses `mode=incremental`
- reuses latest full run
- refreshes high-change layers
- does not rerun Buffett/Graham/growth/fundamentals unless trigger exists
- writes delta reports
- updates `_state.json` and `_index.md`

### Scenario 3: Explicit Full Refresh

Input:

```text
/tos-funder-stock-research 宁波银行 mode=full detail=redundant
```

Assume workspace exists.

Expected:

- creates a new full run directory
- does not overwrite prior full run
- writes complete report set

### Scenario 4: Partial Refresh

Input:

```text
/tos-funder-stock-research 宁波银行 mode=refresh layers=technicals,risk
```

Expected:

- writes refresh directory
- only writes technical/risk delta plus summary/manifest
- updates state selectively

## Required Checks

Run and record results in `validation-pr12.md`:

```bash
rg -n "tos-funder-stock-research" tos-funder docs/tos-funder
rg -n "outputs/stocks|_state.json|_manifest.json|_index.md" tos-funder docs/tos-funder
rg -n "final_action|final_actions|\"action\"\\s*:" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review\"" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md
rg -n "query2data|query -r event|query -r business|hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md
```

Expected:

- command is routed
- workspace output paths are documented
- stock-research does not introduce new final portfolio action logic
- no enum drift
- no dead route usage
- no iWencai technical indicator dependency

## Acceptance Criteria

PR12 is acceptable only if:

1. `/tos-funder-stock-research` exists with valid frontmatter.
2. `SKILL.md` routes the command clearly.
3. `stock-research-workspace.md` documents mode/detail/output/state/manifest protocols.
4. `validation-pr12.md` covers first full run, second incremental run, explicit full refresh, and partial refresh.
5. Full redundant mode writes separate layer reports.
6. Incremental mode uses existing `_state.json` and does not default to full recomputation.
7. Existing analyst commands are not rewritten unnecessarily.
8. `/tos-funder-portfolio` remains the final portfolio decision source.
9. Output directories are deterministic and non-overwriting.
10. PR11 data boundaries remain intact.

## CC Delivery Summary Required

When finished, reply with:

```text
PR12 完成。

新增文件：
- tos-funder/commands/tos-funder-stock-research.md
- tos-funder/references/stock-research-workspace.md
- docs/tos-funder/validation-pr12.md

修改文件：
- ...

核心设计：
- mode=auto/full/incremental/refresh
- detail=redundant/normal/compact
- outputs/stocks/<股票名>-<代码>/ workspace
- _state.json / _index.md / _manifest.json

验证结果：
- first full redundant run: ...
- second incremental run: ...
- explicit full refresh: ...
- partial refresh: ...

已确认：
- no final action duplication
- no enum drift
- no dead route usage
- no iWencai technical dependency
- existing run directories are not overwritten

需要架构师复核的点：
- ...
```
