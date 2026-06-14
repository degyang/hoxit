# Ningbo Bank Full-Run Lessons

Date: 2026-06-10

Target: 宁波银行 `002142`

Output workspace: `/Users/mac/Projects/POS/90-Inbox/tos-funder/宁波银行-002142/_index/`

## Problems Found

1. **Legacy 11-layer full run was incomplete**

   The first execution used the historical `/tos-funder-stock-research` full order:

   `price-series, value-buffett, value-graham, growth, quant-fundamentals, quant-technicals, quant-sentiment, risk-manager, tactical, macro-topdown, portfolio`

   This missed the newly migrated dimensions: Munger, Burry, Pabrai, Cathie Wood, quant valuation, Damodaran, Ackman, Taleb, Druckenmiller, Jhunjhunwala, and news sentiment.

   Resolution: POS `tos-funder-stock-research.md` now distinguishes `CORE_SPINE` from `EXPANDED_MIGRATED_LAYERS`; `mode=full` must run both.

2. **Portfolio was synthesized too early**

   The initial portfolio report was written after the core spine. After adding the expanded layers, the portfolio decision, summary, manifest, state, and stock index had to be regenerated.

   Resolution: full-run protocol now requires final portfolio synthesis after all expanded layers complete.

3. **Workspace entry file requirement differs from the reference protocol**

   The reference protocol used `_index.md`, but the user requested `_index/宁波银行.md` as the durable entry file.

   Resolution: this run uses `90-Inbox/tos-funder/宁波银行-002142/_index/宁波银行.md` as the entry file. Future runs for this stock should update that file rather than creating `_index.md`.

4. **Some hoxit routes returned partial or empty facts**

   Observed during the Ningbo Bank run:

   - `hoxit signals fund-flow 002142 --days 20` returned an empty list.
   - `hoxit valuation full 002142` did not provide forward EPS, PEG, or analyst coverage inputs.
   - iWencai report/announcement search is usable as a proxy, but not complete external news sentiment.
   - Bank stocks require sector-specific interpretation; generic ROIC/current-ratio/gross-margin scoring is not sufficient.

   Resolution: reports include `data_quality_warnings`; valuation and news/persona layers are marked as proxy or degraded where facts are missing.

5. **Ad hoc generation code hit a Python statistics edge case**

   The first report generation script used `statistics.stdev()` on values that triggered a runtime error in this environment:

   `AttributeError: 'float' object has no attribute 'numerator'`

   Resolution: use a simple explicit sample-standard-deviation implementation when generating run artifacts from raw floats.

## Updated Skill Rules

- `mode=full` must include expanded migrated layers, not only the core spine.
- If only the core spine runs, label the result `partial_full` or `core_spine_only`.
- Final portfolio synthesis must be regenerated after expanded layers finish.
- The index must show expanded dimension count.
- Missing or proxy data must reduce confidence or cap action; do not force buy/sell.

## Hoxit Follow-Ups

These are incremental hoxit improvements, not POS skill logic:

- Add an executable reusable runner/helper for stock-research artifact generation so full runs do not rely on ad hoc scripts.
- Add tests that assert a complete full run includes all commands from `docs/tos-funder/18-hoxit-execution-binding.md` plus POS `tos-funder-stock-research.md`.
- Improve `valuation full` for bank stocks with bank-specific valuation inputs, e.g. ROE/COE/PB model, forward EPS, dividend yield, and capital adequacy facts.
- Investigate empty `signals fund-flow` responses and document whether this is source-side empty data, parsing loss, or endpoint drift.
- Add a news-sentiment route or explicitly preserve iWencai announcement/report as the only supported proxy.

## Validation From This Run

- Final expanded dimension count: 22.
- Final action: `hold`.
- Final confidence: 73.
- JSON files validated: `_state.json` and `_manifest.json`.
