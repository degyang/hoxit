# PR-LIVE-002: UZEN Derived Market Metrics

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-live-002-uzen-derived-market-metrics`

## Goal

Compute deterministic market metrics from hoxit quote and bars so basic OHLCV-derived report fields do not remain missing when providers expose the required inputs.

## Scope

- Add market metric derivation helpers in `hoxit/uzen.py`.
- Derive:
  - `change_pct`
  - `change_amount`
  - `amplitude_pct`
  - `avg_price`
  - `return_5d`
  - `return_20d`
  - `ma5`
  - `ma20`
  - `volatility_20d`
  - `drawdown_60d`
- Add source/input quality metadata for derived fields where practical.
- Render the most important derived fields in Markdown without clutter.
- Preserve existing direct provider fields when present.

## Out of Scope

- No technical indicator library dependency.
- No visualization.
- No non-hoxit data collection.
- No trading recommendation language.

## Files Likely To Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/API_DEVLOG.md`

## Must Not Change

- `hoxit/market.py` unless a tiny field alias is necessary and justified.
- `hoxit/cli.py`
- `uzen-skills/`
- Later PR tickets.

## Acceptance Criteria

- If `quote.price` and `quote.last_close` are available, `analysis.summary.change_pct` is populated.
- If bars have enough close values, moving averages and returns are computed.
- Missing inputs produce `data_needed`/warnings rather than silent blanks.
- Existing tests continue passing.

## Required Tests

- Unit test for `change_pct` derived from `price` and `last_close`.
- Unit test for `change_amount` and `amplitude_pct`.
- Unit test for MA/return/volatility/drawdown from bars.
- Unit test for insufficient bars producing explicit missing metadata.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md
```

## Dependencies

Depends on PR-LIVE-001 approved or merged.

## Definition Of Done

- Tests pass.
- Derived metrics are visible in JSON and selected Markdown fields.
- Implementation report is written to `docs/superpowers/status/PR-LIVE-002-implementation.md`.
- Board marks PR-LIVE-002 as `REVIEW_READY`.

## Stop Condition

After implementation, verification, commit, push, implementation report, and board update, stop for Codex review.

## Rollback Notes

Revert the PR commit. Reports fall back to provider-direct market fields.
