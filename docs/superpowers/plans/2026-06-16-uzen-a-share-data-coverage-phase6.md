# UZEN A股数据覆盖 Phase 6 Plan

> **For agentic workers:** 每个 PR 只能由 Claude Code 执行一个 ticket。完成实现、测试、implementation report、commit、push 后必须停止等待 Codex review。

## Goal

补齐 UZEN 与 `Reference/UZI-Skill` 在 A股研究数据覆盖上的关键差距，让 UZEN 能在现有 research spine 中表达更多 A股事实、缺口和 unsupported 边界。

Phase 6 先做数据底座，不做视觉报告、完整 persona、跨市场或社交证据结论。

## Architecture

保持现有主流程：

```text
collect_snapshot()
  -> analyze_snapshot()
  -> render_markdown()
  -> run_analysis()
```

Phase 6 只做 additive changes：

- 在 hoxit 现有模块中新增可复用 A股接口。
- 在 `UzenDataProvider` 和 `collect_snapshot()` 中接入新 source。
- 在 `analysis["dimensions"]`、`analysis["synthesis"]`、Markdown 中消费新增 source。
- 保持旧 JSON keys、CLI 命令和默认输出文件名兼容。

## Non-Goals

- 不导入 UZI provider chain/runtime。
- 不新增 HTML/PNG/Playwright artifact。
- 不新增非 A股支持。
- 不实现完整 65/66 investor persona。
- 不做 LHB 席位身份分类或历史席位数据库。
- 不声称 social trap evidence 已实现。

## PR Sequence

| PR | Title | Purpose |
| --- | --- | --- |
| PR-DATA-001 | hoxit A股治理与事件接口 | 新增 management/event/business 轻量 hoxit 接口，遵守 CLI/API 规范。 |
| PR-DATA-002 | UZEN Snapshot Data Coverage | 把新增接口接入 `UzenDataProvider` 和 snapshot/data_quality。 |
| PR-DATA-003 | UZEN Coverage Dimensions | 扩展 dimensions，表达 governance、business、events、policy 等覆盖状态。 |
| PR-DATA-004 | UZEN Data-Aware Synthesis And Markdown | 让 synthesis/Markdown 消费新增事实摘要，仍保持非编造。 |
| PR-DATA-005 | Phase 6 Docs And Live Test Sync | 同步 docs、skills、API_DEVLOG/live tests，明确 current/deferred 边界。 |

## Verification Baseline

默认每个 PR 至少运行：

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit tests docs uzen-skills
```

涉及 CLI 或新增 hoxit module API 的 PR 还要运行：

```bash
.venv/bin/python -m pytest tests/test_cli.py tests/test_signals.py tests/test_fundamentals.py tests/test_reports.py tests/test_news.py -v
```

涉及外部接口的 PR 可新增/更新集成测试，但必须默认 skip：

```bash
HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -v
```

## Rollback

每个 PR 都必须可单独 revert。新增 source 在 UZEN 中必须有 neutral default，避免接口不可用时破坏现有模式。
