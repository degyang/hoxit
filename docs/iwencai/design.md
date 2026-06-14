---
date: 2026-05-19
type: design
tags:
  - pos
  - system-skill
  - iwencai
  - skillhub
ai-first: true
---

## For future Claude

本文档记录本地 iWencai SkillHub 能力合并为一个运行时 skill：`trading-iwencai` 的设计。

## 问题

现有 iWencai skill 集合分散在多个目录：

- 17 个 `hithink-*` skills，每个都有几乎相同的 `scripts/cli.py`。
- `announcement-search` 和 `report-search` 使用另一组搜索 API。
- `TOS/90-Inbox/问财SkillHub.md` 是人工整理的能力索引。

这些重复脚本的主要差异只是 `SKILL_NAME`、帮助文案和 route 语义。继续分散维护会导致修复、安全清理、gateway header 变更和 CLI 行为逐渐漂移。

## 决策

在 POS System 下建立统一 skill：

```text
00-System/Skills/skills-trading-iwencai/
  trading-iwencai/
    SKILL.md
    scripts/
      cli.py
      iwencai_all.py
      routes.json
    references/
      design.md
      query2data.md
      comprehensive-search.md
      routing.md
      original-docs/
```

统一 skill 只保留一个 CLI，并拆成两个 adapter family：

- `Query2DataClient`：覆盖所有 `hithink-*` route。
- `ComprehensiveSearchClient`：覆盖 `announcement-search` 和 `report-search`。

## 不可妥协的 Gateway 规则

不要把所有 gateway 调用都改成 `X-Claw-Skill-Id: trading-iwencai`。

本地 skill 可以统一，但每次请求必须保留原始子能力 id：

- `hithink-market-query`
- `hithink-astock-selector`
- `announcement-search`
- `report-search`
- 等等

原因：上游 gateway 可能使用 `X-Claw-Skill-Id` 做授权、审计、限流、统计或产品侧行为分流。

## 接口族

### query2data

所有 `hithink-*` route 使用这一类接口。

- Endpoint: `POST https://openapi.iwencai.com/v1/query2data`
- Payload:
  - `query`
  - `page`
  - `limit`
  - `is_cache`
  - `expand_index`
- 常见响应字段：
  - `datas`
  - `code_count`
  - `chunks_info`

### comprehensive_search

公告搜索和研报搜索使用这一类接口。

- Endpoint: `POST https://openapi.iwencai.com/v1/comprehensive/search`
- Payload:
  - `channels`
  - `app_id`
  - `query`
- 常见响应字段：
  - `data`

对 `report-search`，原始文档明确要求透明传递 API 响应，因此代码层只做最小必要转换。

## CLI 形态

推荐命令：

```bash
python3 scripts/cli.py routes
python3 scripts/cli.py query --route market -q "贵州茅台最新价"
python3 scripts/cli.py query --route astock -q "今日涨幅超过5%的A股" --limit 20
python3 scripts/cli.py search --route announcement -q "贵州茅台 分红公告"
python3 scripts/cli.py search --route report -q "机器人行业研究报告"
```

`query` 只接受 `query2data` route；`search` 只接受 `comprehensive_search` route。这样可以让协议误用尽早暴露。

## 迁移方案

1. 创建 `trading-iwencai`，建立统一 route table 和 CLI。
2. 做 smoke test：route 列表、参数校验、缺少 API key、Python 语法。
3. 在存在有效 `IWENCAI_API_KEY` 时验证真实调用。
4. 将旧 `hithink-*` CLI 改成调用统一 CLI 的 compatibility wrapper。
5. 在确认透明传递要求后，再迁移 `announcement-search` 和 `report-search` 的旧 CLI。
6. 旧 skill 目录先保留一段时间作为 redirect，避免破坏既有引用。

## 安全说明

历史文档可能包含 API key 配置示例。此 skill 不应保存真实 key；示例只能使用 `your-api-key` 或 `$IWENCAI_API_KEY`。
