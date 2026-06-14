# Incremental Skill Migration Design

Date: 2026-06-10

Purpose: define how `skills-tos-funder` should continue migrating `Reference/ai-hedge-fund` capabilities into POS while keeping executable code in hoxit.

Execution binding source: `docs/tos-funder/18-hoxit-execution-binding.md`.

## Boundary

The hoxit repository is the executable layer. POS `skills-tos-funder` is the interaction and orchestration layer.

Do:

- Add or extend hoxit Python modules and CLI/API functions when a capability needs executable logic.
- Add POS skill commands only as thin wrappers that describe how to call existing hoxit capabilities.
- Add hoxit tests first for every executable increment.
- Keep migration docs under `hoxit/docs/tos-funder/`.
- Maintain `docs/tos-funder/18-hoxit-execution-binding.md` so every POS command maps to existing hoxit executable routes or to upstream tos-funder command outputs.

Do not:

- Add a second runtime registry in POS.
- Add a separate `hoxit tos-funder` registry if equivalent hoxit commands/modules already exist.
- Duplicate hoxit logic inside POS markdown commands.
- Treat command markdown parity as executable parity.

## Increment Unit

Each increment should contain exactly one capability slice:

1. **hoxit executable change**: function, CLI route, or helper module.
2. **hoxit tests**: offline unit tests first; live tests only behind `HOXIT_LIVE_TESTS=1`.
3. **POS skill wrapper**: command/reference update pointing to the hoxit route.
4. **docs update**: update `docs/tos-funder/*` with status, validation, and known gaps.

## Current Migration Mode

Current POS skill commands are mostly command specifications. Future work should convert the highest-value specs into hoxit executable capabilities one by one.

Suggested next executable increments:

| Increment | hoxit target | POS wrapper |
|---|---|---|
| Price-series canonicalizer | existing `market bars`; add stable adapter/test if needed | `/tos-funder-quant-price-series` |
| Quant fundamentals scorer | hoxit fundamentals/iwencai scoring function | `/tos-funder-quant-fundamentals` |
| Technical indicators | local MA/RSI/MACD/ATR from OHLCV | `/tos-funder-quant-technicals` |
| Risk manager | volatility/drawdown/VaR/liquidity/correlation | `/tos-funder-risk-manager` |
| Sentiment/event proxy | announcement/report classifier | `/tos-funder-quant-sentiment` |
| Portfolio synthesizer | signal aggregation and final action constraints | `/tos-funder-portfolio` |

Only after these shared primitives are executable should persona commands add specialized scoring. Persona commands should consume hoxit primitive outputs rather than re-querying all data independently.

## TDD Rule

For every increment:

1. Add a failing hoxit test under `tests/`.
2. Implement the minimal hoxit code.
3. Run `python3 -m pytest`.
4. Update POS skill docs only after the hoxit test is green.

## Validation Layers

| Layer | Location | Purpose |
|---|---|---|
| Unit tests | `hoxit/tests/` | deterministic logic, routing, schema contracts |
| Live tests | `tests/test_live_endpoints.py` or new integration tests | external data checks behind env flag |
| Skill parity tests | `tests/test_tos_funder_migration.py` | ensure POS wrappers match migrated capabilities |
| Validation docs | `docs/tos-funder/validation-*.md` | sample-based manual audit trail |

## Design Principle

Build bottom-up:

1. Data adapters.
2. Deterministic factors.
3. Shared signals.
4. Persona overlays.
5. Portfolio synthesis.
6. Backtesting / quant lab.

This avoids duplicating collection/scoring logic across persona commands and keeps POS skills lightweight.
