# UZEN Skills

UZEN 是 `Reference/UZI-Skill` 的 A 股优先迁移层。
保留研究工作流、命令意图、投资者面板概念和风险检查，以 hoxit 为主要数据基底。

## 运行时行为（Runtime Behavior）

### 模式执行配置（Mode Execution Profiles）

每个命令只调用其需要的 data provider。跳过的 source 使用中性默认值（`{}` 或 `[]`）。

| 模式 | 调用的 Providers |
|------|-----------------|
| `analyze-stock` | 全部 20 个（完整覆盖） |
| `quick-scan` | quote, metrics, valuation, fundamentals, concept, fund_flow |
| `panel-only` | quote, metrics, valuation, fundamentals, finance |
| `scan-trap` | quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger |
| `lhb-analyzer` | quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup |
| `dcf` | quote, metrics, valuation, fundamentals, finance |
| `comps` | quote, metrics, fundamentals, industry |

未知模式回退到 `analyze-stock` 行为。

### 数据质量记录（Source Quality Records）

JSON 输出包含结构化的 `data_quality.sources`，质量值：
- `full`：数据完整
- `partial`：部分数据（如 F10 不支持）
- `missing`：数据缺失
- `error`：provider 异常
- `skipped`：模式跳过

跳过的 source 不影响顶层 `complete` 标志。

### Markdown 报告格式（Report Contract）

Markdown 使用紧凑、人类可读的格式：
- 行情：名称、最新价、涨跌幅
- 估值：前瞻 PE、PEG、PE TTM、PB、总市值
- 基本面：行业、ROE、净利润
- 研报/新闻/公告：数量 + 前 3 条标题
- 概念：逗号分隔名称
- 缺失数据：显示 `缺失` 或中文说明

### 分析模型（Analytical Models）

#### DCF 估值

轻量 DCF 模型，使用 hoxit 可用的估值和财务字段：

- 5 年显式预测 + 终值（Terminal Value）
- 默认假设：折现率（Discount Rate）10%、终端增长率（Terminal Growth）3%
- 敏感性分析：折现率 × 终端增长率 矩阵
- 输出：内在价值（Intrinsic Value）、安全边际（Margin of Safety）
- 数据不足时返回 `status: "data_needed"`

#### 同业比较（Comps）

基于行业横向对比的可比公司分析：

- 提取主体 PE TTM、PB
- 计算行业中位 PE/PB
- 判断估值位置：`below_median`、`near_median`、`above_median`
- 数据不足时返回 `status: "data_needed"`

#### 风险模型拆分

`scan-trap` 模式输出两个独立的风险对象：

**市场数据风险（market_risk）**：
- 基于可观测的市场数据：大宗交易、融资融券、股东户数变化、资金流
- 不暗示社交操纵或杀猪盘证据
- 输出：`level`、`basis: "market_data"`、`flags`

**社交/操纵风险（trap_risk）**：
- 当前状态：`status: "unsupported"`
- 社交证据采集尚未实现
- 输出：`status`、`basis: "social_evidence"`、`evidence`、`warnings`

#### 投资者面板信号

5 个确定性投资者原型：

| 投资者 | ID | 分组 | 判断依据 |
|--------|-----|------|----------|
| 价值投资者 | `value` | 基本面 | PE、PB |
| 质量投资者 | `quality` | 基本面 | ROE、净利润 |
| 成长投资者 | `growth` | 基本面 | 盈利增长、PEG |
| 动量投资者 | `momentum` | 技术面 | 涨跌幅、资金流、龙虎榜 |
| 游资关注者 | `hot_money` | 技术面 | 大宗交易、融资融券、股东户数、龙虎榜 |

每个信号包含：`signal`（pass/fail/neutral/data_needed）、`score`、`confidence`、`reasoning`。

聚合输出：`vote_distribution`（票数统计）、`score`（加权平均分）、`verdict`。

## 命令

- `analyze-stock`：完整 A 股分析报告
- `quick-scan`：快速扫描（行情、估值、资金流、题材、风险）
- `dcf`：轻量估值视图（DCF）
- `comps`：行业与同业对比
- `panel-only`：投资者面板摘要
- `scan-trap`：市场数据风险检查
- `lhb-analyzer`：龙虎榜专项分析

## 当前限制

- 仅支持 A 股
- 无 HTML 渲染或分享图
- 无 UZI 原 65 投资者完整对标
- 无 portfolio 命令
- F10 数据依赖 mootdx 支持
- DCF 使用净利润作为现金流代理（非自由现金流）
- 社交/操纵证据采集尚未实现

## 延迟能力（Deferred）

- HTML 报告和分享图
- Playwright 兜底
- 完整 65 投资者面板
- 社交情绪和操纵证据采集
- 历史龙虎榜席位模式
- 跨市场分析
- 自由现金流（Free Cash Flow）DCF
