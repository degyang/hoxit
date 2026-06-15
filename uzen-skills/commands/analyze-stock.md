# analyze-stock

Run a full A-share UZEN report.

## Execution Path

```bash
hoxit uzen analyze-stock <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls all 20 providers (full coverage):
- quote, bars, metrics, valuation, fundamentals, finance, f10
- reports, news, filings
- hot, concept, fund_flow, dragon_tiger, lockup, industry
- margin_trading, block_trade, holder_num, dividend

## Output

- `<code>-analyze-stock.json` — Full snapshot with sources, analysis, and data_quality
- `<code>-analyze-stock.md` — Compact Markdown report

## JSON Structure

```json
{
  "code": "600519",
  "market": "A",
  "mode": "analyze-stock",
  "data_quality": {
    "complete": true,
    "warnings": [],
    "sources": { "...": { "quality": "full", "..." : "..." } }
  },
  "sources": { "..." : "..." },
  "analysis": { "..." : "..." }
}
```
