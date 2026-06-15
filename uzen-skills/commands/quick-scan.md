# quick-scan

运行紧凑 A 股扫描。

## 执行路径

```bash
hoxit uzen quick-scan <code> --output-dir uzen-skills/reports
```

## Data Providers

仅调用 6 个 provider：
- quote, metrics, valuation, fundamentals
- concept, fund_flow

跳过的 provider 使用中性默认值（`{}` 或 `[]`）。

## 关注领域

行情、估值、资金流、题材和风险标记。

## 输出

- `<code>-quick-scan.json` — 紧凑快照
- `<code>-quick-scan.md` — 紧凑 Markdown 报告

## Mode Profile

- depth: `lite`
- primary_section: `summary`
