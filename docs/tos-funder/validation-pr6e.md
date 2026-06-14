# PR 6E Validation: Unified JSON Schema Examples + Minimal End-to-End Outputs

验证日期：2026-06-02
验证范围：Trading Funder 统一输出 schema 从 text/table 说明升级为正式 JSON schema 示例 + 最小端到端样例

---

## 1. Schema Coverage Verification

### 验证 4 个 schema 示例是否完整

| Schema Anchor | File | Status | Required Fields Present |
|---|---|---|---|
| `#price_series_output` | `output-schema-examples.md` | ✅ | target, source, series, data_quality, adjustment_check, fallback variant |
| `#risk_manager_output` | `output-schema-examples.md` | ✅ | target, data_quality, facts, computed_metrics, data_quality_warnings, action_constraints, risks, opportunities, next_steps; 含 degraded variant + multi-stock variant |
| `#analyze_output` | `output-schema-examples.md` | ✅ | target, data_quality_summary, adjustment_summary, degraded_metrics, blocked_metrics, analyst_signals, combined_signal, action_constraints, final_action, risks, opportunities, next_steps; 含 degraded + valid 变体 |
| `#portfolio_output` | `output-schema-examples.md` | ✅ | portfolio_summary, risk_limits, data_quality_vetoes, risk_vetoes, manual_review_queue, analyst_signal_table, allowed_actions, final_actions, data_quality_warnings, opportunities, next_steps; 含单股/空仓/degraded 边缘案例说明 |

### 每个 schema 必需的 9 层

每层验证：

| 层 | price_series | risk_manager | analyze | portfolio |
|---|---|---|---|---|
| target | ✅ code, name | ✅ code, name, date | ✅ code/name string | ✅ portfolio_summary |
| data_quality | ✅ status, warnings, adjustment_check | ✅ 同左 + risk_metric_status, degraded_metrics, blocked_metrics | ✅ data_quality_summary, adjustment_summary | ✅ data_quality_vetoes |
| facts / computed_metrics | ✅ series[] | ✅ volatility, drawdown, var, liquidity | ✅ analyst_signals | ✅ analyst_signal_table |
| data_quality_warnings | ✅ | ✅ | ✅ | ✅ |
| action_constraints | ❌ N/A (raw data layer) | ✅ action_ceiling + reason | ✅ action_ceiling + reason | ✅ data_quality_vetoes + risk_vetoes |
| signal / final_action | ❌ N/A | ❌ N/A (risk level, not signal) | ✅ final_action | ✅ final_actions[] |
| risks | ❌ N/A | ✅ | ✅ | ✅ |
| opportunities | ❌ N/A | ✅ | ✅ | ✅ |
| next_steps | ❌ N/A | ✅ | ✅ | ✅ |

Note: price_series is a data layer — it provides raw/computed data and adjustment checks but does not generate action-level fields (action_constraints, final_action, risks). This is by design; the price-series command is consumable by risk-manager and technicals, not directly by portfolio.

---

## 2. Analyze Consumption of Degraded Risk Metrics

### 测试: analyzed 能否消费 risk_metric_status=degraded

| 条件 | analyze 行为 | 验证 |
|---|---|---|
| risk_metric_status=degraded | action_constraints.action_ceiling=watch | ✅ 见 analyze.md 样例 |
| 同时 adjustment_status=suspect | manual_review_required=true | ✅ |
| 仅 risk metrics bearish, fundamentals/value neutral | final_action=watch, 不是 reject | ✅ |
| risk metrics bearish + fundamentals also bearish | final_action 可能是 reject | ✅ (constitution 规则: 独立确认才允许) |

**验证通过** — analyze 正确消费 degraded:
- `data_quality_summary.risk_metric_status` 被正确映射
- `action_constraints.action_ceiling` 正确设限
- `degraded_metrics` / `blocked_metrics` 正确列出
- 不输出强硬 sell/reject

---

## 3. Portfolio Consumption of Analyze/Risk Outputs

### 测试: portfolio 能否消费 analyze/risk 的 degraded 输出

| 生产者 → 消费者 | 关键字段 | 映射验证 |
|---|---|---|
| risk-manager → portfolio | `risk_metric_status` | ✅ risk.risk_metric_status 在 analyst_signal_table 中 |
| risk-manager → portfolio | `adjustment_status` | ✅ risk.adjustment_status 在 analyst_signal_table 中 |
| risk-manager → portfolio | `degraded_metrics` | ✅ risk-manager 输出含 degraded_metrics |
| risk-manager → portfolio | `action_constraints.action_ceiling` | ✅ portfolio Step 9 消费 action_ceiling |
| analyze → portfolio | `final_action` | ✅ 可作为 analyst_signal 的补充输入 |
| analyze → portfolio | `data_quality_summary.risk_metric_status` | ✅ 与 risk-manager 的 risk_metric_status 一致 |

