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

## 命令

- `analyze-stock`：完整 A 股分析报告
- `quick-scan`：快速扫描（行情、估值、资金流、题材、风险）
- `dcf`：轻量估值视图
- `comps`：行业与同业对比
- `panel-only`：投资者面板摘要
- `scan-trap`：风险与杀猪盘检查
- `lhb-analyzer`：龙虎榜专项分析

## 当前限制

- 仅支持 A 股
- 无 HTML 渲染或分享图
- 无 UZI 原 22 维度完整对标
- 无 portfolio 命令
- F10 数据依赖 mootdx 支持

## 延迟能力（Deferred）

- HTML 报告和分享图
- Playwright 兜底
- 完整 65 投资者面板
- 社交情绪和操纵证据
- 历史龙虎榜席位模式
- 跨市场分析
