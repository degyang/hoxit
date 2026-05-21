---
name: a-stock-data
description: A股全栈数据工具包。通过 /Users/mac/Projects/hoxit 中的统一主命令 hoxit 和 hoxit Python 包覆盖行情、研报、信号、新闻、基础数据、公告、估值七类能力；Skill 只负责激活和选路，确定性执行逻辑由脚本与测试保障。
origin: custom
version: 2.2
---

# A股全栈数据工具包 V2.2

本 Skill 已从“Markdown 内嵌大段代码”改为“Skill 选路 + Python 脚本执行”模式。

项目主页：https://github.com/simonlin1212/a-stock-data

## When to Activate

当用户询问 A 股相关数据、估值、研报、行情、资金、题材、公告、龙虎榜、解禁、行业轮动时启用本 Skill。

关键词包括：估值、一致预期、PE、PB、PEG、市值、研报、产业链、K线、盘口、公告、新闻、强势股、题材、热点、概念、北向资金、主力资金、龙虎榜、席位、解禁、限售、行业对比、行业轮动。

## 虚拟环境

程序必须在项目虚拟环境中执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

真实数据接口需要额外安装数据依赖：

```bash
.venv/bin/python -m pip install -e ".[data]"
```

## 统一主命令

主命令为 `hoxit`。每个数据层对应一个子命令组，输出统一为 JSON。

### 环境变量

调用需要密钥的接口前执行：

```bash
cd /Users/mac/Projects/hoxit
set -a
source .env.local
set +a
```

```bash
hoxit market quote 688017 300476
hoxit market quote 688017 --format json
hoxit market metrics 688017 300476
hoxit market bars 688017 --category 4 --offset 10
hoxit market transactions 688017 --date 20260512
hoxit reports eastmoney 688017 --max-pages 2
hoxit reports iwencai "人形机器人 丝杠 研报" --size 50
hoxit news stock 688017
hoxit fundamentals info 688017
hoxit filings cninfo 688017 --start-date 20260101 --end-date 20260516
hoxit signals hot --date 2026-05-12
hoxit signals hot --date 2026-05-12 --exclude-st
hoxit signals concept 688017
hoxit signals fund-flow 000858 --days 20
hoxit signals dragon-tiger 002475 --trade-date 2026-05-12
hoxit signals lockup 002475 --trade-date 2026-05-12 --forward-days 90
hoxit signals industry --top-n 20
hoxit signals daily-dragon-tiger --trade-date 2026-05-12
hoxit valuation full 688017
```

## Python API

需要在脚本或 notebook 中复用时，直接导入 `/Users/mac/Projects/hoxit` 中的 `hoxit` 包：

```python
from hoxit.market import mootdx_quote, tencent_metrics
from hoxit.valuation import full_valuation
from hoxit.signals import lockup_expiry, baidu_concept_blocks

quotes = mootdx_quote(["688017"])
metrics = tencent_metrics(["688017"])
valuation = full_valuation("688017")
lockup = lockup_expiry("002475", "2026-05-12", forward_days=90)
```

## 能力索引

### 行情层

- `hoxit market quote <codes...>`：mootdx 实时行情，腾讯仅作 fallback；默认 CSV，`--format json` 输出 JSON
- `hoxit market bars <code>`：mootdx K线
- `hoxit market transactions <code>`：mootdx 逐笔成交
- `hoxit market metrics <codes...>`：腾讯 PE/PB/市值/换手率/涨跌停
- Python: `hoxit.market.mootdx_quote`, `mootdx_bars`, `mootdx_transactions`, `tencent_metrics`
- 数据源：mootdx 优先，腾讯财经仅补充估值字段或 fallback。

### 研报层

- `hoxit reports eastmoney <code>`
- `hoxit reports iwencai <query>`
- Python: `hoxit.reports.eastmoney_reports`, `iwencai_search`, `download_pdf`, `dedup_articles`
- 数据源：东财 reportapi、东财 PDF、iwencai OpenAPI。

### 信号层

- `hoxit signals hot`
- `hoxit signals hot --exclude-st`：过滤 ST/*ST 股票
- `hoxit signals northbound`
- `hoxit signals concept <code>`
- `hoxit signals fund-flow <code>`
- `hoxit signals dragon-tiger <code>`
- `hoxit signals lockup <code>`
- `hoxit signals industry`
- `hoxit signals daily-dragon-tiger`
- Python: `hoxit.signals`
- 数据源：同花顺、百度股市通、akshare、东财 datacenter。

### 新闻层

- `hoxit news stock <code>`
- `hoxit news cls`
- `hoxit news global`
- Python: `hoxit.news`
- 数据源：akshare。

### 基础数据层

- `hoxit fundamentals info <code>`
- `hoxit fundamentals finance <code>`
- `hoxit fundamentals f10 <code>`
- Python: `hoxit.fundamentals`
- 数据源：akshare、mootdx。

### 公告层

- `hoxit filings cninfo <code> --start-date YYYYMMDD --end-date YYYYMMDD`
- Python: `hoxit.filings.cninfo_reports`
- 数据源：巨潮 cninfo。

### 估值流程

- `hoxit valuation full <code>`
- Python: `hoxit.valuation.full_valuation`
- 能力：实时价、一致预期 EPS、前向 PE、PEG、PE 消化年数。

## TDD 验收

每次修改后运行：

```bash
.venv/bin/python -m pytest
```

默认测试只覆盖确定性逻辑、解析逻辑、CLI 路由和兼容别名，不访问真实网络。

## 注意事项

- 腾讯 API 使用 GBK 编码；PB 字段是索引 46，索引 43 是振幅。
- iwencai 语义搜索需要 `IWENCAI_API_KEY`，并携带 X-Claw Headers。
- 调用 iwencai 前执行 `set -a; source .env.local; set +a`。
- 百度 PAE `ResultCode` 可能是 int `0` 或 string `"0"`，脚本已统一处理。
- 北向历史采用本地自缓存，首次运行只有本地已采集数据。
- `lockup_expiry()` 已按 `trade_date` 到 `trade_date + forward_days` 的窗口逐日查询，不再只查单日。
- 无机构覆盖时，`full_valuation()` 返回 quote 数据并将 EPS/PEG 字段置空，不抛出空 DataFrame 异常。

## 文件入口

- 设计文档：`docs/IMPLEMENTATION_DESIGN.md`
- Python 包：`/Users/mac/Projects/hoxit/hoxit/`
- 测试：`tests/`
- 命令入口：`hoxit`

## Disclaimer

本项目仅提供数据获取工具，不构成任何投资建议。股市有风险，投资需谨慎。
