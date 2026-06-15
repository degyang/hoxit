# dcf

运行轻量 DCF 估值视图。

## 执行路径

```bash
hoxit uzen dcf <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用 5 个 provider：
- quote, metrics, valuation, fundamentals, finance

## 输出

- `<code>-dcf.json` — 估值聚焦快照
- `<code>-dcf.md` — 紧凑 Markdown 报告

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `valuation`

## DCF 模型

轻量 DCF 模型，使用 hoxit 可用的估值和财务字段：

### 输入数据

- 市场价格：`quote.price`
- 净利润（用作现金流代理）：`finance.net_profit`
- 总股本：`metrics.total_shares` 或 `finance.total_shares`
- 盈利增长率：`valuation.earnings_growth` 或 `metrics.profit_growth`

### 默认假设

- 折现率（Discount Rate）：10%
- 终端增长率（Terminal Growth）：3%
- 显式预测期：5 年

### 输出结构

```json
{
  "status": "computed",
  "inputs": { "market_price": 20.0, "net_profit": 500000000, "share_count": 1000000000, "growth_rate": 15.0 },
  "assumptions": { "discount_rate": {"value": 10.0}, "terminal_growth": {"value": 3.0} },
  "intrinsic_value_per_share": 25.50,
  "market_price": 20.0,
  "margin_of_safety": 27.50,
  "sensitivity": [
    {"discount_rate": 8.0, "terminal_growth": 2.0, "intrinsic_value_per_share": 30.00},
    "..."
  ],
  "warnings": []
}
```

### 敏感性分析

3×3 矩阵：折现率（8%/10%/12%）× 终端增长率（2%/3%/4%）

## 限制

- 使用净利润作为现金流代理，非自由现金流（Free Cash Flow）
- 数据不足时返回 `status: "data_needed"`，不产生虚假估值
- 完整 UZI DCF 对标已延迟