**验证通过** — portfolio 可以完全消费 risk-manager 的 degraded 输出:
- `data_quality_vetoes` 从 `adjustment_status=suspect` 或 `risk_metric_status=degraded` 生成
- `manual_review_queue` 从 `manual_review_required=true` 生成
- `allowed_actions` 受 `risk_metric_status` 门控

---

## 4. No New Signal Enum Verification

### 遍历所有修改文件中的 signal 相关字段

| 文件 | 使用的信号枚举 | 新枚举? |
|---|---|---|
| `output-schema-examples.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |
| `skill-workflow.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |
| `command-template.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |
| `analyze.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |
| `portfolio.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |
| `portfolio-synthesis.md` | bullish, neutral, bearish, blocked | ❌ 无新枚举 |

**验证通过** — 未引入新的 signal enum。

---

## 5. No New Action Enum Verification

### 遍历所有修改文件中的 action 相关字段

| 文件 | 使用的动作枚举 | 新枚举? |
|---|---|---|
| `output-schema-examples.md` | buy, hold, sell, reduce, watch, reject, blocked | ❌ 无新枚举 |
| `skill-workflow.md` | buy, hold, sell, reduce, watch, reject, blocked | ❌ 无新枚举 |
| `command-template.md` | buy, hold, sell, reduce, watch, reject, blocked | ❌ 无新枚举 |
| `analyze.md` | buy, hold, sell, reduce, watch, reject, blocked | ❌ 无新枚举 |
| `portfolio.md` | buy, hold, sell, reduce, watch, reject, blocked | ❌ 无新枚举 |

**验证通过** — 未引入新的 action enum。

---

## 6. Degraded Metric → Hard Veto Prevention

### 确认 degraded metric 不被转为 hard veto

| 场景 | 文件 | 验证 |
|---|---|---|
| max_dd 78.5%, risk_metric_status=degraded | `output-schema-examples.md#risk_manager_output` | ✅ degraded variant 中 action_ceiling=watch, max_dd 在 blocked_metrics |
| max_dd 78.5%, risk_metric_status=degraded | `output-schema-examples.md#analyze_output` | ✅ final_action.action=watch, 不是 reject |
| max_dd 78.5%, risk_metric_status=degraded | `output-schema-examples.md#portfolio_output` | ✅ final_actions[002594].action=watch, data_quality_vetoes 阻止 max_dd veto |
| 单日跳变验证 | `skill-workflow.md` Data Quality → Action Mapping | ✅ degraded + suspect/unknown → action ceiling = watch/reduce |
| degrated 时 sell/reject 条件 | `skill-workflow.md` Degraded Metric Handling #6 | ✅ sell/reject 仅当 fundamental/value 独立确认恶化 |

**验证通过** — degraded metric 在所有命令中都不被转为 hard veto。

---

## 7. File Reference Consistency

### 验证 output-schema-examples.md 被正确引用

| 引用方 | 引用格式 | 验证 |
|---|---|---|
| `skill-workflow.md` | 顶层 Schema Reference 表格 + data_quality 字段表 | ✅ |
| `command-template.md` | produced_schema.matches 指向 4 个 anchor | ✅ |
| `analyze.md` | `output-schema-examples.md#analyze_output` | ✅ |
| `portfolio.md` | `output-schema-examples.md#portfolio_output` | ✅ |
| `portfolio-synthesis.md` | 引用 `validation-pr6d-lite.md` | ✅ (已有) |

**验证通过** — 所有引用正确。

---

## 8. Constitution Self-Review

| # | 检查项 | 结果 | 说明 |
|---|---|---|---|
| 1 | 读取最新 accepted schema | ✅ | 读取了 PR6D-lite 的 skill-workflow.md + output-schema-examples.md |
| 2 | 避免新 signal enum | ✅ | 沿用 bullish/neutral/bearish/blocked |
| 3 | 区分 facts/metrics/warnings/interpretation/action | ✅ | schema 示例严格分层 |
| 4 | 标注 fallback 和 degraded 数据 | ✅ | price_series 含 fallback variant; risk_manager 含 degraded variant |
| 5 | 避免从样本验证推出全局正确性 | ✅ | 仅验证 4 个 schema 和 2 个样例 |
| 6 | 区分 data-quality veto 与 risk veto | ✅ | portfolio_output 中两个数组分离 |
| 7 | 下游可直接消费 | ✅ | analyze_output → portfolio 可映射; risk_manager_output → portfolio 可映射 |
| 8 | 保持 iWencai 和 mootdx 边界 | ✅ | 未改数据源政策和 source 标注 |
| 9 | 记录未解决问题 | ✅ | 见下一节 |

