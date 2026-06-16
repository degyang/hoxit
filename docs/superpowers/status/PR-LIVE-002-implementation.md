# PR-LIVE-002 Implementation Report

## Status

REVIEW_READY

## Summary

Added deterministic market metric derivation helpers so UZEN reports populate MA, returns, volatility, and drawdown fields from quote and bars data when providers do not directly return them.

## Corrected Base

Previous implementation was based on `main` (commit `887bbdd`). Rebuilt on top of `agent/cc/pr-live-001-uzen-provider-normalization-boundary` (commit `7bb9597`) as required by the ticket dependency.

- Base branch: `agent/cc/pr-live-001-uzen-provider-normalization-boundary`
- Includes PR-LIVE-001 normalization implementation and review approval
- PR-LIVE-001 board status preserved as APPROVED

## Changes Made

### hoxit/uzen.py

Added 9 derivation helpers after `_quote_change_pct()`:

- **`_quote_change_amount(quote)`**: Derives `price - last_close`; preserves direct `change_amount`.
- **`_quote_amplitude_pct(quote)`**: Derives `(high - low) / last_close * 100`; preserves direct `amplitude_pct`.
- **`_bars_closes(bars)`**: Extracts valid close prices from bars list.
- **`_bars_ma(closes, n)`**: Simple moving average of last n closes.
- **`_bars_return(closes, n)`**: Percentage return over last n bars.
- **`_bars_volatility(closes, n)`**: Annualised volatility from last n daily returns (σ × √242).
- **`_bars_drawdown(closes, n)`**: Max drawdown over last n bars.
- **`_bars_avg_price(closes)`**: Average close price over available bars.
- **`_derive_market_metrics(quote, bars)`**: Orchestrates all derivations, returns dict with `_meta` tracking.

Updated `analyze_snapshot()`:
```python
derived = _derive_market_metrics(quote, bars)
snapshot["analysis"]["summary"] = {
    "name": ..., "price": ...,
    "change_pct": derived["change_pct"],
    "change_amount": derived["change_amount"],
    "amplitude_pct": derived["amplitude_pct"],
    "avg_price": derived["avg_price"],
    "return_5d": derived["return_5d"],
    "return_20d": derived["return_20d"],
    "ma5": derived["ma5"],
    "ma20": derived["ma20"],
    "volatility_20d": derived["volatility_20d"],
    "drawdown_60d": derived["drawdown_60d"],
    "_meta": derived["_meta"],
}
```

Updated `render_markdown()` core conclusion:
```
- 涨跌幅：+10.00%（变动 1.00元）
- 振幅：15.00%
- MA5：32.00元，MA20：24.50元
- 5日收益：+17.24%，20日波动率：25.30%
```

### tests/test_uzen.py

Added 9 new tests (187 total, 178 from PR-LIVE-001 + 9 from PR-LIVE-002):

1. `test_derived_change_pct_from_price_last_close` — derives change_pct and change_amount
2. `test_derived_change_pct_preserves_direct_field` — direct provider field preserved
3. `test_derived_amplitude_pct` — from high/low/last_close
4. `test_derived_ma_and_returns` — MA5, MA20, return_5d, return_20d from 25 bars
5. `test_derived_volatility_and_drawdown` — volatility_20d and drawdown_60d from 65 bars
6. `test_derived_insufficient_bars_warnings` — explicit warnings for insufficient bars
7. `test_derived_no_bars_all_none` — no bars → all None
8. `test_derived_avg_price` — average close price
9. `test_derived_metrics_in_markdown` — derived fields appear in Markdown

### docs/API_DEVLOG.md

Added 2026-06-16 entry documenting derived market metrics.

## Verification

- `.venv/bin/python -m pytest tests/test_uzen.py -v` → 187 passed
- `.venv/bin/hoxit uzen --help` → Normal output
- `git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md` → No whitespace issues
- `git merge-base --is-ancestor origin/agent/cc/pr-live-001-uzen-provider-normalization-boundary HEAD` → true

## Design Decisions

- **Direct field preservation**: `_quote_change_pct()` and friends check for direct provider fields first, only deriving when missing.
- **Explicit warnings**: `_meta.warnings` records exactly which inputs were insufficient and how many bars were available.
- **No silent blanks**: Missing bars produce `None` values with explicit warnings, not empty strings or zero.
- **Annualised volatility**: Uses simple daily return σ × √242 (242 A-share trading days). Not EWMA or log returns.
- **60-bar drawdown**: Fixed 60-bar window for drawdown; configurable if needed later.
