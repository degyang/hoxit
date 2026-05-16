# hoxit

A 股数据工具的脚本化主体工程，基于 `Reference/a-stock-data/SKILL.md` 的六层能力设计实现。

## 虚拟环境

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

真实数据接口需要额外安装：

```bash
.venv/bin/python -m pip install -e ".[data]"
```

## 主命令

```bash
.venv/bin/hoxit market quote 688017 300476
.venv/bin/hoxit market quote 688017 --format json
.venv/bin/hoxit market metrics 688017 300476
.venv/bin/hoxit market bars 688017 --category 4 --offset 10
.venv/bin/hoxit market transactions 688017 --date 20260512
.venv/bin/hoxit reports eastmoney 688017 --max-pages 2
.venv/bin/hoxit signals concept 688017
.venv/bin/hoxit valuation full 688017
```

## Python API

```python
from hoxit.market import mootdx_quote, tencent_metrics
from hoxit.valuation import full_valuation
from hoxit.signals import lockup_expiry
```

## 目录

- `hoxit/`: 主体 Python 包。
- `tests/`: TDD 测试框架，默认不访问真实网络。
- `docs/IMPLEMENTATION_DESIGN.md`: 需求、设计和实现说明。
- `docs/INTERFACES.md`: 每个接口的具体调用指令。
- `docs/SKILL_GAP_ANALYSIS.md`: 原 Skill 对照当前实现的遗漏清单。
- `TODO.md`: 后续接口补齐、输出格式和工作流任务。
- `SKILLS.md`: 本地 Skill 简化说明和命令/API 索引。
- `Reference/a-stock-data/`: 原始 Skill 参考来源。
