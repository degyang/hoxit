# hoxit 脚本化实现设计

## 目标

将 `Reference/a-stock-data/SKILL.md` 中分散的内嵌 Python 片段沉淀为可导入、可测试、可复用的 Python 模块，保留原 Skill 的六层数据能力，并在本地 `SKILLS.md` 中维护简化后的激活规则、能力索引和脚本调用说明。

本次改造重点不是引入复杂框架，而是把关键逻辑从 Markdown 中移出，形成稳定执行面：

- 行情层：mootdx 实时行情/K线/逐笔成交优先，腾讯财经仅作为行情 fallback 和估值指标补充。
- 研报层：东财研报列表、PDF 下载、iwencai 搜索辅助、去重逻辑。
- 新闻层：akshare 新闻/快讯/资讯的轻封装。
- 基础数据层：mootdx 财务/F10 和 akshare 个股基本面的轻封装。
- 公告层：巨潮公告查询和市场映射。
- 信号层：同花顺热点、北向资金自缓存、百度股市通、龙虎榜、解禁、行业对比。
- 估值流程：单票估值、PE/PEG/消化时间等确定性计算。

## 目录结构

```text
hoxit/
  __init__.py
  cli.py
  utils.py
  market.py
  reports.py
  news.py
  fundamentals.py
  filings.py
  signals.py
  valuation.py
tests/
  conftest.py
  test_utils.py
  test_market.py
  test_reports.py
  test_signals.py
  test_valuation.py
pyproject.toml
```

## 命令接口

项目提供统一主命令 `hoxit`，每个数据层对应一个一级子命令：

```bash
hoxit market quote 688017 300476
hoxit market quote 688017 --format json
hoxit market metrics 688017 300476
hoxit market bars 688017 --category 4 --offset 10
hoxit market transactions 688017 --date 20260512
hoxit reports eastmoney 688017 --max-pages 2
hoxit news stock 688017
hoxit fundamentals info 688017
hoxit filings cninfo 688017 --start-date 20260101 --end-date 20260516
hoxit signals hot --date 2026-05-12
hoxit valuation full 688017
```

子命令按“层面 -> 动作”的方式组织。默认输出以 JSON 为主；`market quote` 面向表格查看，默认 CSV，并可通过 `--format json` 切回 JSON。

## 虚拟环境要求

程序必须在项目虚拟环境中运行。推荐流程：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/hoxit market quote 688017
```

默认测试不访问真实网络，也不要求安装 `akshare`、`mootdx` 等行情依赖；真实数据命令需要按需安装 optional 依赖。

## 设计原则

1. 网络 I/O 可注入

   直接请求外部数据源的函数支持注入 `http_get`、`http_post` 或 `urlopen`，测试中用假响应替代真实网络，避免 TDD 依赖行情服务可用性。

2. 第三方依赖延迟导入

   `akshare`、`mootdx`、`pandas`、`requests` 都放在函数内部或可注入边界内导入。基础测试只依赖标准库和 `pytest`，本地没有行情依赖时也能验证核心逻辑。

3. 返回结构稳定

   脚本函数返回 `dict` / `list[dict]` 等稳定结构。需要 DataFrame 的上游接口只在边界内出现，模块内部尽量转为普通 Python 数据结构。

4. 修复已发现问题

   - `lockup_expiry()` 必须真的覆盖 `trade_date` 到 `trade_date + forward_days` 的窗口。
   - `full_valuation()` 必须容忍无机构覆盖或空 DataFrame。
   - CHANGELOG/README/SKILL 中的函数名要和真实函数一致。
   - 端点数量统一为 21。

5. 命名兼容

   保留原文中已出现的函数名，同时提供 changelog 曾宣传的 `get_*` 兼容别名，降低用户迁移成本。

## TDD 策略

测试按风险优先级覆盖：

- 纯函数测试：代码归一化、市场前缀、PE/PEG/消化时间。
- 解析测试：腾讯 GBK `~` 字段解析、东财 PDF 文件名清洗、百度 PAE 字段解析。
- 行为测试：无机构覆盖时估值不崩溃、解禁窗口会遍历未来日期、北向缓存会按日期覆盖写入。
- 兼容测试：`get_*` 别名存在且指向等效实现。

每次变更的最小验收命令：

```bash
.venv/bin/python -m pytest
```

可选的真实接口冒烟测试不放入默认测试，避免 CI 或本地网络导致误报。

## SKILLS.md 简化方案

本地 `SKILLS.md` 不承载大段可执行代码，而是保留：

- 元数据、激活条件、依赖安装。
- 六层能力索引。
- 常用调用示例，指向 `hoxit` 模块函数。
- 数据源注意事项和 FAQ。

这样 Skill 仍能指导 AI 助手选择正确能力，但实际执行由脚本保证，避免复制片段时发生命名漂移、逻辑遗漏或日期窗口错误。

## 实现顺序

1. 新增 `pyproject.toml` 和 `hoxit` 包。
2. 先实现工具层、行情层和估值层，建立基础测试。
3. 实现研报、信号、公告等外部接口封装，测试解析和错误路径。
4. 将本地 `SKILLS.md` 整理为脚本调用指南，不修改外部映射目录 `Reference/a-stock-data`。
5. 运行 `pytest`，确认默认测试不依赖真实网络和未安装第三方行情包。
