# PR13 Validation: Explicit Preflight Screening Command

Created: 2026-06-05

## Scope

PR13 adds an explicit low-cost preflight screening command for Trading Funder.

Primary goal:

- let the user screen a stock before running expensive full multi-agent research
- preserve PR12 default `/tos-funder-stock-research` behavior
- reuse preflight outputs in a later full run only when explicitly requested

## Files Created

| File | Purpose |
|---|---|
| `tos-funder/commands/tos-funder-preflight.md` | Explicit low-cost screening command |
| `tos-funder/references/preflight-screening.md` | Scoring, hard gates, routing, reuse protocol |
| `docs/tos-funder/validation-pr13.md` | This validation record |
| `docs/tos-funder/audit/pr13-preflight-screening-instruction-20260605-000000.md` | PR instruction/audit record |

## Files Modified

| File | Change |
|---|---|
| `tos-funder/SKILL.md` | Added `/tos-funder-preflight` route and reference |
| `tos-funder/references/skill-workflow.md` | Added `#preflight_screening_output` schema anchor |
| `tos-funder/references/output-schema-examples.md` | Added canonical preflight output schema |
| `tos-funder/references/stock-research-workspace.md` | Added optional preflight run layout and reuse boundary |
| `tos-funder/commands/tos-funder-stock-research.md` | Added explicit `reuse_preflight=true` parameter without changing default execution |
| `docs/tos-funder/quick-guide.md` | Updated current progress and roadmap |

## Acceptance Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | `/tos-funder-preflight` exists with valid frontmatter | ✅ |
| 2 | Preflight is explicit-only and does not change default `/tos-funder-stock-research` behavior | ✅ |
| 3 | Preflight runs only low-cost reusable layers: price-series, quant-fundamentals, quant-sentiment | ✅ |
| 4 | Preflight does not produce portfolio `final_actions` | ✅ |
| 5 | Output includes `preflight_score`, `screening_decision`, dimension scores, hard gates, reason codes, reusable outputs | ✅ |
| 6 | Decisions are limited to `skip`, `watch`, `deep_dive`, `blocked` | ✅ |
| 7 | Workspace stores preflight under `YYYY-MM-DD-preflight/` | ✅ |
| 8 | Reuse requires explicit `reuse_preflight=true` or preflight `continue=true` | ✅ |
| 9 | Data-quality artifacts are not treated as real negative market signals | ✅ |
| 10 | PR12 full/incremental/refresh semantics remain intact by default | ✅ |

## Validation Scenarios

### Scenario 1: Low Score Skip

Input:

```text
/tos-funder-preflight <弱基本面股票> threshold=65
```

Expected behavior:

1. Runs `/tos-funder-quant-price-series`
2. Runs `/tos-funder-quant-fundamentals`
3. Runs `/tos-funder-quant-sentiment`
4. Computes weighted score below 45
5. Returns `screening_decision: "skip"`
6. Writes `YYYY-MM-DD-preflight/00-preflight-summary.md`
7. Does not run Buffett/Graham/Growth/Technicals/Risk/Tactical/Macro/Portfolio

### Scenario 2: Middle Score Watch

Input:

```text
/tos-funder-preflight <中等股票> threshold=65
```

Expected behavior:

1. Computes score between 45 and 64
2. Returns `screening_decision: "watch"`
3. Writes reason codes explaining which dimensions were insufficient
4. Does not trigger full research automatically

### Scenario 3: Deep Dive Candidate

Input:

```text
/tos-funder-preflight <优质股票> threshold=65
```

Expected behavior:

1. Computes score >=65
2. Returns `screening_decision: "deep_dive"`
3. Lists reusable outputs:
   - `price-series.json`
   - `quant-fundamentals.json`
   - `sentiment.json`
4. Suggests next command:

```text
/tos-funder-stock-research <优质股票> reuse_preflight=true
```

### Scenario 4: Explicit Continue

Input:

```text
/tos-funder-preflight <优质股票> continue=true
```

Expected behavior:

1. Runs preflight first
2. If result is `deep_dive`, emits a continuation plan using `/tos-funder-stock-research <target> reuse_preflight=true`
3. Full research may reuse same-date raw outputs
4. If result is `skip`, `watch`, or `blocked`, does not continue

### Scenario 5: Stock Research Default Unchanged

Input:

```text
/tos-funder-stock-research 宁波银行
```

Expected behavior:

1. Does not run `/tos-funder-preflight`
2. Does not stop based on preflight score
3. Uses PR12 mode auto-detection:
   - no `_state.json` -> full redundant
   - existing `_state.json` -> incremental normal
4. Runs normal PR12 layer plan

### Scenario 6: Explicit Reuse

Input:

```text
/tos-funder-stock-research 宁波银行 reuse_preflight=true
```

Expected behavior:

1. Looks for same-date `YYYY-MM-DD-preflight/raw/`
2. Reuses price-series, quant-fundamentals, and sentiment only if valid
3. Records `commands_reused` in `_manifest.json`
4. Runs all remaining required full/incremental layers according to stock-research mode
5. Does not treat preflight decision as a portfolio decision

## Required Checks

```bash
rg -n "tos-funder-preflight|preflight-screening|preflight_screening_output|latest_preflight|reuse_preflight" tos-funder docs/tos-funder -g "*.md"
```

Expected: command, route, schema, workspace, validation, and quick-guide references are present.

```bash
rg -n "final_action|final_actions|portfolio_decision" tos-funder/commands/tos-funder-preflight.md tos-funder/references/preflight-screening.md
```

Expected: only boundary text appears; preflight does not define final portfolio actions.

```bash
rg -n "query2data|query -r event|query -r business|hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR" tos-funder/commands/tos-funder-preflight.md tos-funder/references/preflight-screening.md
```

Expected: no executable dead-route usage.

## PR13 Verdict

✅ PR13 accepted as an explicit cost-control screening layer.

The default full research path remains unchanged. Preflight is available only when explicitly invoked, and its outputs are reusable by later deep research only through an explicit reuse flag.

