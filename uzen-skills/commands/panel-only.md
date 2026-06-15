# panel-only

运行投资者面板摘要（不含完整报告）。

## 执行路径

```bash
hoxit uzen panel-only <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用 5 个 provider：
- quote, metrics, valuation, fundamentals, finance

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `panel`

## 当前行为

第一版轻量面板，基于估值和财务质量指标。

### 评分规则

- 基础分：50
- +10：PE < 20（估值有吸引力）
- -15：PE > 60（估值偏高）
- +10：ROE ≥ 10（盈利质量）

### 输出

- `<code>-panel-only.json` — 结构化面板数据
- `<code>-panel-only.md` — 紧凑 Markdown 摘要

### JSON Schema（当前）

```json
{
  "score": 50,
  "verdict": "neutral",
  "reasons": ["..."]
}
```

- `score`：整数 0-100
- `verdict`：`"bullish"` (≥65)、`"bearish"` (≤40)、`"neutral"` (41-64)
- `reasons`：解释字符串列表

## 限制

这**不**等同于 UZI 完整 65 投资者面板。这是确定性的第一版近似。

参见 `uzen-skills/skills/investor-panel/SKILL.md`：
- 目标投资者信号 schema
- 完整 UZI 投资者对标状态
- 推荐的未来投资者分组
