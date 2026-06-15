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

## 投资者面板模型

5 个确定性投资者原型，每个产生独立信号：

### 投资者原型

| 投资者 | ID | 分组 | 判断依据 |
|--------|-----|------|----------|
| 价值投资者 | `value` | 基本面 | PE、PB |
| 质量投资者 | `quality` | 基本面 | ROE、净利润 |
| 成长投资者 | `growth` | 基本面 | 盈利增长、PEG |
| 动量投资者 | `momentum` | 技术面 | 涨跌幅、资金流、龙虎榜 |
| 游资关注者 | `hot_money` | 技术面 | 大宗交易、融资融券、股东户数、龙虎榜 |

### 信号结构

每个投资者信号包含：

```json
{
  "investor_id": "value",
  "name": "价值投资者",
  "group": "fundamental",
  "signal": "pass",
  "score": 70,
  "confidence": 0.75,
  "reasoning": ["PE 12.0 倍，估值偏低"]
}
```

- `signal`：`"pass"`（看多）、`"fail"`（看空）、`"neutral"`（中性）、`"data_needed"`（数据不足）
- `score`：0-100 分
- `confidence`：0.0-1.0 置信度
- `reasoning`：判断理由列表

### 聚合输出

```json
{
  "score": 65,
  "verdict": "bullish",
  "reasons": ["价值投资者：PE 12.0 倍，估值偏低", "..."],
  "signals": ["..."],
  "vote_distribution": { "pass": 3, "fail": 0, "neutral": 1, "data_needed": 1 }
}
```

- `vote_distribution`：各信号类型的票数统计
- `score`：有效信号的加权平均分（排除 data_needed）
- `verdict`：`"bullish"` (≥65)、`"bearish"` (≤40)、`"neutral"` (41-64)

### 输出

- `<code>-panel-only.json` — 结构化面板数据
- `<code>-panel-only.md` — 紧凑 Markdown 摘要

## 限制

- 这**不**等同于 UZI 完整 65 投资者面板
- 仅包含 5 个确定性基线投资者
- 无 LLM 角色扮演
- 缺失数据时输出 `data_needed` 信号，不产生虚假判断

参见 `uzen-skills/skills/investor-panel/SKILL.md`：
- 目标投资者信号 schema
- 完整 UZI 投资者对标状态
- 推荐的未来投资者分组
