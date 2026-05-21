# hoxit

将 A 股数据接口按业务场景拆分为 market / reports / news / fundamentals / filings / signals / valuation 七层，每层提供独立的 Python 函数和 CLI 子命令。核心思路是所有网络调用可注入（方便测试）、第三方库延迟导入（零安装即可跑通全部单元测试）、统一返回 dict/list[dict] 格式便于脚本化处理。

## 快速开始

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"

# 运行测试（默认不联网）
.venv/bin/python -m pytest

# 真实数据接口需要额外安装
.venv/bin/python -m pip install -e ".[data]"
```

## 主命令

需要密钥的接口先执行：

```bash
set -a; source .env.local; set +a
```

```bash
# 行情层
.venv/bin/hoxit market quote 688017 300476
.venv/bin/hoxit market quote 688017 --format json
.venv/bin/hoxit market metrics 688017 300476
.venv/bin/hoxit market bars 688017 --category 4 --offset 10
.venv/bin/hoxit market transactions 688017 --date 20260512

# 研报层
.venv/bin/hoxit reports eastmoney 688017 --max-pages 2
.venv/bin/hoxit reports iwencai "人形机器人" --channel report --size 50

# 新闻层
.venv/bin/hoxit news stock 600519
.venv/bin/hoxit news cls
.venv/bin/hoxit news global

# 基本面层
.venv/bin/hoxit fundamentals info 688017
.venv/bin/hoxit fundamentals finance 688017
.venv/bin/hoxit fundamentals f10 688017

# 公告层
.venv/bin/hoxit filings cninfo 600519 --start-date 20260101 --end-date 20260521

# 信号层
.venv/bin/hoxit signals hot --exclude-st
.venv/bin/hoxit signals northbound
.venv/bin/hoxit signals concept 688017
.venv/bin/hoxit signals fund-flow 600519 --days 20
.venv/bin/hoxit signals dragon-tiger 002475 --trade-date 2026-05-12
.venv/bin/hoxit signals lockup 688017 --trade-date 2026-05-21 --forward-days 90
.venv/bin/hoxit signals industry --top-n 20
.venv/bin/hoxit signals daily-dragon-tiger --trade-date 2026-05-21

# 估值层
.venv/bin/hoxit valuation full 688017
```

## Python API

```python
from hoxit.market import mootdx_quote, tencent_metrics
from hoxit.valuation import full_valuation
from hoxit.signals import lockup_expiry
from hoxit.iwencai import query2data, comprehensive_search
```

## 项目结构

| Path | 说明 |
|---|---|
| `hoxit/` | 主体 Python 包（七层 + utils + iwencai 适配器） |
| `tests/` | 测试框架，默认不访问真实网络 |
| `tests/test_live_endpoints.py` | 真实服务可用性测试（`HOXIT_LIVE_TESTS=1`） |
| `docs/IMPLEMENTATION_DESIGN.md` | 需求、设计和实现说明 |
| `docs/INTERFACES.md` | 每个接口的具体调用指令 |
| `docs/SKILL_GAP_ANALYSIS.md` | 原 Skill 对照当前实现的遗漏清单 |
| `docs/IWENCAI_FALLBACK_ANALYSIS.md` | iwencai 作为各层 fallback 的评估 |
| `docs/DEVLOG.md` | 开发日志 |
| `CLAUDE.md` | Claude Code 项目指引 |
| `TODO.md` | 后续接口补齐、输出格式和工作流任务 |
| `SKILLS.md` | 本地 Skill 简化说明和命令/API 索引 |
| `Reference/a-stock-data/` | 原始 Skill 参考来源 |
