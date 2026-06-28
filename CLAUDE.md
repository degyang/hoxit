# CLAUDE.md

本文件指导 Claude Code（claude.ai/code）在此仓库中工作。

## 双 Agent 启动规则

本仓库已安装 Codex + Claude Code 双 Agent workflow。

Claude Code 在本仓库中默认是 executor：implementer、tester、fixer。会话开始后，如果用户说“你现在是 CC / Claude Code / executor / 执行者”，或要求执行某个 `docs/superpowers/prs/PR-XXX-<slug>.md`，必须先使用 `$pos-magents` 确认当前阶段，然后进入 `cc-implementer` 或 `cc-tester`。

如果用户没有提供明确 PR ticket，不要自行决定架构或开始实现；应要求 Codex master 先用 `codex-pm`、`codex-architect`、`codex-pr-planner` 创建 design 和 PR ticket。

### 双 Agent 硬门禁

- Claude Code 一次只能处理一个明确指定的 PR ticket。
- 开始前必须检查 `docs/superpowers/status/board.md`：当前 PR 的所有依赖必须是 `APPROVED` 或 `MERGED`。
- 当前 PR 完成实现、测试、提交和 implementation report 后，必须停止并等待 Codex review。
- Claude Code 只能把当前 PR 推进到 `REVIEW_READY`；只有 Codex 可以写入 `APPROVED`、`CHANGES_REQUESTED` 或 `REJECTED`。
- 未获得 Codex 明确指令，不得读取、实现、提交或更新后续 PR。
- 如果发现自己已经越过 review gate，必须停止后续工作，回到当前 Codex 指定的 PR 或 review 修复项。

## 先检查接口同步状态

处理外部数据接口相关任务时，先查看：

- `docs/API_DEVLOG.md`：接口健壮性跟踪日志，记录 `Reference/a-stock-data` 同步状态、已知失效接口、修复和验证结果。
- `Reference/a-stock-data/CHANGELOG.md`：上游参考项目最新接口变更。
- `docs/INTERFACES.md`：hoxit 当前 CLI/API 调用说明。

如果任务涉及东财、巨潮、同花顺、iwencai、腾讯、mootdx、百度等数据源，先对照 `Reference/a-stock-data` 最新标签确认 hoxit 是否已经同步。完成修复或确认后，把来源版本、影响接口、hoxit 变更、验证命令和后续关注项追加到 `docs/API_DEVLOG.md`。

## 接口变更后同步关联 Skills

`skills/` 目录下软链接了 4 个 POS 侧 skill（外层包装目录，含 `CLAUDE.md`、`SETUP.md`、`commands/` 和内层 `SKILL.md`）：

| 链接 | 目标 |
|---|---|
| `skills/skills-tos-hoxit` | `../../POS/00-System/Skills/skills-tos-hoxit` |
| `skills/skills-tos-periodic-review` | `../../POS/00-System/Skills/skills-tos-periodic-review` |
| `skills/skills-tos-kanpan` | `../../POS/00-System/Skills/skills-tos-kanpan` |
| `skills/skills-tos-iwencai` | `../../POS/00-System/Skills/skills-tos-iwencai` |

**每当 hoxit 接口发生以下变更时，必须检查并同步更新这 4 个 skill：**

- CLI 子命令、参数名、默认值或选项变更（如 `--category` → `--frequency`）
- Python API 函数签名、参数名、返回值结构变更
- 数据源端点 URL、参数格式、鉴权方式变更
- 新增或移除端点/数据层
- 环境变量或配置路径变更

**同步检查清单：**

1. `grep` 旧参数名/函数名/URL 在 `skills/` 下是否仍有残留引用。
2. 更新 skill 内的 CLI 示例、参数表、频率值表、Python API 示例。
3. 更新 `references/` 下的命令参考、工作流、背景说明文件。
4. 如果变更影响上游使用方的调用方式，在 `docs/API_DEVLOG.md` 中记录 skill 同步情况。

## 常用命令

```bash
# 安装（开发模式）
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"

# 安装可选数据依赖（mootdx, pandas, requests, stockstats）
.venv/bin/python -m pip install -e ".[data]"

# 运行全部单元测试（不联网）
.venv/bin/python -m pytest

# 详细输出
.venv/bin/python -m pytest -v

# 运行单个测试文件
.venv/bin/python -m pytest tests/test_market.py

# 运行单个测试用例
.venv/bin/python -m pytest tests/test_signals.py::test_ths_hot_reason

# 运行集成测试（需要网络 + data 依赖）
HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -v

# 查看 CLI 帮助
.venv/bin/hoxit --help
```

## 架构

A 股数据工具，按业务领域拆分为七层。每层是一个独立的扁平模块，CLI（`cli.py`）通过 argparse 按需延迟导入对应函数。

### 七层结构

| 层 | 模块 | 功能 |
|---|---|---|
| 行情 | `market.py` | 实时行情、K 线、逐笔成交 |
| 研报 | `reports.py` | 东财研报列表、iwencai 语义搜索 |
| 新闻 | `news.py` | 个股新闻、快讯、全球资讯 |
| 基本面 | `fundamentals.py` | 个股信息、财务快照、F10 |
| 公告 | `filings.py` | 巨潮公告 |
| 信号 | `signals.py` | 热点、北向资金、概念板块、资金流、龙虎榜、解禁、行业对比 |
| 估值 | `valuation.py` | 完整估值、远期 PE、PEG |

辅助模块：
- `utils.py` — 代码规整、日期迭代等工具函数，零依赖
- `iwencai.py` — iwencai API 适配器，被 reports/fundamentals/filings 各层复用
- `cli.py` — argparse 入口，按需导入各层

### 核心设计原则

1. **网络 IO 可注入** — 函数接收 `http_get`/`http_post`/`urlopen` 参数，测试时无需真实网络。
2. **第三方库延迟导入** — `requests`、`pandas`、`mootdx`、`stockstats` 在函数体内导入，非模块顶层。仅需 stdlib + pytest 即可跑通全部单元测试。
3. **统一返回类型** — 函数返回 `dict` 或 `list[dict]`，pandas DataFrame 止于边界。
4. **向后兼容** — 旧函数名保留为别名（如 `tencent_quote = tencent_metrics`）。

### 测试模式

默认测试套件不依赖任何网络或第三方数据。HTTP 相关函数接收注入的可调用对象。`conftest.py` 提供：
- `JsonResponse` / `TextResponse` — mock HTTP 响应包装器
- `FakeDataFrame` / `FakeSeries` — 无需 pandas 的 DataFrame 替代品
- `FakeMootdxClient` — mootdx TCP 客户端 mock

集成测试位于 `test_live_endpoints.py`，通过 `HOXIT_LIVE_TESTS=1` 环境变量启用，标记为 `@pytest.mark.integration`。

### 数据来源

- **mootdx** — TCP 行情客户端（实时行情、K 线、逐笔成交）
- **腾讯** — PE/PB/市值等 HTTP API
- **东财** — 研报、新闻、资金流、龙虎榜
- **巨潮** — 监管公告
- **iwencai** — 语义搜索（各层的 fallback/适配器）
- **百度** — 概念板块、资金流历史
- **同花顺** — 热点原因、EPS 预测

### 环境变量

- API 密钥存放于 `.env.local`（使用前加载：`set -a; source .env.local; set +a`）
- iwencai 接口需要 `IWENCAI_BASE_URL` 和 `IWENCAI_API_KEY`
