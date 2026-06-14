# Claude Code Implementation Guide

Use this guide when extending Trading Funder.

Before starting any PR:
1. Read `docs/tos-funder/07-cc-working-constitution.md`. Treat it as the mandatory self-review checklist before reporting completion.
2. Read the latest validation document for the PR family: `docs/tos-funder/validation-*.md` — this contains the most recently accepted schema for the subsystem you are modifying.
3. Read the command file and reference files you will be modifying to ensure you are working from the latest accepted schema, not a stale copy.

## Downstream Consumption Consistency Check

Before finalizing any PR that modifies command output schemas:

1. **Identify downstream consumers**: Which commands read this output?
   - `/tos-funder-analyze` consumes price-series, risk, fundamentals, technical, value signals
   - `/tos-funder-portfolio` consumes fundamentals, technicals, value, risk signals
   - `/tos-funder-risk-manager` consumes price-series

2. **Verify field name compatibility**: Every field name in the new output must match what downstream commands expect. Check the consuming command's Prerequisites, Data Collection, and Step references.

3. **Check enum consistency**: Signal values (`bullish/neutral/bearish/blocked`), action values (`buy/hold/sell/reduce/watch/reject/blocked`), and status values (`valid/degraded/blocked`) must be shared across producer and consumer.

4. **Machine readability**: Downstream commands must be able to parse the output as structured data (JSON fields), not extract values from prose. If a value is only mentioned in a `reason` string, it is not consumable.

5. **Backward compatibility flag**: If renaming or removing a field that a downstream command currently references, add a deprecation note and update the consumer in the same PR.

## Add a New Analyst Command

1. Open `tos-funder/references/command-template.md`.
2. Choose family prefix:
   - `tos-funder-value-*`
   - `tos-funder-growth-*`
   - `tos-funder-tactical-*`
   - `tos-funder-quant-*`
   - `tos-funder-portfolio*`
3. Read the corresponding POS agent document and source file from `Reference/ai-hedge-fund/src/agents`.
4. Extract:
   - data dependencies
   - deterministic scoring
   - persona prompt
   - signal schema
   - fallback behavior
5. Map each data dependency through the correct reference:
   - fundamentals, valuation snapshots, announcements, reports: `tos-funder/references/iwencai-adapter.md`
   - OHLCV, quote, intraday, technical, risk: `tos-funder/references/price-series.md`
6. Create the command in `tos-funder/commands`.
7. Add or update a reference file only if the logic is reusable.

## Data Collection Rules

- Prefer several narrow iWencai queries over one broad query.
- Use `query` routes for structured data.
- Use `search` routes for announcements and reports.
- If iWencai returns empty, retry with fewer fields before declaring a gap.
- Use `.venv/bin/hoxit market bars <CODE> --category 4 --offset 250 --adjust qfq` for daily OHLCV.
- Compute technical indicators locally from OHLCV; do not depend on iWencai precomputed RSI/MACD as the primary source.

## Reporting Rules

Every analysis should include:

```text
signal
confidence
action
facts
score or model output
risks
opportunities
next-step prompts
```

## A-share Action Rules

Default action set:

```text
buy | hold | sell | reduce | watch | reject | blocked
```

Do not use the original `short`/`cover` portfolio actions unless the command explicitly verifies margin or short eligibility.

## Example Path

The current key sample is:

```text
tos-funder/commands/tos-funder-value-buffett.md
```

Use it as the implementation reference for other persona-based analyst commands.
