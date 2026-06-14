# PR13 Instruction — Explicit Preflight Screening

Created: 2026-06-05

## User Requirement

Add a low-cost rough evaluation mechanism for Trading Funder because the current skill can involve complex multi-agent execution with high cost.

Required behavior:

- The screening mechanism must be command-triggered.
- If the user does not call the screening command, the existing skill/full research behavior remains unchanged.
- If a stock looks low-value after several simple dimensions, avoid deep execution.
- If the stock scores medium or above, allow full deep execution.
- Any layers already run during screening should be reusable by later deep analysis.
- Preserve PR documentation.

## Architecture Decision

Implement PR13 as a new explicit command:

```text
/tos-funder-preflight <股票代码或名称>
```

Do not make `/tos-funder-stock-research` auto-run preflight.

Optional explicit reuse:

```text
/tos-funder-stock-research <股票代码或名称> reuse_preflight=true
```

## Files

Create:

- `tos-funder/commands/tos-funder-preflight.md`
- `tos-funder/references/preflight-screening.md`
- `docs/tos-funder/validation-pr13.md`

Modify:

- `tos-funder/SKILL.md`
- `tos-funder/references/skill-workflow.md`
- `tos-funder/references/output-schema-examples.md`
- `tos-funder/references/stock-research-workspace.md`
- `tos-funder/commands/tos-funder-stock-research.md`
- `docs/tos-funder/quick-guide.md`

## Acceptance Criteria

1. Preflight is explicit-only.
2. Stock research default behavior is unchanged.
3. Preflight uses only low-cost reusable layers:
   - price-series
   - quant-fundamentals
   - quant-sentiment
4. Preflight outputs:
   - `preflight_score`
   - `screening_decision`
   - `confidence`
   - `dimension_scores`
   - `hard_gates`
   - `reason_codes`
   - `reusable_outputs`
5. Decisions are `skip`, `watch`, `deep_dive`, `blocked`.
6. Preflight does not produce final portfolio actions.
7. Workspace stores `YYYY-MM-DD-preflight/` runs.
8. Deep analysis can reuse preflight raw outputs only with explicit reuse.

