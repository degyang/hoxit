# analyze-stock

运行完整 A 股 UZEN 报告。

## 执行路径

```bash
hoxit uzen analyze-stock <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用全部 20 个 provider（完整覆盖）：
- quote, bars, metrics, valuation, fundamentals, finance, f10
- reports, news, filings
- hot, concept, fund_flow, dragon_tiger, lockup, industry
- margin_trading, block_trade, holder_num, dividend

## 输出

- `<code>-analyze-stock.json` — 完整快照（含 sources、analysis、data_quality）
- `<code>-analyze-stock.md` — 紧凑 Markdown 报告

## JSON 结构

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
