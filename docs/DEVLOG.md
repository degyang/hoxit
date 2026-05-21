# Dev Log

## 2026-05-21

- Added `Reference/skills-iwencai-all` as a symlink under `Reference/` for local route reference.
- Added `hoxit.iwencai` as a shared adapter for `query2data` and `comprehensive_search`.
- Switched `reports.iwencai_search()` to the shared adapter so `report-search` uses the canonical route table and headers.
- Added fallback paths for `fundamentals.individual_info()`, `filings.cninfo_reports()`, and `signals.daily_dragon_tiger()` using iWencai where the response shape can be mapped cleanly.
- Added tests for the adapter, the wrapper, and the fallback paths.

