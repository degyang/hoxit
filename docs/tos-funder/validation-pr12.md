# PR12 Validation: Stock Research Workspace

Created: 2026-06-03

## Files Created

| File | Purpose |
|---|---|
| `tos-funder/commands/tos-funder-stock-research.md` | Workspace orchestrator command |
| `tos-funder/references/stock-research-workspace.md` | Workspace protocol reference |
| `docs/tos-funder/validation-pr12.md` | This file |

## Files Modified

| File | Change |
|---|---|
| `tos-funder/SKILL.md` | Added `/tos-funder-stock-research` to command routing |
| `tos-funder/references/skill-workflow.md` | Added `#stock_research_workspace` schema anchor |
| `tos-funder/references/output-schema-examples.md` | Added section 12 `stock_research_workspace` |
| `tos-funder/commands/tos-funder-analyze.md` | Added `workspace` family routing |
| `docs/tos-funder/quick-guide.md` | Added PR12 to accepted list, current delivery, roadmap |

## Validation Scenarios

### Scenario 1: First Full Redundant Run — 宁波银行

**Input**:
```text
/tos-funder-stock-research 宁波银行 mode=auto detail=redundant
```

**Expected behavior** (no existing workspace):
1. ✅ Resolves `宁波银行` → code `002142`
2. ✅ Chooses `mode=full` (no `_state.json` exists)
3. ✅ Chooses `detail=redundant` (first full run)
4. ✅ Creates `outputs/stocks/宁波银行-002142/`
5. ✅ Creates `outputs/stocks/宁波银行-002142/2026-06-03-full/`
6. ✅ Runs all 11 commands in order (price-series → value-buffett → value-graham → growth → quant-fundamentals → quant-technicals → quant-sentiment → risk-manager → tactical → macro-topdown → portfolio)
7. ✅ Writes 12 report files (00-summary.md + 01-11 layer reports)
8. ✅ Writes raw JSON to `raw/` directory
9. ✅ Writes `_manifest.json` in run directory
10. ✅ Writes `_state.json` at stock root
11. ✅ Writes `_index.md` at stock root
12. ✅ Portfolio final decision comes from `/tos-funder-portfolio`, not stock-research itself
13. ✅ All 12 reports include signal, confidence, key facts
14. ✅ `detail=redundant` reports include full scoring, assumptions, source status, risks/opportunities, expert framing

### Scenario 2: Second Run — 宁波银行 Incremental

**Input**:
```text
/tos-funder-stock-research 宁波银行
```

**Expected behavior** (workspace exists from Scenario 1):
1. ✅ Reads `outputs/stocks/宁波银行-002142/_state.json`
2. ✅ Chooses `mode=incremental` (state file exists)
3. ✅ Chooses `detail=normal` (default for incremental)
4. ✅ Identifies latest full run: `2026-06-03-full`
5. ✅ Creates new run dir: `2026-06-03-incremental/`
6. ✅ Runs high-change layers only: price-series, quant-technicals, quant-sentiment, risk-manager, tactical, macro-topdown, portfolio
7. ✅ Does NOT run low-change layers (value-buffett, value-graham, growth, quant-fundamentals) unless triggers exist
8. ✅ Writes `00-delta-summary.md` with what changed
9. ✅ Writes `<layer>-delta.md` for each refreshed layer (with comparison to previous run)
10. ✅ Updates `_state.json` with new signals and updated `latest_runs.incremental`
11. ✅ Appends run to `_index.md` table
12. ✅ Does not modify `2026-06-03-full/` directory

### Scenario 3: Explicit Full Refresh

**Input**:
```text
/tos-funder-stock-research 宁波银行 mode=full detail=redundant
```

**Expected behavior** (workspace exists):
1. ✅ Creates new full run directory: `2026-06-03-full-2/` (appends suffix since `2026-06-03-full/` exists)
2. ✅ Runs all 11 commands
3. ✅ Writes complete report set
4. ✅ Does NOT overwrite `2026-06-03-full/`
5. ✅ Updates `_state.json` with `latest_runs.full = "2026-06-03-full-2"`

### Scenario 4: Partial Refresh

**Input**:
```text
/tos-funder-stock-research 宁波银行 mode=refresh layers=technicals,risk
```

**Expected behavior**:
1. ✅ Creates refresh run directory: `2026-06-03-refresh-technicals-risk/`
2. ✅ Resolves dependency: runs price-series first (prerequisite for technicals)
3. ✅ Runs quant-technicals and risk-manager
4. ✅ Does NOT run value/growth/quant-fundamentals/sentiment/tactical/macro/portfolio
5. ✅ Writes `00-delta-summary.md`
6. ✅ Writes `06-quant-technicals-delta.md` and `08-risk-manager-delta.md`
7. ✅ Selectively updates `_state.json` (technicals, risk signals only)
8. ✅ Appends to `_index.md`

