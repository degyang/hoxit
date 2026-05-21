# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install (dev mode)
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"

# Add optional data dependencies (mootdx, pandas, requests, stockstats)
.venv/bin/python -m pip install -e ".[data]"

# Run all unit tests (no network)
.venv/bin/python -m pytest

# Run tests verbosely
.venv/bin/python -m pytest -v

# Run a single test file
.venv/bin/python -m pytest tests/test_market.py

# Run a single test case
.venv/bin/python -m pytest tests/test_signals.py::test_ths_hot_reason

# Run live integration tests (requires network + data deps)
HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -v

# Run CLI
.venv/bin/hoxit --help
```

## Architecture

A-share data toolkit organized into seven data layers. Each layer is a flat module in `hoxit/`. The CLI (`cli.py`) dispatches via argparse → lazy-imported functions.

### Seven Layers

| Layer | Module | Purpose |
|---|---|---|
| Market | `market.py` | Real-time quotes, K-line bars, tick transactions |
| Reports | `reports.py` | Research reports (EastMoney), iwencai semantic search |
| News | `news.py` | Stock news, flash news, global news |
| Fundamentals | `fundamentals.py` | Individual info, financial snapshot, F10 |
| Filings | `filings.py` | CNINFO regulatory filings |
| Signals | `signals.py` | Hot reasons, northbound flow, concept blocks, fund flow, dragon-tiger board, lockup expiry, industry comparison |
| Valuation | `valuation.py` | Full valuation, forward PE, PEG calculation |

Supporting modules:
- `utils.py` — Shared helpers (code normalization, date iteration, etc.), zero dependencies
- `iwencai.py` — iwencai API adapter used by reports/fundamentals/filings
- `cli.py` — argparse entry point, lazy-imports the layer above

### Key Design Principles

1. **Network I/O injectable** — Functions accept `http_get`/`http_post`/`urlopen` parameters for testability without network calls.
2. **Third-party deps lazily imported** — `requests`, `pandas`, `mootdx`, `stockstats` are imported inside function bodies, not at module top level. Tests work with only stdlib + pytest.
3. **Stable return types** — Functions return `dict` or `list[dict]`; pandas DataFrames are kept at the boundary.
4. **Backward compatibility** — Old function names kept as aliases (e.g., `tencent_quote = tencent_metrics`).

### Testing Pattern

Default test suite runs without any network access or third-party data dependencies. HTTP-dependent functions receive injected callables. `conftest.py` provides:
- `JsonResponse` / `TextResponse` — mock HTTP response wrappers
- `FakeDataFrame` / `FakeSeries` — pandas-free DataFrame stand-ins
- `FakeMootdxClient` — mootdx TCP client mock

Integration tests in `test_live_endpoints.py` are gated behind `HOXIT_LIVE_TESTS=1` and marked with `@pytest.mark.integration`.

### Data Sources

- **mootdx** — TCP-based quote client (market quotes, K-line, transactions)
- **Tencent** — HTTP API for PE/PB/market cap metrics
- **EastMoney** — Reports, news, fund flow, dragon-tiger board
- **CNINFO** — Regulatory filings
- **iwen cai** — Semantic search (used as fallback/adapter across multiple layers)
- **Baidu** — Concept blocks, fund flow history
- **THS (Tonghuashun)** — Hot reasons, EPS forecasts

### Environment

- API keys in `.env.local` (loaded manually before CLI: `set -a; source .env.local; set +a`)
- `IWENCAI_BASE_URL` and `IWENCAI_API_KEY` required for iwencai endpoints
