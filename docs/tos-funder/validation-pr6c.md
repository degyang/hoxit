# PR 6C Validation: Corporate Action / Adjustment Verification

验证日期：2026-06-02
验证方法：`/tmp/risk_compute.py` 对三个样本分别计算 adjustment check 指标，结果与 `docs/tos-funder/07-corporate-action-adjustment.md` 协议交叉验证。

## 样本 1: 002594 比亚迪

### 价格序列

| 字段 | 值 |
|---|---|
| source | mootdx |
| period | daily |
| adjustment | qfq |
| total_rows | 250 (after NaN filter: 248) |
| first_date | 2025-06-02 |
| last_date | 2026-06-02 |

### Adjustment Check

| 指标 | 值 |
|---|---|
| `factor_unique_count` | 1 (all 1.0) |
| `max_single_day_return_pct` | -66.94% |
| `max_single_day_return_date` | 2025-07-29 |
| `max_dd_pct` | 78.5% |
| `regime_shift_median_pct` | 11.4% |
| `adjustment_status` | **suspect** |
| `corporate_action_warning` | **true** |
| `risk_metric_status` | **degraded** |
| `manual_review_required` | **true** |

### 触发条件

| 触发条件 | 阈值 | 实际值 | 触发 |
|---|---|---|---|
| T1: 单日回报 >20% | >20% | -66.94% | ✅ |
| T2: 最大回撤 >50% | >50% | 78.5% | ✅ |
| T3: Factor 全为 1.0 | all == 1.0 | 1.0 × 248 rows | ✅ |
| T4: Regime shift >30% | >30% | 11.4% | ❌ |

T1 + T3 同时触发 → 强数据质量警示：factor 无变化，但存在超出正常交易限制的单日跳变 → 高度疑似未捕获的送转事件。

### 分类路径

```
unique_factors == 1 AND max_single_day_return > 20% → suspect
```

### 风险指标降级

| Tier 1: Valid（可用） | Tier 2: Degraded（降级） | Tier 3: Blocked（禁用） |
|---|---|---|
| vol_20d: 21.8% | max_dd: 78.5% | max_dd（硬否决） |
| vol_60d | downside_vol: 89.4% | |
| current_dd (120d): 13.0% | vol_percentile | |
| VaR 95%: 2.72% | | |
| liquidity | | |

### 动作约束

| 约束 | 值 |
|---|---|
| 新建仓位 | `watch`（封顶） |
| 已有仓位 | `reduce`（最大减仓，非 sell） |
| 硬否决 | max_dd 否决停用 |
| 交叉验证 | `hoxit signals dividend 002594` 确认 2025-07-29 送转事件 |

### 结论

✅ **必须触发 `suspect` + `manual_review_required`** — 已确认。

2025-07-29 的 -66.94% 单日跳变超出 002594 正常交易限制；配合 factor 全为 1.0，以及 `hoxit signals dividend 002594` 返回同日 `bonus_ratio=8`，足以将该段 max_dd 归类为高度疑似复权失真，而不是可直接用于硬否决的真实价格崩塌证据。当前近期指标（DD 13.0%、vol 21.8%、VaR 2.72%）仍可作为 Tier 1 recent-window metrics 使用。

---

## 样本 2: 600519 贵州茅台

### 价格序列

| 字段 | 值 |
|---|---|
| source | mootdx |
| period | daily |
| adjustment | qfq |
| total_rows | 250 (after NaN filter: 249) |
| first_date | 2025-06-02 |
| last_date | 2026-06-02 |

### Adjustment Check

| 指标 | 值 |
|---|---|
| `factor_unique_count` | 2 |
| `max_single_day_return_pct` | +8.61% / -3.80% |
| `max_single_day_return_date` | N/A（均在 normal range 内） |
| `max_dd_pct` | 20.8% |
| `regime_shift_median_pct` | 2.7% |
| `adjustment_status` | **verified** |
| `corporate_action_warning` | **false** |
| `risk_metric_status` | **valid** |
| `manual_review_required` | **false** |

### 触发条件

