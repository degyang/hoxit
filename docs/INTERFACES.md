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

### 东财全球资讯

```bash
.venv/bin/hoxit news global
```

## 基础数据层

### akshare 个股基本面

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

### 百度资金流向历史

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
