# PR-LIVE-005 Implementation Report

## Summary

Live smoke gate and documentation sync for Phase 7. Added optional UZEN live smoke test for Ningbo Bank (002142) and documented Phase 7 provider contract, source quality evaluation, and fallback policy.

## What Changed

### `tests/test_live_endpoints.py`

- **`test_live_uzen_ningbo_bank_smoke(tmp_path)`** — new integration test:
  - Skipped by default (`HOXIT_LIVE_TESTS=1` required).
  - Runs `run_analysis("002142", mode="analyze-stock")`.
  - Validates:
    - JSON and Markdown output files exist.
    - `analysis.summary.change_pct` is not None.
    - Core sections present: panel, dcf, bank_metrics, synthesis.
    - 002142 detected as bank stock (`bank_metrics.is_bank == True`).
    - DCF has FCFF/银行 warning.
    - `data_quality.sources` has field-level status (finance.roe, finance.nim, etc.).
    - Markdown contains "基本面与财务" and "银行专项指标".
    - No raw dict/list repr in Markdown.

### `docs/INTERFACES.md`

- Added **Phase 7：Live Provider Contract Hardening** section:
  - Provider 归一化边界（PR-LIVE-001/003）
  - 派生行情指标（PR-LIVE-002）
  - 字段级来源质量（PR-LIVE-003）
  - 银行股报告（PR-LIVE-004）
  - Live Smoke Gate（PR-LIVE-005）
  - 来源质量与 Fallback 策略

### `uzen-skills/README.md`

- Added **Phase 7** section with summary table.
- Added **来源质量与 Fallback 策略** table:
  - hoxit-first / 字段级 fallback / 无 one-off scraper / 质量原因必填 / Web 受控

### `docs/API_DEVLOG.md`

- Added PR-LIVE-005 entry documenting live smoke gate and docs sync.

## Verification

```
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v  → 258 passed
.venv/bin/python -m pytest                                           → 358 passed, 30 skipped
.venv/bin/python -m pytest tests/test_live_endpoints.py -v           → 30 skipped (offline)
.venv/bin/hoxit uzen --help                                          → Normal output
git diff --check -- docs hoxit tests uzen-skills                     → No whitespace issues
```

## Live Smoke Status

The live smoke test (`test_live_uzen_ningbo_bank_smoke`) is designed to run with:
```bash
set -a; source .env.local; set +a; HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -k uzen -v
```

This PR does NOT run the live smoke (requires network + data dependencies). The test validates JSON/Markdown output structure, bank detection, DCF warnings, field-level quality, and core report sections.

## Base Branch

Built on top of `agent/cc/pr-live-004-bank-report-quality-ningbo` (PR-LIVE-004 latest).

## Status

Ready for Codex review.