| 触发条件 | 阈值 | 实际值 | 触发 |
|---|---|---|---|
| T1: 单日回报 >20% | >20% | 8.61% | ❌ |
| T2: 最大回撤 >50% | >50% | 20.8% | ❌ |
| T3: Factor 全为 1.0 | all == 1.0 | 2 distinct values | ❌ |
| T4: Regime shift >30% | >30% | 2.7% | ❌ |

无任何触发条件激活。

### 分类路径

```
unique_factors >= 2 AND max_single_day_return <= 20% AND max_dd <= 50% → verified
```

### 风险指标

全部 Tier 1 valid，无降级。

### 动作约束

无动作约束 — 全部否决规则正常生效。

### 结论

✅ **应为 `verified` 或 `acceptable`** — 已确认为 `verified`。

Factor 有 2 个不同值（分红复权路径活跃），无任何极端跳变，回撤在正常范围。

---

## 样本 3: 002142 宁波银行

### 价格序列

| 字段 | 值 |
|---|---|
| source | mootdx |
| period | daily |
| adjustment | qfq |
| total_rows | 250 (after NaN filter: 249) |
| first_date | 2025-06-02 |
| last_date | 2026-06-02 |

### Adjustment Check

| 指标 | 值 |
|---|---|
| `factor_unique_count` | 2 |
| `max_single_day_return_pct` | +6.24% / -5.10% |
| `max_single_day_return_date` | N/A |
| `max_dd_pct` | 10.8% |
| `regime_shift_median_pct` | 9.3% |
| `adjustment_status` | **verified** |
| `corporate_action_warning` | **false** |
| `risk_metric_status` | **valid** |
| `manual_review_required` | **false** |

### 触发条件

| 触发条件 | 阈值 | 实际值 | 触发 |
|---|---|---|---|
| T1: 单日回报 >20% | >20% | 6.24% | ❌ |
| T2: 最大回撤 >50% | >50% | 10.8% | ❌ |
| T3: Factor 全为 1.0 | all == 1.0 | 2 distinct values | ❌ |
| T4: Regime shift >30% | >30% | 9.3% | ❌ |

无任何触发条件激活。

### 分类路径

```
unique_factors >= 2 AND max_single_day_return <= 20% AND max_dd <= 50% → verified
```

### 风险指标

全部 Tier 1 valid，无降级。

### 动作约束

无动作约束 — 全部否决规则正常生效。

### 结论

✅ **应为 `verified` 或 `acceptable`** — 已确认为 `verified`。

Factor 有 2 个不同值，无极端跳变，回撤和 regime shift 均在正常范围。

---

## 三样本汇总

| 指标 | 002594 比亚迪 | 600519 贵州茅台 | 002142 宁波银行 |
|---|---|---|---|
| rows | 248 | 249 | 249 |
| factor_unique_count | 1 | 2 | 2 |
| max_single_day_return | **-66.94%** | +8.61% | +6.24% |
| max_dd | **78.5%** | 20.8% | 10.8% |
| adjustment_status | **suspect** | verified | verified |
| corporate_action_warning | **true** | false | false |
| risk_metric_status | **degraded** | valid | valid |
| manual_review_required | **true** | false | false |
| action_constraint_effect | watch/reduce cap, no max_dd veto | none | none |

---

## 交付总结

### 1. 修改文件列表

| 文件 | 状态 | 变更内容 |
|---|---|---|
| `docs/tos-funder/07-corporate-action-adjustment.md` | 新建 | 完整复权验证协议：触发条件、分类决策树、风险指标分层、动作约束 |
| `tos-funder/references/price-series.md` | 修改 | 新增 qfq factor 警告；新增 Adjustment Verification 附录 |
| `tos-funder/commands/tos-funder-quant-price-series.md` | 修改 | 新增 Step 6: Adjustment Verification Check（含 verified/suspect 输出样例） |
| `tos-funder/commands/tos-funder-risk-manager.md` | 修改 | 新增 Step 2a: Adjustment Verification；条件化 max_dd 否决；新增 Step 5a: Risk Metric Tier System |
| `tos-funder/references/portfolio-synthesis.md` | 修改 | 区分 Risk Veto / Data-Quality Veto；新增 Veto Resolution Order；扩展决策矩阵（10×3 entry, 8×4 exit）；新增 BYD degraded 示例 |

### 2. 三个样本的 Adjustment Verification 结果