## Required Checks — Actual Results

### 1. Command routing

```bash
rg -n "tos-funder-stock-research" tos-funder docs/tos-funder -g "*.md"
```

| Location | Match | Classification |
|---|---|---|
| `tos-funder/SKILL.md` | Command routing entry | ✅ Active route |
| `tos-funder/commands/tos-funder-stock-research.md` | Command file | ✅ Active command |
| `tos-funder/commands/tos-funder-analyze.md` | Workspace family routing | ✅ Active route |
| `tos-funder/references/skill-workflow.md` | Schema anchor mapping | ✅ Active reference |
| `tos-funder/references/output-schema-examples.md` | Section 12 `stock_research_workspace` | ✅ Active schema |
| `tos-funder/references/stock-research-workspace.md` | Reference document | ✅ Active reference |
| `docs/tos-funder/validation-pr12.md` | This file | ✅ Validation |
| `docs/tos-funder/quick-guide.md` | Progress update | ✅ Quick-guide |

**Verdict**: ✅ Full routing coverage.

### 2. Workspace output paths

```bash
rg -n "outputs/stocks|_state.json|_manifest.json|_index.md" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md
```

All three files contain complete documentation:
- Base path: `outputs/stocks/<股票名>-<代码>/`
- State: `_state.json` with `latest_portfolio_decision` sourced from `/tos-funder-portfolio`
- Manifest: `_manifest.json` with `summary.portfolio_decision`
- Index: `_index.md` with run history table

**Verdict**: ✅ Workspace output paths documented in all required files.

### 3. Final action boundary

```bash
rg -n "final_action|final_actions|\"action\"\s*:" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md
```

| Match | Classification | Reason |
|---|---|---|
| `stock-research-workspace.md:384` — constraint text | ✅ Allowed | "portfolio is the only command producing final_actions" |
| `commands/tos-funder-stock-research.md:13` — constraint text | ✅ Allowed | "Does not produce final portfolio actions" |
| `commands/tos-funder-stock-research.md:378` — constraint text | ✅ Allowed | "This command does NOT produce final_action" |
| `stock-research-workspace.md:80-85` — `latest_portfolio_decision` | ✅ Allowed | Portfolio output snapshot with `source_command: "/tos-funder-portfolio"` |
| `commands/tos-funder-stock-research.md:324-329` — `summary.portfolio_decision` | ✅ Allowed | Manifest records portfolio output with `source_command` + `source_report` |
| `stock-research-workspace.md:159-165` — `summary.portfolio_decision` | ✅ Allowed | Manifest schema example, same pattern |

**Verdict**: ✅ No `final_action`/`final_actions` at stock-research orchestrator level. All portfolio decision fields are clearly sourced from `/tos-funder-portfolio`.

### 4. Enum drift

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md
```

| Match | Classification |
|---|---|
| `stock-research-workspace.md:103` — `manual_review_required: false` (data_quality boolean field) | ✅ Allowed — not an action enum |
| `validation-pr12.md:140` — the rg command itself | ✅ Allowed — check text |

**Verdict**: ✅ No enum drift.

### 5. Dead route usage

```bash
rg -n "query2data|query -r event|query -r business|hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR" tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md
```

| Match | Classification |
|---|---|
| `stock-research-workspace.md:378-379` — "Blocked — Do not query" | ✅ Allowed — constraint text marking routes as blocked |
| `commands/tos-funder-stock-research.md:381` — "Do NOT use ..." | ✅ Allowed — constraint text |

**Verdict**: ✅ No dead routes used as executable paths.

## Acceptance Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | `/tos-funder-stock-research` exists with valid frontmatter | ✅ |
| 2 | `SKILL.md` routes the command clearly | ✅ |
| 3 | `stock-research-workspace.md` documents mode/detail/output/state/manifest | ✅ |
| 4 | `validation-pr12.md` covers 4 required scenarios | ✅ |
| 5 | Full redundant mode writes separate layer reports | ✅ (per command specification) |
| 6 | Incremental mode uses `_state.json` and avoids full recomputation | ✅ (per command specification) |
| 7 | Existing analyst commands not rewritten | ✅ |
| 8 | `/tos-funder-portfolio` remains final portfolio decision source | ✅ |
| 9 | Output directories are deterministic and non-overwriting | ✅ |
| 10 | PR11 data boundaries remain intact | ✅ |
