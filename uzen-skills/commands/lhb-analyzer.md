# lhb-analyzer

运行龙虎榜专项分析。

## 执行路径

```bash
hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD --output-dir uzen-skills/reports
```

## 必需参数

- `code`：6 位 A 股代码
- `--trade-date`：龙虎榜日期（`YYYY-MM-DD` 格式）

## 数据提供方（Data Providers）

调用 7 个 provider：
- quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup

## 模式配置（Mode Profile）

- depth: `focused`
- primary_section: `dragon_tiger`

## 当前行为

第一版龙虎榜分析，使用 hoxit 个股数据。

### 数据输入（当前已接入）

通过 `default_provider()` 接入 `hoxit.uzen lhb-analyzer`：

- 单股龙虎榜：`hoxit.signals.dragon_tiger_board`
- 资金流：`hoxit.signals.baidu_fund_flow_history`
- 大宗交易：`hoxit.signals.block_trade`
- 融资融券：`hoxit.signals.margin_trading`
- 限售解禁：`hoxit.signals.lockup_expiry`

### 可用但未接入

hoxit 中存在但未连接到 UZEN：

- 全市场龙虎榜：`hoxit.signals.daily_dragon_tiger`

### 输出

- `<code>-lhb-analyzer.json` — 结构化龙虎榜数据
- `<code>-lhb-analyzer.md` — Markdown 摘要

### 当前限制

- 仅个股数据（无席位级别详情）
- 无席位分类（机构 vs 游资）
- 无同行排名或领涨对比
- 无历史模式分析

## 功能范围

- 报告龙虎榜出现和基本指标
- 与资金流和大宗交易数据交叉引用
- 识别龙虎榜原因（涨幅偏离、跌幅偏离、换手率达20%）
- 标注数据可用性和缺口

## 不支持的功能

- 分类单个交易席位
- 识别机构 vs 游资活动
- 对比板块内股票领涨地位
- 分析历史龙虎榜模式

## 未来增强

参见 `uzen-skills/skills/lhb-analyzer/SKILL.md`：
- 目标席位 schema（含分类）
- 机构 vs 游资分析框架
- 板块和同行领涨对比
- 延迟的 hoxit API（席位数据库、同行排名）
