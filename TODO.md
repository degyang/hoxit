# TODO

## 高优先级

- [ ] 实现 `iwencai_query` 结构化查询接口。
  - 原 Skill 对应：`POST /v1/query2data`
  - 当前已有：`hoxit reports iwencai` 语义搜索，即 `/v1/comprehensive/search`
  - 目标命令建议：`.venv/bin/hoxit reports iwencai-query "贵州茅台 ROE"`

- [ ] 给东财 PDF 下载增加 CLI。
  - 当前已有 Python API：`hoxit.reports.download_pdf`
  - 目标命令建议：`.venv/bin/hoxit reports download-pdf <info-code-or-record-json> --target-dir reports`

- [ ] 给百度资金流向分钟级增加 CLI。
  - 当前已有 Python API：`hoxit.signals.baidu_fund_flow_realtime`
  - 目标命令建议：`.venv/bin/hoxit signals fund-flow-realtime 000858 --date 20260512`

- [ ] 给北向资金历史缓存增加读取命令。
  - 当前已有 Python API：`hoxit.signals.load_northbound_history`
  - 目标命令建议：`.venv/bin/hoxit signals northbound-history --days 20 --cache-dir .cache`

- [ ] 完整实现龙虎榜席位明细和机构统计。
  - 当前 `dragon_tiger_board()` 只返回基础上榜记录。
  - 需要补齐 `stock_lhb_stock_detail_em` 买入/卖出席位 TOP5。
  - 需要补齐 `stock_lhb_jgmmtj_em` 机构买卖统计。

- [ ] 优化 `fundamentals finance` 输出格式。
  - 当前 CLI 会把 DataFrame 字符串化，字段被省略。
  - 目标：支持 `--format csv|json`，默认可考虑 CSV。
  - 同时补充字段中文释义或 `--explain`。

## 中优先级

- [ ] 给一致预期 EPS 增加独立命令。
  - 当前只在 `hoxit valuation full` 内部使用 `ak.stock_profit_forecast_ths`。
  - 目标命令建议：`.venv/bin/hoxit valuation forecast 688017`

- [ ] 结构化 `mootdx F10` 公司资料。
  - 原 Skill 提到 9 大类文本。
  - 需要支持分类参数，例如 `--section 股东研究`、`--section 最新提示`。
  - 需要实现股东研究截断策略。

- [ ] 增加 F10 最新提示/公告摘要命令。
  - 目标命令建议：`.venv/bin/hoxit fundamentals f10-latest 688017`

- [ ] 同花顺热点字段中文映射。
  - 当前 `hoxit signals hot` 返回原始字段。
  - 原 Skill 中有 `代码`、`名称`、`题材归因`、`涨幅%` 等中文友好字段。

- [ ] 给所有表格型接口统一 `--format csv|json`。
  - 当前只有 `market quote` 默认 CSV 并支持 `--format json`。
  - 候选：`market bars`、`market metrics`、`signals hot`、`news global`、`fundamentals finance`。

## 工作流

- [ ] 批量估值对比。
  - 目标命令建议：`.venv/bin/hoxit workflow valuation-batch 688017 300476 002463`

- [ ] 主题研报批量检索。
  - 目标命令建议：`.venv/bin/hoxit workflow thematic-reports "人形机器人 丝杠"`

- [ ] 新标的快速调研。
  - 目标命令建议：`.venv/bin/hoxit workflow quick-research 688017`

## 质量与运维

- [ ] 增加 `hoxit doctor`。
  - 检查虚拟环境依赖：`mootdx`、`akshare`、`requests`、`pandas`。
  - 检查 `IWENCAI_API_KEY`。
  - 检查 `.env.local` 是否已导出到子进程环境。
  - 检查 mootdx TCP 行情源连通性。
  - 检查腾讯、同花顺、百度 PAE 基础 HTTP 连通性。

- [ ] 增加可选真实接口冒烟测试。
  - 默认 `pytest` 继续只用 fake 数据，不访问网络。
  - 真实测试可单独放到 `tests_live/` 或通过环境变量启用。
