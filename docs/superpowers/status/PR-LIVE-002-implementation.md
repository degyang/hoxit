# PR-LIVE-002 Implementation Report

## Summary

Implemented UZEN derived market metrics — deterministic computation from quote and bars data with no network calls.

## What Changed

### `hoxit/uzen.py`

1. **9 derivation helpers** (after `_quote_change_pct`, before normalization helpers):
   - `_quote_change_amount(quote)` — derive from price/last_close when direct field absent
   - `_quote_amplitude_pct(quote)` — derive from high/low/last_close when direct field absent
   - `_quote_avg_price(quote)` — compute 成交均价 from amount/vol (成交额/成交量); returns None when turnover data unavailable
   - `_bars_closes(bars)` — extract close list from bars
   - `_bars_ma(closes, n)` — simple moving average
   - `_bars_return(closes, n)` — N-day return %
   - `_bars_volatility(closes, n)` — annualised volatility (σ × √242)
   - `_bars_drawdown(closes, n)` — max drawdown over N bars
   - `_derive_market_metrics(quote, bars)` — orchestrates all derivations

2. **`_derive_market_metrics(quote, bars)`** orchestrator:
   - Computes all derived fields from quote and bars
   - Tracks `_meta.quote_inputs` (which quote fields were used)
   - Tracks `_meta.bars_count` (number of valid closes)
   - Generates `_meta.warnings` for insufficient data, including missing 成交均价

3. **`analyze_snapshot()`** updated:
   - Uses `_derive_market_metrics(quote, bars)` for all market metric fields
   - Summary includes: change_pct, change_amount, amplitude_pct, avg_price, return_5d, return_20d, ma5, ma20, volatility_20d, drawdown_60d, _meta

4. **`render_markdown()`** updated:
   - Core conclusion includes: change_amount, amplitude_pct, MA5/MA20, return_5d, volatility_20d
   - avg_price rendered when available (from turnover data)

### `tests/test_uzen.py`

9 new tests added (188 total):
- `test_derived_change_pct_from_price_last_close` — derivation from price/last_close
- `test_derived_change_pct_preserves_direct_field` — direct field takes precedence
- `test_derived_amplitude_pct` — amplitude from high/low/last_close
- `test_derived_ma_and_returns` — MA5/MA20 and 5d/20d returns with 25 bars
- `test_derived_volatility_and_drawdown` — annualised vol and max drawdown with 65 bars
- `test_derived_insufficient_bars_warnings` — warnings when bars < threshold
- `test_derived_no_bars_all_none` — all bar-derived fields None with empty bars
- `test_derived_avg_price_from_turnover` — avg_price = amount/vol when both present
- `test_derived_avg_price_none_when_no_turnover` — avg_price=None with warning when turnover data missing
- `test_derived_metrics_in_markdown` — derived fields appear in Markdown output

### `docs/API_DEVLOG.md`

Added entry documenting the derivation layer with derivation order and fallback behavior.

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py -v         → 188 passed
.venv/bin/python -m pytest                                → 301 passed, 29 skipped
.venv/bin/hoxit uzen --help                               → Normal output
```

## Base Branch

Built on top of `agent/cc/pr-live-001-uzen-provider-normalization-boundary` (commit `7bb9597`, APPROVED).

## Status

Ready for Codex review.
