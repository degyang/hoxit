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
| `analyze-stock` | 全部（quote, bars, metrics, valuation, fundamentals, finance, f10, reports, news, filings, hot, concept, fund_flow, dragon_tiger, lockup, industry, margin_trading, block_trade, holder_num, dividend） |
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
