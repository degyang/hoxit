# hoxit 接口调用说明

所有命令在项目虚拟环境下执行：

```bash
cd /Users/mac/Projects/hoxit
.venv/bin/hoxit --version
```

## 环境变量

调用需要密钥的接口前执行：

```bash
cd /Users/mac/Projects/hoxit
set -a
source .env.local
set +a
```

## 行情层

### mootdx 实时报价与五档盘口

默认输出 CSV：

```bash
.venv/bin/hoxit market quote 688017
.venv/bin/hoxit market quote 688017 300476
```

输出 JSON：

```bash
.venv/bin/hoxit market quote 688017 --format json
```

说明：优先使用 `mootdx`；如果 `mootdx` 失败或缺失代码，腾讯财经只作为 fallback。

### 腾讯估值指标

```bash
.venv/bin/hoxit market metrics 688017
.venv/bin/hoxit market metrics 688017 300476
```

返回 PE(TTM)、PB、市值、换手率、涨跌停、振幅等字段。

### mootdx K 线

```bash
.venv/bin/hoxit market bars 688017 --category 4 --offset 10
.venv/bin/hoxit market bars 688017 --category 4 --offset 250 --adjust qfq
```

常用 `category`：

```text
4  日线
5  周线
6  月线
7  1分钟
8  5分钟
9  15分钟
10 30分钟
11 60分钟
```

`--adjust` 支持：

```text
raw 不复权（默认）
qfq 前复权
hfq 后复权
```

### mootdx 逐笔成交

```bash
.venv/bin/hoxit market transactions 688017 --date 20260512
```

## 研报层

### 东财研报列表

```bash
.venv/bin/hoxit reports eastmoney 688017 --max-pages 2
```

### iwencai 语义搜索

```bash
set -a
source .env.local
set +a
.venv/bin/hoxit reports iwencai "人形机器人 丝杠 研报" --channel report --size 50
```

调用 iwencai 前先执行本文档“环境变量”步骤。

## 新闻层

### 个股新闻

```bash
.venv/bin/hoxit news stock 688017
```

### 财联社快讯

```bash
.venv/bin/hoxit news cls
```

说明：参考项目标记下线的是旧 `cls.cn/nodeapi/telegraphList`；hoxit 当前调用新版网页使用的 `cls.cn/v1/roll/get_roll_list`，请求参数带前端静态算法生成的 `sign`，无需用户申请 key。若后续签名算法或接口结构变化，可改用东财全球资讯。

### 东财全球资讯

```bash
.venv/bin/hoxit news global
```

## 基础数据层

### 东财个股基本面

```bash
.venv/bin/hoxit fundamentals info 688017
```

### mootdx 财务快照

```bash
.venv/bin/hoxit fundamentals finance 688017
```

### mootdx F10

```bash
.venv/bin/hoxit fundamentals f10 688017
```

说明：如果当前 `mootdx` client 不暴露 `f10()` 方法，hoxit 返回结构化降级结果：

```json
{"status": "unsupported", "sections": {}, "warnings": ["..."]}
```

此时用 `fundamentals info`、`fundamentals finance`、`filings cninfo`、`reports eastmoney` 作为替代事实源，不让完整分析链中断。

## 公告层

### 巨潮公告

```bash
.venv/bin/hoxit filings cninfo 688017 --start-date 20260101 --end-date 20260516
```

## 信号层

### 同花顺热点

```bash
.venv/bin/hoxit signals hot
.venv/bin/hoxit signals hot --date 2026-05-12
```

