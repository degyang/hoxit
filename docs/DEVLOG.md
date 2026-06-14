# Dev Log

接口变更和健壮性同步记录见 [API_DEVLOG.md](API_DEVLOG.md)。

## 2026-06-09

- Checked `Reference/a-stock-data` latest `v3.2.2` changes against hoxit interface modules.
- Confirmed hoxit already includes Eastmoney throttling, Eastmoney concept blocks, Eastmoney stock-news list parsing compatibility, Cailianpress deprecation, and cninfo dynamic orgId lookup.
- Added known cninfo orgId fallback mapping for cases where the live mapping endpoint is unavailable.
- Added `docs/API_DEVLOG.md` for ongoing external-interface robustness tracking.
- Verified with `pytest -q`: 71 passed, 26 skipped.

## 2026-05-21

- Added `Reference/skills-iwencai-all` as a symlink under `Reference/` for local route reference.
- Added `hoxit.iwencai` as a shared adapter for `query2data` and `comprehensive_search`.
- Switched `reports.iwencai_search()` to the shared adapter so `report-search` uses the canonical route table and headers.
- Added fallback paths for `fundamentals.individual_info()`, `filings.cninfo_reports()`, and `signals.daily_dragon_tiger()` using iWencai where the response shape can be mapped cleanly.
- Added tests for the adapter, the wrapper, and the fallback paths.