---

## 9. 交付总结

### 1. 修改文件列表

| 文件 | 状态 | 变更内容 |
|---|---|---|
| `tos-funder/references/output-schema-examples.md` | 🆕 新建 | 4 个 JSON schema 示例 (price_series, risk_manager, analyze, portfolio) + 变体 + 边缘案例说明 |
| `tos-funder/references/skill-workflow.md` | ✅ 修改 | 新增 Schema Reference 表格指向 output-schema-examples.md; 新增 Required data_quality Fields 表; facts bundle 增加 JSON schema 引用 |
| `tos-funder/references/command-template.md` | ✅ 修改 | 新增 produced_schema (matches + consumable_by); 明确 data_quality_warnings 必需、action_constraints/final_action 按命令层级适用; 新增 3 项 Validation Checklist |
| `tos-funder/commands/tos-funder-analyze.md` | ✅ 修改 | 输出 schema 改为引用 output-schema-examples.md#analyze_output; 新增 002594 degraded 和 600519 valid 两个最小样例; 新增 Required Output Fields 表 |
| `tos-funder/commands/tos-funder-portfolio.md` | ✅ 修改 | 输出 schema 改为引用 output-schema-examples.md#portfolio_output; 精简内联 schema 为摘要; 新增 002594 在 manual_review_queue 中的样例; data_quality_vetoes 与 risk_vetoes 分离 |
| `docs/tos-funder/validation-pr6e.md` | 🆕 新建 | 8 项验证 + constitution self-review |

### 2. 新增/更新的 Schema 列表

| Schema Anchor | 用途 | 变体 |
|---|---|---|
| `output-schema-examples.md#price_series_output` | 价格序列标准化输出 | normal + iwencai_fallback |
| `output-schema-examples.md#risk_manager_output` | 单股和多股风险指标 | verified/valid + suspect/degraded + multi-stock portfolio |
| `output-schema-examples.md#analyze_output` | 综合分析输出 | degraded + valid |
| `output-schema-examples.md#portfolio_output` | 投资组合综合输出 | mixed portfolio with degraded entry; 附带 single-stock / empty / all-degraded 边缘案例 |

### 3. 两个最小端到端样例

**场景 A: 002594 比亚迪 — degraded / manual_review_required**

```
price_series → adjustment_status=suspect → risk-manager → risk_metric_status=degraded
  → analyze: final_action=watch, action_constraints.action_ceiling=watch, manual_review_required=true
  → portfolio: data_quality_vetoes=[002594 max_dd], manual_review_queue=[002594], allowed_actions[002594]=[watch]
```

所有 degraded 护栏均生效: 不 reject/sell, max_dd 不触发硬否决, 仅用 Tier 1 指标。

**场景 B: 600519 贵州茅台 — verified / valid**

```
price_series → adjustment_status=verified → risk-manager → risk_metric_status=valid
  → analyze: final_action=watch, action_constraints.action_ceiling=null, degraded_metrics=[]
  → portfolio: data_quality_vetoes=[], risk_vetoes=[], manual_review_queue=[]
```

正常风险约束生效, 无数据质量约束, 全部指标可用。

### 4. Downstream Compatibility Check

| 生产者 → 消费者 | 字段 | 兼容 |
|---|---|---|
| price_series → risk-manager | `adjustment_check.adjustment_status` | ✅ |
| risk-manager → analyze | `risk_metric_status` | ✅ |
| risk-manager → portfolio | `risk.risk_metric_status`, `risk.adjustment_status` | ✅ |
| analyze → user/portfolio | `final_action`, `action_constraints` | ✅ |
| portfolio → user | `final_actions[]`, `data_quality_vetoes`, `risk_vetoes` | ✅ |

### 5. Constitution Self-Review

全部 9 项检查通过。详见第 8 节。

### 6. 边界和下一步建议

| 项目 | 影响 | 建议 |
|---|---|---|
| `portfolio_output` 已补齐 `opportunities` 字段 | 与其他 schema 保持一致 | 后续命令应继续保留 portfolio-level opportunities, 不要只写入 `next_steps` 或 `reason` |
| `price_series_output` 是纯数据层, 不含 action 字段 | 与其他 schema 层数不同 | 这是设计决定的 — price-series 是基础设施命令 |
| schema 示例目前是 JSON 样例而非正式 JSON Schema (`.d.ts` / OpenAPI) | 无法自动验证输出合规性 | 可考虑将 schema 转为 TypeScript 类型定义或 JSON Schema 格式 |
| 缺少 `output-schema-examples.md` 的 changelog | 多人协作时难以追踪变更 | 可在文件末尾增加 changelog 表 |
