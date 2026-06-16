# UZEN Skills

UZEN 是 `Reference/UZI-Skill` 的 A 股优先迁移层。
保留研究工作流、命令意图、投资者面板概念和风险检查，以 hoxit 为主要数据基底。

## 运行时行为（Runtime Behavior）

### 模式执行配置（Mode Execution Profiles）

每个命令只调用其需要的 data provider。跳过的 source 使用中性默认值（`{}` 或 `[]`）。

| 模式 | 调用的 Providers |
|------|-----------------|
| `analyze-stock` | 全部 23 个（完整覆盖，含 Phase 6：governance, business, event） |
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
- 治理与股权结构（Phase 6）：实控人、质押比例、高管持股、股东增减持
- 经营与产业链（Phase 6）：主营构成、客户/供应商集中度
- 事件与催化剂（Phase 6）：近期事件计数、催化剂、情绪标记（↑/↓/—）
- 龙虎榜详情（Phase 6）：记录数、最新上榜原因
- 缺失数据：显示 `缺失` 或中文说明

### 模式特定 Markdown（Mode-Specific Markdown）

每个模式只渲染相关的 Markdown section，避免显示无关的 data_needed section。

JSON artifact 不受影响（所有 analysis 对象保留）。

### 分析封套（Agent Analysis Envelope）

可选的定性分析封套，允许 agent 注入判断而不修改原始数据或确定性分析：

```bash
hoxit uzen analyze-stock 600519 --agent-analysis agent.json
```

封套状态：
- `not_provided`：默认状态，不渲染 Markdown section
- `provided`：包含 agent 定性判断，渲染 "Agent 定性分析" section

Phase 5 扩展字段（可选）：
- `data_gap_acknowledged`：`dict[str, str]`，agent 确认的数据缺口
- `dimension_commentary`：`dict[str, str]`，agent 对各维度的评注
- `panel_insights`：`str`，agent 对投资者面板的定性洞察

Phase 4 封套文件仍然有效，新字段使用默认值。

限制：不修改 sources、data_quality、DCF、Comps、panel、risk 对象。

### 维度层（Dimensions）

`analysis["dimensions"]` 包含 16 个确定性维度摘要，每个维度包含 `status`、`quality`、`inputs`、`outputs`、`warnings`：

- 基础层：basic, market, valuation, fundamentals, capital_flow, panel, risk, lhb, dcf, comps
- Phase 6：governance（治理与股权）、business（经营与产业链）、events（事件与催化剂）、lhb_detail（龙虎榜详情）
- 延迟（unsupported）：policy（政策）、sentiment（情绪）

### 综合研判（Synthesis）

`analysis["synthesis"]` 从 panel、market_risk、dimensions、dcf、comps、lhb、data_quality、governance、business、event 推导确定性综合判断，包含 `stance`、`confidence`、`drivers`、`risks`、`conflicts`、`followups`。无 LLM 调用。

Phase 6 扩展推导：
- 治理驱动/风险：实控人信息、质押比例偏高（> 50%）
- 经营驱动：主营构成
- 事件驱动/风险：正面/负面事件计数

### 报告自审（Report Review）

`analysis["report_review"]` 在 `run_analysis()` 中渲染 Markdown 后计算，审计 JSON 和 Markdown 产物契约。包含 5 个检查项：required_analysis_sections、disclaimer_present、no_raw_dict_repr、mode_section_alignment、unsupported_feature_wording。非阻塞：状态为 `passed` 或 `warnings`。

### 龙虎榜分析（LHB Summary）

`lhb-analyzer` 模式包含确定性龙虎榜摘要，从 `sources.signals.dragon_tiger` 推导：
- 行数统计
- 净买入合计
- 简单信号（净买入为正/净卖出/买卖平衡）

限制：不推断席位级别身份（机构 vs 游资）。

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

#### DCF/Comps 输入质量（Input Quality）

DCF 和 Comps 包含 `input_quality` 子对象，便于审计缺失数据行为：

**DCF 输入质量**：
- `required`：必需输入键列表
- `available`：可用输入键列表
- `missing`：缺失输入键列表
- `proxy_used`：使用的代理指标列表

**Comps 输入质量**：
- `peer_rows`：同业行数
- `pe_samples`：有效 PE 样本数
- `pb_samples`：有效 PB 样本数
- `missing`：缺失输入键列表

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

## Phase 6 数据覆盖

Phase 6 通过 iwencai 适配器补充 A 股特有数据维度（仅 `analyze-stock` 模式）：

| 数据源 | hoxit 函数 | 内容 |
|--------|-----------|------|
| 治理与股权 | `fundamentals.governance_summary()` | 实控人、质押比例、高管持股、股东增减持 |
| 经营与产业链 | `fundamentals.business_summary()` | 主营构成、前五大客户/供应商、集中度 |
| 事件与催化剂 | `signals.event_summary()` | 近期事件、催化剂、情绪分类 |

综合研判扩展：治理驱动/风险、经营驱动、事件驱动/风险（确定性推导，无 LLM）。

### Phase 6 vs 延迟 UZI 维度

| 维度 | 状态 | 说明 |
|------|------|------|
| 治理与股权 | ✅ | iwencai management route |
| 经营与产业链 | ✅ | iwencai business route |
| 事件与催化剂 | ✅ | iwencai event route + 情绪分类 |
| 龙虎榜详情 | ✅ | 扩展 dragon_tiger 信号 |
| 政策维度 | ❌ | 无 A 股政策数据源 |
| 情绪维度 | ❌ | 无社交情绪数据源 |
| 原材料/期货 | ❌ | 无期货数据源 |
| 护城河 | ❌ | 无定性评估框架 |
| 竞争格局 | ❌ | 无竞争分析框架 |

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
- 政策维度分析（需 A 股政策数据源）
- 社交情绪维度（需社交数据源）
- 原材料/期货维度（需期货数据源）
- 护城河定性评估（需评估框架）
- 竞争格局分析（需竞争数据框架）
