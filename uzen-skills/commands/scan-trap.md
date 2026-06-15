# scan-trap

运行风险与杀猪盘检查。

## 执行路径

```bash
hoxit uzen scan-trap <code> --output-dir uzen-skills/reports
```

## Data Providers

调用 8 个 provider：
- quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger

## Mode Profile

- depth: `focused`
- primary_section: `trap_risk`

## 当前行为

第一版市场风险检测，使用 hoxit 量化信号。

### 数据输入

- Quote：`provider.quote`
- Bars：`provider.bars`
- Concept：`hoxit.signals.baidu_concept_blocks`
- Fund flow：`hoxit.signals.baidu_fund_flow_history`
- Margin trading：`hoxit.signals.margin_trading`
- Block trades：`hoxit.signals.block_trade`
- Holder changes：`hoxit.signals.holder_num_change`
- Dragon-tiger：`hoxit.signals.dragon_tiger_board`

### 风险评分规则

- 基础：无标记 → `low`
- 1-2 个标记 → `medium`
- 3+ 个标记 → `high`

### 输出

- `<code>-scan-trap.json` — 结构化风险数据
- `<code>-scan-trap.md` — Markdown 摘要

### JSON Schema（当前）

```json
{
  "level": "low",
  "flags": ["..."]
}
```

- `level`：`"low"`、`"medium"` 或 `"high"`
- `flags`：风险标记字符串列表

## 限制

这仅检测**市场风险信号**，不检测社交/操纵陷阱。

### 功能范围

- 识别可观测的量化风险指标
- 报告数据可用性和缺口
- 基于可用信号计算风险等级

### 不支持的功能

- 检测社交情绪或协调推广
- 识别操纵模式或假新闻
- 分析论坛活动或 KOL 行为
- 提供陷阱指控的证据 URL

参见 `uzen-skills/skills/trap-detector/SKILL.md`：
- 完整风险类别区分
- 延迟的 UZI 风格陷阱证据
- 证据 URL 和关键词要求
- 社交声明的不捏造规则
