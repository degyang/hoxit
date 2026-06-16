# UZEN Phase 7 Live Provider Contract Hardening Plan

## Goal

让 UZEN 报告从“mock provider 能跑”升级到“真实 hoxit provider 输出可稳定支撑报告关键字段”。优先目标股票是宁波银行 `002142`，报告方向优先，不做可视化。

## Non-Goals

- 不做 HTML/PNG/Playwright。
- 不新增 UZEN 内部 one-off scraper。
- 暂不考虑 akshare 作为 Phase 7 fallback。
- Web/Playwright fallback 仅在 hoxit 多源评估后仍不合格时考虑，且必须沉淀为 hoxit reusable helper；需要登录/Cookie/页面确认时向用户提出协助请求。
- 不声明完整 UZI parity。
- 不做 persona parity、社交操纵证据、LHB 席位身份推断。

## Milestones

### M1 Provider Boundary

建立 UZEN normalization 层，让 quote、finance、concept、dragon_tiger、fund_flow 等常见 live shape 被统一成报告层稳定结构。

### M2 Derived Market Metrics

从 hoxit quote/bars 衍生基础行情指标，解决涨跌幅、区间收益、均线、波动率等字段缺口。

### M3 Finance Normalization

将 finance DataFrame/dict 映射到报告可用字段，优先解决 ROE、净利润、营收、总股本等字段缺口。同时建立字段级数据源质量评估：如果当前 hoxit source 不合格，应评估 hoxit 已有替代源或新增 hoxit reusable helper。

如需网页数据（例如同花顺 F10、东财 F10、交易所页面等），先由 PR 明确列出字段和页面，再决定是否引入 Playwright fallback。Phase 7 不使用 akshare 兜底。

### M4 Bank Report Quality

针对银行股增加确定性财务/估值质量规则，不强行套普通 FCFF DCF；宁波银行报告需要明确展示银行相关关键指标或 data_needed 原因。

### M5 Live Smoke Gate

增加可选 live smoke 测试与文档同步，固定宁波银行 `002142` 为验收样例。

## PR Queue

| PR | Title | Dependency | Purpose |
|---|---|---|---|
| PR-LIVE-001 | UZEN Provider Normalization Boundary | main | 统一 live provider shape |
| PR-LIVE-002 | UZEN Derived Market Metrics | PR-LIVE-001 | 补行情衍生指标 |
| PR-LIVE-003 | hoxit/UZEN Finance Field Normalization And Source Quality | PR-LIVE-002 | 补财务字段归一化与字段级 fallback |
| PR-LIVE-004 | Bank Report Quality For Ningbo Bank | PR-LIVE-003 | 银行股报告质量 |
| PR-LIVE-005 | Live Smoke Gate And Docs Sync | PR-LIVE-004 | live gate 与文档 |
| PR-LIVE-006 | hoxit Playwright Fallback Provider Foundation | PR-LIVE-005 | hoxit 级浏览器兜底基础设施 |

## Acceptance

- 每个 PR 有独立单元测试，不依赖网络。
- 最后 PR 有可选 live smoke，默认跳过。
- 宁波银行 live 报告可生成 Markdown/JSON，核心结论不缺涨跌幅。
- 财务/估值缺口必须明确说明输入缺失来源。
- 数据源不合格时必须记录 field-level quality，并优先评估 hoxit 可复用 fallback，而不是静默缺失。
- 需要用户协助的 Web/Playwright fallback 必须在 implementation report 中明确列出协助项和风险，不能静默引入。
- 所有新增能力走 hoxit provider 或 hoxit reusable helper。

## Review Policy

Codex review 必须检查：

- 是否只处理当前 PR ticket。
- 是否遵守 hoxit-first。
- 是否没有新增 one-off scraper。
- 是否有 mock shape 覆盖真实 live provider 形态。
- 是否对不合格数据源做了质量评估和 fallback 说明。
- 是否有报告产物或 live smoke 证据，至少在 PR-LIVE-005 必须提供。
