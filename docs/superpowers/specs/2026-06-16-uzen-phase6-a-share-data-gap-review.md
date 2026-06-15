# UZEN Phase 6 A股数据覆盖差距复盘

Date: 2026-06-16
Status: planning

## Purpose

Phase 5 已把 UZEN 从单层报告推进到可审计的 research spine：

```text
raw hoxit snapshot -> dimensions -> synthesis -> report_review -> JSON/Markdown
```

本复盘重新对照 `Reference/UZI-Skill`，决定 Phase 6 的下一步。结论是：不要立即做 HTML、分享图、完整 65 人面板或跨市场。UZEN 当前最关键的缺口是 A股研究数据覆盖不足，尤其是 UZI Task 1 的公司治理、事件催化、产业链/经营、政策/宏观、资金面深度、舆情/社交风险等输入仍没有稳定进入 UZEN snapshot。

## Current UZEN Baseline

已合并能力：

- 7 个 `hoxit uzen` A股模式。
- hoxit-native provider boundary：`UzenDataProvider`。
- 每模式按需调用 source。
- `data_quality.sources` 记录。
- DCF、Comps、market risk、unsupported trap risk、LHB summary。
- 5 个确定性投资者原型。
- `analysis["dimensions"]` 10 维摘要。
- `analysis["synthesis"]` 确定性综合研判。
- `analysis["report_review"]` 非阻断产物自审。
- 可选 Agent Analysis Envelope，含 deep-review 字段。

当前限制：

- 只有 10 个 UZEN 维度，且主要是“数据质量/状态”维度，不是 UZI 的 19 个业务维度评分。
- 治理、经营/产业链、事件催化、政策/宏观、舆情/社交风险没有一等 snapshot source。
- UZEN 没有 raw_data 风格的 A股覆盖矩阵，导致后续 persona、辩论、HTML 都缺底层事实。
- LHB 已有 seat 原始字段，但 UZEN 仍不消费 seat-level 摘要，避免误判是正确的，但也限制了游资分析深度。

## UZI Reference Shape

`Reference/UZI-Skill` 的 deep-analysis 定义了 22 维数据采集，其中 0-19 为采集维度，20-22 为机构建模/研究方法输出。

与 UZEN Phase 6 最相关的是 0-19：

| UZI 维度 | 当前 UZEN 状态 | Phase 6 判断 |
| --- | --- | --- |
| 0 基础信息 | 已覆盖：fundamentals/quote | 保持 |
| 1 财报 | 已部分覆盖：finance/f10/fundamentals | 保持，后续可增强 |
| 2 K线 | 已覆盖：bars | 保持 |
| 3 宏观 | 未进入 UZEN | 延迟或以 iwencai/macro 接口做 data_needed |
| 4 同行 | 已部分覆盖：industry_comparison | 保持，后续增强 |
| 5 上下游 | 未进入 UZEN | Phase 6 重点 |
| 6 研报 | 已覆盖：reports | 保持，增强催化提取 |
| 7 行业景气 | 已部分覆盖：industry/concept | Phase 6 重点 |
| 8 原材料 | 未进入 UZEN | 延迟，先定义缺口 |
| 9 期货 | 未进入 UZEN | 延迟，先定义缺口 |
| 10 估值 | 已覆盖：valuation/metrics + DCF/Comps | 保持 |
| 11 治理 | 未进入 UZEN | Phase 6 重点 |
| 12 资金面 | 已部分覆盖：fund_flow/margin/block/holder | Phase 6 重点 |
| 13 政策 | 未进入 UZEN | Phase 6 轻量接口/缺口记录 |
| 14 专利/护城河 | 未进入 UZEN | 延迟，先定义缺口 |
| 15 事件 | 已有 filings/news，但未结构化为 event | Phase 6 重点 |
| 16 龙虎榜 | 已部分覆盖：records/seats | Phase 6 重点但不做席位身份推断 |
| 17 舆情 | 已有 stock_news，可补 iwencai/sentiment proxy | Phase 6 轻量 |
| 18 杀猪盘 | unsupported | 保持 unsupported，先加 evidence schema |
| 19 实盘赛 | 未覆盖 | 延迟 |