过滤 ST/*ST 股票：

```bash
.venv/bin/hoxit signals hot --date 2026-05-12 --exclude-st
```

### 北向资金实时

```bash
.venv/bin/hoxit signals northbound
```

写入本地缓存：

```bash
.venv/bin/hoxit signals northbound --date 2026-05-12 --cache-dir .cache
```

### 百度概念板块

```bash
.venv/bin/hoxit signals concept 688017
```

### 东财资金流向历史

```bash
.venv/bin/hoxit signals fund-flow 000858 --days 20
```

### 个股龙虎榜

```bash
.venv/bin/hoxit signals dragon-tiger 002475 --trade-date 2026-05-12
```

### 限售解禁

```bash
.venv/bin/hoxit signals lockup 002475 --trade-date 2026-05-12 --forward-days 90
```

### 行业横向对比

```bash
.venv/bin/hoxit signals industry --top-n 20
```

### 全市场龙虎榜

```bash
.venv/bin/hoxit signals daily-dragon-tiger --trade-date 2026-05-12
.venv/bin/hoxit signals daily-dragon-tiger --trade-date 2026-05-12 --min-net-buy 5000
```

## 估值流程

### 单票完整估值

```bash
.venv/bin/hoxit valuation full 688017
```


输出实时价格、PE/PB、市值、一致预期 EPS、前向 PE、PEG、PE 消化时间。

### 融资融券明细

```bash
.venv/bin/hoxit signals margin-trading 600519 --page-size 30
```

### 大宗交易

```bash
.venv/bin/hoxit signals block-trade 600519 --page-size 20
```

### 股东户数变化

```bash
.venv/bin/hoxit signals holder-num 600519 --page-size 10
```

### 分红送转历史

```bash
.venv/bin/hoxit signals dividend 600519 --page-size 20
```

## UZEN A股研究工作流

UZEN 是 `Reference/UZI-Skill` 的 A 股优先迁移层。通过 hoxit 数据接口生成 JSON 和 Markdown 报告，不启用 UZI 原 provider chain、HTML 渲染、分享图、Playwright 兜底或跨市场分析。

### 命令

```bash
.venv/bin/hoxit uzen analyze-stock 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen quick-scan 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen dcf 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen comps 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen panel-only 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen scan-trap 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen lhb-analyzer 600519 --trade-date 2026-06-14 --output-dir uzen-skills/reports
```

输出：

- `<code>-<mode>.json`
- `<code>-<mode>.md`

### 模式执行配置

每个模式只调用其需要的数据 provider，跳过的 source 使用中性默认值（`{}` 或 `[]`）。

| 模式 | 调用的 Providers |
|------|-----------------|
| `analyze-stock` | 全部 23 个（quote, bars, metrics, valuation, fundamentals, finance, f10, reports, news, filings, hot, concept, fund_flow, dragon_tiger, lockup, industry, margin_trading, block_trade, holder_num, dividend, governance, business, event） |
| `quick-scan` | quote, metrics, valuation, fundamentals, concept, fund_flow |
| `panel-only` | quote, metrics, valuation, fundamentals, finance |
| `scan-trap` | quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger |
| `lhb-analyzer` | quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup |
| `dcf` | quote, metrics, valuation, fundamentals, finance |
| `comps` | quote, metrics, fundamentals, industry |

未知模式回退到 `analyze-stock` 行为。

### 数据质量记录

JSON 输出包含结构化的 `data_quality.sources` 记录：

```json
{
  "data_quality": {
    "complete": true,
    "warnings": [],
    "sources": {
      "quote": {
        "label": "quote",
        "quality": "full",
        "source": "provider.quote",
        "warnings": [],
        "required": true,
        "optional_missing": []
      },
      "bars": {
        "label": "bars",
        "quality": "skipped",
        "source": "provider.bars",
        "warnings": [],
        "required": true,
        "optional_missing": []
      }
    }
  }
}
```

质量值：

- `full`：数据完整
- `partial`：部分数据（如 F10 不支持）
- `missing`：数据缺失
- `error`：provider 异常
- `skipped`：模式跳过

跳过的 source 不影响顶层 `complete` 标志。

### Markdown 报告格式

Markdown 报告使用紧凑、人类可读的格式：

- 行情：名称、最新价、涨跌幅
- 估值：前瞻 PE、PEG、PE TTM、PB、总市值
- 基本面：行业、ROE、净利润
- 研报/新闻/公告：数量 + 前 3 条标题
- 概念：逗号分隔的名称
- 治理与股权结构（Phase 6）：实控人、质押比例、高管持股、股东增减持
- 经营与产业链（Phase 6）：主营构成、客户/供应商集中度
- 事件与催化剂（Phase 6）：近期事件计数、催化剂、情绪标记（↑/↓/—）
- 龙虎榜详情（Phase 6）：记录数、最新上榜原因
- 缺失数据：显示 `缺失` 或中文说明

### 分析模型（Phase 3）

#### DCF 估值

轻量 DCF 模型，使用 hoxit 可用的估值和财务字段：

- 5 年显式预测 + 终值（Terminal Value）
- 默认假设：折现率 10%、终端增长率 3%
- 敏感性分析：折现率（8%/10%/12%）× 终端增长率（2%/3%/4%）
- 输出：内在价值（Intrinsic Value）、市场价格、安全边际（Margin of Safety）
- 数据不足时返回 `status: "data_needed"`，不产生虚假估值

#### 同业比较（Comps）

基于行业横向对比的可比公司分析：

- 提取主体 PE TTM、PB
- 从 `signals.industry` 获取同行 PE/PB 中位数
- 判断估值位置：`below_median`、`near_median`、`above_median`
- 数据不足时返回 `status: "data_needed"`

#### 风险模型拆分

`scan-trap` 模式现在输出两个独立的风险对象：

**市场数据风险（market_risk）**：
- 基于可观测的市场数据：大宗交易、融资融券、股东户数变化、资金流
- 不暗示社交操纵或杀猪盘证据
- 输出：`level`（low/medium/high）、`basis: "market_data"`、`flags`

**社交/操纵风险（trap_risk）**：
- 当前状态：`status: "unsupported"`
- 社交证据采集尚未实现
- 输出：`status`、`basis: "social_evidence"`、`evidence`、`warnings`

#### 投资者面板信号

5 个确定性投资者原型，每个产生独立信号：

| 投资者 | ID | 分组 | 判断依据 |
|--------|-----|------|----------|
| 价值投资者 | `value` | 基本面 | PE、PB |
| 质量投资者 | `quality` | 基本面 | ROE、净利润 |
| 成长投资者 | `growth` | 基本面 | 盈利增长、PEG |
| 动量投资者 | `momentum` | 技术面 | 涨跌幅、资金流、龙虎榜 |
| 游资关注者 | `hot_money` | 技术面 | 大宗交易、融资融券、股东户数、龙虎榜 |

每个信号包含：
- `signal`：`pass`（看多）、`fail`（看空）、`neutral`（中性）、`data_needed`（数据不足）
- `score`：0-100 分
- `confidence`：0.0-1.0 置信度
- `reasoning`：判断理由列表

聚合输出：
- `vote_distribution`：各信号类型的票数统计
- `score`：有效信号的加权平均分
- `verdict`：bullish（≥65）、bearish（≤40）、neutral（41-64）

### 模式特定 Markdown（Phase 4）

每个模式只渲染相关的 Markdown section，避免显示无关的 data_needed section：

| 模式 | 可见 Section |
|------|-------------|
| `analyze-stock` | 全部（含 Phase 6：治理与股权结构、经营与产业链、事件与催化剂、龙虎榜详情） |
| `quick-scan` | 核心结论、数据完整性、行情与估值、基本面与财务、资金/龙虎榜/题材、综合研判、后续跟踪项 |
| `dcf` | 核心结论、数据完整性、行情与估值、基本面与财务、DCF 估值、综合研判、后续跟踪项 |
| `comps` | 核心结论、数据完整性、行情与估值、基本面与财务、行业与同业、同业比较（Comps）、综合研判、后续跟踪项 |
| `panel-only` | 核心结论、数据完整性、行情与估值、基本面与财务、投资者面板、综合研判、后续跟踪项 |
| `scan-trap` | 核心结论、数据完整性、行情与估值、基本面与财务、市场数据风险检查、社交/操纵风险检查、综合研判、后续跟踪项 |
| `lhb-analyzer` | 核心结论、数据完整性、行情与估值、基本面与财务、资金/龙虎榜/题材、龙虎榜分析、综合研判、后续跟踪项 |

JSON artifact 不受影响（所有 analysis 对象保留）。

### 分析封套（Agent Analysis Envelope）

可选的定性分析封套，允许 agent 注入判断而不修改原始数据或确定性分析：

```bash
.venv/bin/hoxit uzen analyze-stock 600519 --agent-analysis agent.json
```

封套状态：
- `not_provided`：默认状态，不渲染 Markdown section
- `provided`：包含 agent 定性判断，渲染 "Agent 定性分析" section

封套结构：

```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "核心论点",
  "assumptions": ["假设1", "假设2"],
  "conflicts": ["矛盾/风险1"],
  "followups": ["后续验证项1"],
  "warnings": []
}
```

限制：
- 不修改 `sources`、`data_quality`、DCF、Comps、panel、risk 对象
- 不注入 LLM 调用
- 仅 JSON 格式

#### 深度审阅字段（Deep Review Fields，Phase 5）

封套扩展了 3 个可选字段，允许 agent 注入维度级评注：

```json
{
  "data_gap_acknowledged": {"lhb": "龙虎榜数据缺失"},
  "dimension_commentary": {"risk": "风险维度不完整"},
  "panel_insights": "投资者面板显示多空分歧"
}
```

- `data_gap_acknowledged`：`dict[str, str]`，agent 确认的数据缺口
- `dimension_commentary`：`dict[str, str]`，agent 对各维度的评注
- `panel_insights`：`str`，agent 对投资者面板的定性洞察

Phase 4 封套文件（不含新字段）仍然有效，新字段使用默认值。

### 维度层（Dimensions，Phase 5）

`analysis["dimensions"]` 包含 10 个确定性维度摘要，每个维度总结一个分析领域的状态：

| 维度 | 输入 | 说明 |
|------|------|------|
| `basic` | quote, fundamentals | 基础数据完整性 |
| `market` | quote, bars, metrics | 行情数据完整性 |
| `valuation` | valuation, metrics | 估值数据完整性 |
| `fundamentals` | fundamentals, finance, f10 | 基本面数据完整性 |
| `capital_flow` | concept, fund_flow, dragon_tiger | 资金流数据完整性 |
| `panel` | panel analysis | 投资者面板状态 |
| `risk` | market_risk, trap_risk | 风险维度状态 |
| `lhb` | lhb analysis | 龙虎榜状态 |
| `dcf` | dcf analysis | DCF 估值状态 |
| `comps` | comps analysis | 同业比较状态 |
| `governance` | governance | 治理与股权结构（Phase 6） |
| `business` | business | 经营与产业链（Phase 6） |
| `events` | event | 事件与催化剂（Phase 6） |
| `lhb_detail` | dragon_tiger | 龙虎榜详情（Phase 6） |
| `policy` | — | 政策维度（当前 unsupported） |
| `sentiment` | — | 情绪维度（当前 unsupported） |

每个维度包含：
- `status`：`computed`、`partial`、`data_needed`
- `quality`：`full`、`partial`、`missing`、`error`、`skipped`
- `inputs`：依赖的数据源列表
- `outputs`：产出的分析对象列表
- `warnings`：维度级警告

### 综合研判（Synthesis，Phase 5）

`analysis["synthesis"]` 从现有分析对象推导确定性综合判断：

```json
{
  "basis": "deterministic_hoxit_analysis",
  "stance": "bullish|neutral|bearish|data_needed",
  "confidence": "high|medium|low",
  "drivers": ["面板看多 65分"],
  "risks": ["社交/操纵风险检查尚未实现"],
  "conflicts": ["投资者面板内部存在多空分歧"],
  "followups": ["补充 lhb 维度数据"]
}
```

数据来源（仅使用允许的分析对象）：
- `panel` → 立场和驱动因素
- `market_risk` → 风险标记
- `dimensions["risk"]` → 风险维度警告
- `dcf` + `comps` → 矛盾信号检测
- `dimensions` + `lhb` → 数据缺口后续项
- `data_quality` → 置信度校准
- `governance` → 治理驱动/风险（Phase 6：实控人、质押比例）
- `business` → 经营驱动（Phase 6：主营构成）
- `event` → 事件驱动/风险（Phase 6：正面/负面事件计数）

置信度逻辑：
- `data_needed` 立场 → 始终 `low`
- 完整数据 + ≥3 同向投票 → `high`
- 完整数据 + ≥2 同向投票 → `medium`
- 其他 → `low`

### 报告自审（Report Review，Phase 5）

`analysis["report_review"]` 在 `run_analysis()` 中渲染 Markdown 后计算，审计 JSON 和 Markdown 产物契约：

```json
{
  "status": "passed|warnings",
  "checks": [
    {"name": "required_analysis_sections", "status": "passed", "warnings": []},
    {"name": "disclaimer_present", "status": "passed", "warnings": []},
    {"name": "no_raw_dict_repr", "status": "passed", "warnings": []},
    {"name": "mode_section_alignment", "status": "passed", "warnings": []},
    {"name": "unsupported_feature_wording", "status": "passed", "warnings": []}
  ],
  "warnings": []
}
```

非阻塞：状态为 `passed` 或 `warnings`，不会阻止报告生成。

### 龙虎榜分析（LHB Summary）

`lhb-analyzer` 模式包含确定性龙虎榜摘要：

```json
{
  "status": "computed",
  "rows": 1,
  "net_buy": 2000.0,
  "has_dragon_tiger": true,
  "signals": ["龙虎榜净买入为正", "龙虎榜共 1 条记录"],
  "warnings": []
}
```

信号：
- 净买入为正/净卖出/买卖平衡
- 记录数统计

限制：
- 不推断席位级别身份（机构 vs 游资）
- 不分析历史龙虎榜模式

### DCF/Comps 输入质量（Input Quality）

DCF 和 Comps 包含 `input_quality` 子对象，便于审计缺失数据行为：

**DCF 输入质量**：

```json
"input_quality": {
  "required": ["net_profit", "share_count"],
  "available": ["market_price", "net_profit", "share_count"],
  "missing": [],
  "proxy_used": ["net_profit_as_cash_flow"]
}
```

**Comps 输入质量**：

```json
"input_quality": {
  "peer_rows": 5,
  "pe_samples": 5,
  "pb_samples": 5,
  "missing": []
}
```

### Phase 6 数据覆盖（A 股特有维度）

Phase 6 通过 iwencai 适配器补充 A 股特有数据维度，仅在 `analyze-stock` 模式启用：

| 数据源 | hoxit 函数 | 内容 | 质量边界 |
|--------|-----------|------|----------|
| 治理与股权 | `fundamentals.governance_summary()` | 实控人、质押比例、高管持股、股东增减持 | 数据不足时返回 `data_needed` |
| 经营与产业链 | `fundamentals.business_summary()` | 主营构成、前五大客户/供应商、集中度 | 数据不足时返回 `data_needed` |
| 事件与催化剂 | `signals.event_summary()` | 近期事件、催化剂、情绪分类（positive/negative/neutral） | 关键词匹配分类，非 NLP |

#### 综合研判扩展

Phase 6 综合研判新增以下确定性推导：

- **治理驱动**：有实控人时输出 "实控人：{controller}"
- **治理风险**：质押比例 > 50% 时输出 "股权质押比例偏高"
- **经营驱动**：有主营构成时输出 "主营构成：{segment}"
- **事件驱动**：正面事件 > 负面事件时输出 "近期正面事件 N 条"
- **事件风险**：负面事件 > 正面事件时输出 "近期负面事件 N 条"

#### Phase 6 vs 延迟 UZI 维度

| 维度 | Phase 6 状态 | UZI 原始能力 | 说明 |
|------|-------------|-------------|------|
| 治理与股权 | ✅ 已实现 | ✅ | iwencai management route |
| 经营与产业链 | ✅ 已实现 | ✅ | iwencai business route |
| 事件与催化剂 | ✅ 已实现 | ✅ | iwencai event route + 情绪分类 |
| 龙虎榜详情 | ✅ 已实现 | ✅ | 扩展 dragon_tiger 信号 |
| 政策维度 | ❌ unsupported | ✅ | 无 A 股政策数据源 |
| 情绪维度 | ❌ unsupported | ✅ | 无社交情绪数据源 |
| 原材料/期货 | ❌ deferred | ✅ | 无期货数据源 |
| 护城河 | ❌ deferred | ✅ | 无定性评估框架 |
| 竞争格局 | ❌ deferred | ✅ | 无竞争分析框架 |

### Phase 7：Live Provider Contract Hardening

Phase 7 聚焦 UZEN 对真实 hoxit provider 输出的健壮性：

**Provider 归一化边界**（PR-LIVE-001/003）：
- DataFrame-like / 嵌套 dict / 中英文别名在 `collect_snapshot` 边界统一归一为标量 canonical 字段。
- 财务字段（ROE/净利润/营收等）8 组别名 + 4 组银行专项别名，first-wins 语义。
- pandas 单行 DataFrame `{0: 12.0}` 结构自动展平为标量。

**派生行情指标**（PR-LIVE-002）：
- 涨跌额/振幅/MA/收益率/波动率/回撤/成交均价从 quote + bars 确定性推导。
- 成交均价需明确 `vol_unit`（"股" 或 "手"），无法判断时返回 None + warning。

**字段级来源质量**（PR-LIVE-003）：
- 每个 finance 字段有 `status`（available/missing/unsupported）和 `source`（provider.finance / f10）。
- F10 sections 中的财务字段自动合并到 finance dict，不覆盖 provider 已有值。

**银行股报告**（PR-LIVE-004）：
- 银行股自动检测（industry/concept 关键词）。
- 银行专项指标：净息差 (NIM)、不良贷款率 (NPL)、拨备覆盖率、资本充足率。
- DCF 银行股警告："FCFF DCF 不适用"。
- 非银行 snapshot 不产生银行专项 quality records。

**Live Smoke Gate**（PR-LIVE-005）：
- 宁波银行 002142 作为 Phase 7 验收目标。
- `HOXIT_LIVE_TESTS=1` 启用 live smoke test，验证 JSON/Markdown 输出完整性。

**来源质量与 Fallback 策略**：
- hoxit-first：优先使用 hoxit 已有数据源，不引入 akshare。
- 字段级 fallback：缺失字段逐个评估，记录 status 和 warning。
- 不做 UZEN one-off scraper：如需新数据源，必须实现为可复用 hoxit helper 并附测试。
- 质量原因必填：数据缺失时必须说明原因。
- Web/Playwright 受控引入：需明确目标字段、页面、用户授权，由单独 ticket 管理。

### Web Fallback Provider（PR-LIVE-006）

hoxit 提供受控的 Playwright 浏览器兜底能力，从东财 F10 补全 provider 缺失的财务字段。

**默认关闭**：需设置 `HOXIT_WEB_FALLBACK=1` 环境变量启用。启用后 `collect_snapshot()` 自动尝试补全缺失字段。

**自动补全范围**：

| 场景 | 补全字段 | 数据源 |
|------|----------|--------|
| 银行股缺失专项指标 | npl_ratio, provision_coverage, capital_adequacy, core_capital_adequacy | 东财 F10 专项指标 |
| 所有股票缺失核心字段 | roe, net_margin, eps, book_value_per_share | 东财 F10 主要指标 |

**用法**：

```bash
# 启用 Playwright 补全
HOXIT_WEB_FALLBACK=1 .venv/bin/hoxit uzen analyze-stock 002142

# 不启用（默认）— 缺失字段标记为 data_needed
.venv/bin/hoxit uzen analyze-stock 002142
```

**拼音别名**：mootdx finance snapshot 返回的拼音字段名自动归一化：`jinglirun`→net_profit, `zhuyingshouru`→revenue, `zongguben`→total_shares, `zongzichan`→total_assets, `jingzichan`→total_equity, `meigujingzichan`→book_value_per_share, `yingyelirun`→operating_profit。

**错误分类**：

| 错误类型 | 说明 |
|----------|------|
| `WebTimeoutError` | 页面加载超时 |
| `WebNavigationError` | 导航失败（DNS、连接、HTTP 错误） |
| `WebExtractionError` | 字段提取失败 |
| `WebAuthRequiredError` | 需要登录 |
| `WebCaptchaError` | CAPTCHA 挑战 |

**测试**：使用 `FakeWebDriver` 注入预设页面内容，不依赖网络或浏览器。`_parse_cn_number` 和 `_extract_indicators_from_text` 有独立单元测试。

### 当前限制

- 仅支持 A 股
- 无 HTML 渲染或分享图
- 无 UZI 原 65 投资者完整对标
- 无 portfolio 命令
- F10 数据依赖 mootdx 支持
- DCF 使用净利润作为现金流代理（非自由现金流）
- 社交/操纵证据采集尚未实现

### 延迟能力

以下功能在后续阶段实现：

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
