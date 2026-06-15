# scan-trap

运行市场数据风险检查。

## 执行路径

```bash
hoxit uzen scan-trap <code> --output-dir uzen-skills/reports
```

## 数据提供方（Data Providers）

调用 8 个 provider：
- quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `market_risk`

## 风险模型拆分

`scan-trap` 模式输出两个独立的风险对象：

### 市场数据风险（market_risk）

基于可观测的市场数据，不暗示社交操纵或杀猪盘证据。

#### 数据输入

- 大宗交易：`signals.block_trade`
- 融资融券：`signals.margin_trading`
- 股东户数变化：`signals.holder_num`
- 资金流：`signals.fund_flow`

#### 风险评分规则

- 基础：无标记 → `low`
- 1-2 个标记 → `medium`
- 3+ 个标记 → `high`

#### 输出结构

```json
{
  "level": "medium",
  "basis": "market_data",
  "flags": ["存在大宗交易记录", "存在融资融券变化记录"]
}
```

### 社交/操纵风险（trap_risk）

社交证据采集尚未实现，当前返回 `status: "unsupported"`。

#### 输出结构

```json
{
  "status": "unsupported",
  "basis": "social_evidence",
  "evidence": [],
  "warnings": ["社交/操纵证据采集尚未实现"]
}
```

### 输出

- `<code>-scan-trap.json` — 结构化风险数据（含 market_risk 和 trap_risk）
- `<code>-scan-trap.md` — Markdown 摘要

## 限制

### 功能范围

- 识别可观测的量化风险指标
- 报告数据可用性和缺口
- 基于可用信号计算风险等级
- 明确区分市场数据风险和社交/操纵风险

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