- **002594 比亚迪**: `suspect` — factor 全 1.0 + -66.94% 单日跳变，corporate_action_warning=true，manual_review_required=true
- **600519 贵州茅台**: `verified` — 2 factor values，max 单日变动 8.61%，无异常
- **002142 宁波银行**: `verified` — 2 factor values，max 单日变动 6.24%，无异常

### 3. 哪些 Risk Metrics 被降级，哪些仍可用

**比亚迪（degraded）**：
- 降级（Tier 2）：max_dd (78.5%)、downside_vol (89.4%)、vol_percentile
- 禁用（Tier 3）：max_dd 用于硬否决
- 可用（Tier 1）：vol_20d (21.8%)、vol_60d、current_dd (13.0%)、VaR 95% (2.72%)、liquidity

**茅台 & 宁波银行（valid）**：全部指标可用，无降级。

### 4. Portfolio Action 约束如何变化

| 场景 | 旧行为（PR 6B） | 新行为（PR 6C） |
|---|---|---|
| 比亚迪 max_dd 78.5% | 自动硬否决 → reject | 识别为复权失真 → watch/reduce cap，manual_review_required |
| 茅台 max_dd 20.8% | 正常评估 | 不变（verified，全部否决规则生效） |
| 宁波银行 max_dd 10.8% | 正常评估 | 不变 |
| 某股 factor=2 + max_dd=55% + 无跳变 | 自动否决 | verified → 硬否决仍然生效（真正的 risk veto） |
| 某股 factor=1 + max_dd=35% | 正常评估 | unknown → conservative posture，watch 封顶 |

关键区别：**同一 max_dd 数值，因 adjustment_status 不同而采取不同动作**。

### 5. 未解决问题和下一步建议

| 问题 | 影响 | 建议 |
|---|---|---|
| mootdx factor 不完全覆盖送转/转增 | 依赖单日跳变 + 分红历史交叉验证，非自动化 | PR 6D 可探索 mootdx 以外的复权数据源（如 JoinQuant、Tushare）验证复权正确性 |
| iWencai 前复权方法论不透明 | 无法作为复权正确性的独立验证 | 保持 iWencai 仅用于 post-distortion 近期价格交叉对比 |
| 未知复权路径的边缘情况 | `unknown` 状态保守处理，可能过度限制 | 积累更多样本后可以调整 `unknown` 的处理策略（如按行业/市值区分） |
| 单一数据源依赖 | 如果 mootdx 不可用，无法做复权验证 | iWencai fallback 已标注不可用于复权正确性验证；长期可引入第二复权数据源 |
| 科创/创业板 ±20% 涨跌幅 | T1 阈值 >20% 对这些股票可能不够敏感 | 当前阈值对主板有效；如扩展到科创/创业板，需将 T1 调整为 >30% |

### 下一步建议

- **PR 6D**: 引入 JoinQuant/Tushare 作为第二复权数据源，交叉验证 mootdx qfq 正确性
- **短期**: 已通过 `.venv/bin/hoxit signals dividend 002594 --page-size 10` 验证 2025-07-29 存在 `bonus_ratio=8` 送股事件；后续可将该验证流程自动化。
- **中期**: 对全市场扫描 factor=1.0 但存在 >20% 跳变的股票，建立已知送转失真股票清单

### 6. Constitution Self-Review

| Checklist | Result |
|---|---|
| 读取并遵守 `07-cc-working-constitution.md` | ✅ 已补充验收自检 |
| 避免从样本验证推出全局正确性 | ✅ 已将过强表述改为“高度疑似/交叉验证支持” |
| 沿用最新 signal schema | ✅ 未引入新 signal enum |
| 区分 facts / metrics / warnings / interpretation / action constraints | ✅ validation 和协议分层输出 |
| degraded metric 不直接触发 hard veto | ✅ max_dd veto 受 `adjustment_status` 门控 |
| iWencai 未被用于复权正确性证明 | ✅ iWencai 仅保留为价格 fallback/cross-reference |
| 下游 portfolio 可消费 | ✅ 输出 `adjustment_status`、`risk_metric_status`、`manual_review_required` |
| 未解决问题明确列出 | ✅ 第二复权源、全市场扫描、创业板/科创板阈值 |
