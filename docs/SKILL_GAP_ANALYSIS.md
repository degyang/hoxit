# Reference/a-stock-data Skill 对照实现差距

对照对象：`Reference/a-stock-data/SKILL.md`

当前主体工程：`/Users/mac/Projects/hoxit`

## 已实现

### 行情层

- `mootdx` 实时行情：`hoxit market quote <codes...>`
- `mootdx` K 线：`hoxit market bars <code> --category 4 --offset 10`
- `mootdx` 逐笔成交：`hoxit market transactions <code> --date YYYYMMDD`
- 腾讯估值指标：`hoxit market metrics <codes...>`
- 代码归一化、市场前缀、腾讯 GBK 字段解析。

说明：`market quote` 默认输出 CSV；如需 JSON，使用 `--format json`。

### 研报层

- 东财研报列表：`hoxit reports eastmoney <code>`
- iwencai 语义搜索：`hoxit reports iwencai <query>`
- Python API 已有 `download_pdf`、`dedup_articles`。

### 新闻层

- 个股新闻：`hoxit news stock <code>`
- 财联社快讯：`hoxit news cls`
- 东财全球资讯：`hoxit news global`

### 基础数据层

- akshare 个股基本面：`hoxit fundamentals info <code>`
- mootdx 财务快照：`hoxit fundamentals finance <code>`
- mootdx F10：`hoxit fundamentals f10 <code>`

### 公告层

- 巨潮公告：`hoxit filings cninfo <code> --start-date YYYYMMDD --end-date YYYYMMDD`

### 信号层

- 同花顺热点：`hoxit signals hot`
- 同花顺北向实时：`hoxit signals northbound`
- 百度概念板块：`hoxit signals concept <code>`
- 百度资金流向历史：`hoxit signals fund-flow <code>`
- 龙虎榜基础记录：`hoxit signals dragon-tiger <code>`
- 限售解禁未来窗口：`hoxit signals lockup <code>`
- 行业对比：`hoxit signals industry`
- 全市场龙虎榜：`hoxit signals daily-dragon-tiger`

### 估值流程

- 单票估值：`hoxit valuation full <code>`
- 前向 PE、PEG、PE 消化时间。

## 遗漏或未完全等效

### 高优先级

1. `iwencai_query`

   原 Skill 提供 `/v1/query2data` 结构化字段查询；当前只实现了 `/v1/comprehensive/search` 语义搜索。

2. 东财 PDF 下载命令

   Python API 有 `download_pdf()`，但 CLI 没有 `hoxit reports download-pdf`。

3. 百度资金流向分钟级命令

   Python API 有 `baidu_fund_flow_realtime()`，但 CLI 只有历史 `fund-flow`。

4. 北向历史读取命令

   Python API 有 `load_northbound_history()`，但 CLI 没有 `hoxit signals northbound-history`。

5. 龙虎榜席位明细和机构统计

   原 Skill 聚合 `stock_lhb_stock_detail_em` 买入/卖出席位和 `stock_lhb_jgmmtj_em` 机构统计；当前 `dragon_tiger_board()` 只返回上榜记录，`seats` 和 `institution` 仍是空结构。

### 中优先级

1. 一致预期 EPS 独立命令

   `valuation full` 内部使用 `stock_profit_forecast_ths`，但没有单独的 `reports forecast` 或 `valuation forecast` 命令。

2. F10 分类读取与截断策略

   当前 `fundamentals f10` 只做轻封装，未按原 Skill 中 9 类资料和“股东研究截断”策略做结构化输出。

3. F10 公告摘要

   原 Skill 有 `最新提示` 公告摘要示例；当前没有单独 CLI。

4. 组合流程

   原 Skill 的批量估值、主题研报批量检索、新标的快速调研还没有变成 CLI workflow。

5. 同花顺热点字段中文重命名

   当前返回原始数据，未完全复刻原 Skill 的中文字段映射。

### 低优先级

1. `stockstats` 技术指标

   依赖已保留，但尚未提供 RSI/MACD/BOLL 等命令。

2. CLI 输出格式统一

   目前只有 `market quote` 默认 CSV，其他命令仍默认 JSON；后续可以给所有表格类命令增加 `--format csv|json`。

3. 真实接口冒烟测试

   默认 TDD 不访问网络；可以增加手动 `tests_live/` 或 `hoxit doctor` 检查真实依赖和网络连通性。

## 建议下一步

1. 补齐高优先级遗漏：`iwencai_query`、PDF 下载命令、资金流分钟级、北向历史、龙虎榜席位明细。
2. 给所有表格型命令统一 `--format csv|json`。
3. 增加 `hoxit doctor`，检查 `mootdx`、`akshare`、`requests`、网络连通性和必要环境变量。
4. 将组合流程实现为 `hoxit workflow valuation-batch`、`hoxit workflow thematic-reports`、`hoxit workflow quick-research`。