## Phase 6 Goal

建立 A股优先的数据覆盖层，让 UZEN 明确区分：

- 已采集 raw source；
- hoxit 可覆盖但当前模式未调用；
- hoxit 需要新增接口；
- 当前明确不支持的 UZI 维度；
- 后续 agent 可以安全介入的 data gap。

Phase 6 不追求 UZI 22 维全量实现，而是让 UZEN 的 snapshot 与 dimensions 能诚实表达 A股研究事实覆盖。

## Non-Goals

- 不做 HTML、PNG、分享卡或 Playwright 渲染。
- 不做完整 65/66 投资者 persona。
- 不做非 A股、ETF、基金、可转债工作流。
- 不做社交/操纵证据采集的结论性判断。
- 不做 LHB 席位身份分类（机构 vs 游资）或历史席位数据库。
- 不引入 UZI provider chain 或 UZI runtime 代码。
- 不把 agent 定性判断写入 raw data 或 deterministic analysis 对象。

## Data Boundary

执行顺序：

1. 优先使用已有 hoxit 接口。
2. 如果 A股研究必需且 hoxit 已有 iwencai route 可承载，则在 hoxit 现有模块中加可注入、可测试的函数。
3. 如果无法覆盖，写入 `unsupported` 或 `data_needed`，不得编造。
4. 所有新增外部接口必须遵守 hoxit 规范：网络 IO 可注入、第三方库延迟导入、返回 `dict` 或 `list[dict]`、单元测试不联网。
5. 涉及数据接口变更时追加 `docs/API_DEVLOG.md`。

## Recommended Phase 6 Scope

Phase 6 名称：`UZEN A-share Data Coverage`

优先补 5 类数据：

1. **治理/股权结构（governance / ownership）**
   - 复用：holder_num、dividend、lockup、filings。
   - 新增候选：management route 的股权质押、增减持、实控人/高管。

2. **经营/产业链（business / supply-chain）**
   - 复用：fundamentals industry、reports、news。
   - 新增候选：business route 的主营构成、客户/供应商、合同/订单。

3. **事件催化（events / catalysts）**
   - 复用：filings、news、reports。
   - 新增候选：event route 的公告衍生事件。

4. **资金面/LHB 深度（capital action / LHB detail）**
   - 复用：fund_flow、margin_trading、block_trade、holder_num、dragon_tiger seats。
   - 增强：只做 seat 原始摘要和 institution buy/sell count，不做身份推断。

5. **行业/政策/宏观轻量上下文（industry-policy context）**
   - 复用：concept、industry_comparison。
   - 新增候选：industry、macro、event route 的轻量摘要。
   - 原材料/期货先标记 `data_needed`，不硬接。

## Risks

- iwencai route 字段不稳定，必须通过 mock 单元测试和 live integration 可选测试隔离。
- UZI 维度名称容易诱导过度承诺，文档必须持续标注 current vs deferred。
- LHB seat 原始数据容易被误读为“游资身份识别”，Phase 6 只能做事实摘要。
- 数据覆盖变多后，`hoxit/uzen.py` 可能继续膨胀；本阶段只在必要时抽取 helper，避免无意义重构。

## Success Criteria

- UZEN JSON snapshot 新增 A股研究覆盖对象，但旧 key 保持兼容。
- `analysis["dimensions"]` 能反映新增 source 的质量和缺口。
- `analysis["synthesis"]` 可从新增事实产生更具体的 drivers/risks/followups，但不编造。
- Markdown 展示新增事实摘要，不输出 raw dict。
- 文档明确 Phase 6 当前能力与 deferred UZI parity。
- 全部单元测试默认不联网。
