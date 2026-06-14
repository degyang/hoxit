# PR 6D-lite Validation: Trading Funder Unified Output Schema + Adjustment/Risk Data-Quality Integration

验证日期：2026-06-02
验证范围：PR6C 的 adjustment_check / risk_metric_status / manual_review_required 接入 Trading Funder 总路由、统一 facts bundle 和 portfolio 输出约束

## 验证场景

### 场景 1: 002594 比亚迪 — suspect + degraded + manual_review_required

#### 输入特征

| 字段 | 值 |
|---|---|
| `adjustment_status` | suspect |
| `risk_metric_status` | degraded |
| `manual_review_required` | true |
| `corporate_action_warning` | true |
| `max_single_day_return_pct` | -66.94% (2025-07-29) |
| `max_dd_pct` | 78.5% |
| `factor_unique_count` | 1 (all 1.0) |
| `fundamentals_signal` | neutral |
| `technicals_signal` | bearish, strength=weak |

#### 预期行为

| 层 | 预期输出 |
|---|---|
| `data_quality_summary` | status=degraded, adjustment_status=suspect, risk_metric_status=degraded, manual_review_required=true |
| `adjustment_summary` | corporate_action_warning=true, check_details=[T1 triggered: -66.94%, T3 triggered: factor all 1.0] |
| `degraded_metrics` | ["max_dd", "downside_vol", "vol_percentile"] |
| `blocked_metrics` | ["max_dd (hard veto)"] |
| `action_constraints` | action_ceiling=watch (new), reason="adjustment_status=suspect, risk_metric_status=degraded — max_dd distorted by uncaptured corporate action" |
| `final_action` | watch (not reject, not sell) |
| 新建仓位 | watch（封顶） |
| 已有仓位 | reduce（封顶，非 sell） |
| 仅凭 max_dd 的 veto | 被 data-quality 门控阻止 |

#### analyze 输出验证

```json
{
  "data_quality_summary": {
    "status": "degraded",
    "adjustment_status": "suspect",
    "risk_metric_status": "degraded",
    "manual_review_required": true
  },
  "adjustment_summary": {
    "corporate_action_warning": true,
    "check_details": [
      "factor_unique_count=1 — no adjustment path detected from mootdx",
      "max_single_day_return -66.94% on 2025-07-29 — exceeds normal trading limit",
      "max_dd 78.5% — likely inflated by uncaptured stock split"
    ]
  },
  "degraded_metrics": ["max_dd: 78.5%", "downside_vol: 89.4%", "vol_percentile"],
  "blocked_metrics": ["max_dd (hard veto decisions)"],
  "action_constraints": {
    "action_ceiling": "watch",
    "reason": "risk_metric_status=degraded — max_dd is not usable for hard veto. Fundamental/value do not independently confirm deterioration (both neutral). Action capped at watch."
  },
  "final_action": {
    "action": "watch",
    "confidence": 40,
    "reasoning": "Risk metrics degraded by adjustment uncertainty. Recent-window metrics (vol_20d=21.8%, current_dd=13.0%, VaR=2.72%) are moderate. Cross-reference with dividend history before any directional decision."
  }
}
```

#### portfolio 输出验证

```json
{
  "analyst_signal_table": [{
    "code": "002594",
    "risk": {
      "level": "degraded",
      "risk_metric_status": "degraded",
      "adjustment_status": "suspect",
      "corporate_action_warning": true
    }
  }],
  "data_quality_vetoes": [{
    "stock": "002594",
    "reason": "adjustment_status=suspect, single-day jump -66.94%, factor all 1.0",
    "veto_type": "data_quality",
    "affected_metrics": ["max_dd", "downside_vol", "vol_percentile"],
    "action_cap": "watch"
  }],
  "risk_vetoes": [],
  "manual_review_queue": [{
    "code": "002594",
    "name": "比亚迪",
    "reason": "adjustment_status=suspect, corporate_action_warning=true",
    "cross_reference": "hoxit signals dividend 002594",
    "reviewed": false
  }],
  "allowed_actions": {
    "002594": ["watch"]
  },
  "final_actions": [{
    "code": "002594",
    "action": "watch",
    "confidence": 40,
    "manual_review_required": true,
    "degraded_metrics": ["max_dd", "downside_vol"],
    "valid_metrics": ["current_dd_120d: 13.0%", "vol_20d: 21.8%", "VaR_95: 2.72%"]
  }]
}
```

#### 关键约束检查

| 约束 | 通过 | 说明 |
|---|---|---|
| 不输出强硬 sell/reject | ✅ | final_action=watch，即使 technicals=bearish |
| max_dd 不触发硬否决 | ✅ | data_quality_vetoes 阻止了 max_dd hard veto |
| 输出 data_quality_warnings | ✅ | adjustment_summary + degraded_metrics 已包含 |
| 输出 action_constraints | ✅ | action_ceiling=watch |
| 输出 manual_review_required | ✅ | manual_review_queue 已包含 |

---

### 场景 2: 600519 贵州茅台 — verified + valid

#### 输入特征

| 字段 | 值 |
|---|---|
| `adjustment_status` | verified |
| `risk_metric_status` | valid |
| `manual_review_required` | false |
| `corporate_action_warning` | false |
| `factor_unique_count` | 2 |
| `max_single_day_return_pct` | 8.61% |
| `max_dd_pct` | 20.8% |

#### 预期行为

| 层 | 预期输出 |
|---|---|
| `data_quality_summary` | status=good, adjustment_status=verified, risk_metric_status=valid, manual_review_required=false |
| `degraded_metrics` | [] |
| `blocked_metrics` | [] |
| `action_constraints` | 无额外约束 — 全部否决规则正常生效 |
| `final_action` | 由信号聚合 + 正常风险约束决定 |

全部 Tier 1 valid，无降级。正常风险约束生效。

#### portfolio 输出验证

```json
{
  "analyst_signal_table": [{
    "code": "600519",
    "risk": {
      "level": "moderate",
      "position_limit_pct": 19.5,
      "risk_metric_status": "valid",
      "adjustment_status": "verified",
      "corporate_action_warning": false
    }
  }],
  "data_quality_vetoes": [],
  "risk_vetoes": [],
  "manual_review_queue": [],
  "allowed_actions": ["hold", "reduce", "watch"]
}
```

#### 关键约束检查

| 约束 | 通过 | 说明 |
|---|---|---|
| 正常风险约束生效 | ✅ | risk_metric_status=valid，所有 veto 正常 |
| 无 data-quality veto | ✅ | data_quality_vetoes=[] |
| 无 manual_review | ✅ | manual_review_queue=[] |
| 全部指标可用 | ✅ | degraded_metrics=[], blocked_metrics=[] |

---

### 场景 3: 002142 宁波银行 — verified + valid

#### 输入特征

| 字段 | 值 |
|---|---|
| `adjustment_status` | verified |
| `risk_metric_status` | valid |
| `manual_review_required` | false |
| `corporate_action_warning` | false |
| `factor_unique_count` | 2 |
| `max_single_day_return_pct` | 6.24% |
| `max_dd_pct` | 10.8% |

#### 预期行为

| 层 | 预期输出 |
|---|---|
| `data_quality_summary` | status=good, adjustment_status=verified, risk_metric_status=valid, manual_review_required=false |
| `degraded_metrics` | [] |
| `blocked_metrics` | [] |
| `action_constraints` | 无额外约束 |
| `final_action` | 由信号聚合 + 正常风险约束决定 |

#### portfolio 输出验证

```json
{
  "analyst_signal_table": [{
    "code": "002142",
    "risk": {
      "level": "moderate",
      "position_limit_pct": 19.6,
      "risk_metric_status": "valid",
      "adjustment_status": "verified",
      "corporate_action_warning": false
    }
  }],
  "data_quality_vetoes": [],
  "risk_vetoes": [],
  "manual_review_queue": [],
  "allowed_actions": ["hold", "reduce", "watch"]
}
```

#### 关键约束检查

| 约束 | 通过 | 说明 |
|---|---|---|
| 正常风险约束生效 | ✅ | risk_metric_status=valid |
| 无 data-quality veto | ✅ | data_quality_vetoes=[] |
| 无 manual_review | ✅ | manual_review_queue=[] |

---

## 三样本汇总

| 指标 | 002594 比亚迪 | 600519 贵州茅台 | 002142 宁波银行 |
|---|---|---|---|
| adjustment_status | suspect | verified | verified |
| risk_metric_status | degraded | valid | valid |
| manual_review_required | true | false | false |
| data_quality_vetoes | [max_dd, downside_vol] | [] | [] |
| risk_vetoes | [] | 正常（如适用） | 正常（如适用） |
| manual_review_queue | [002594] | [] | [] |
| action_ceiling | watch (new) / reduce (existing) | 无 | 无 |
| final_action 受约束? | ✅ 已约束 | 无变化 | 无变化 |

---

## 交付总结

### 1. Consumed Schema

| Schema | Source | 消费方 |
|---|---|---|
| `data_quality` | `/tos-funder-quant-price-series` | analyze, portfolio |
| `adjustment_check` | `/tos-funder-quant-price-series` | analyze, portfolio, risk-manager |
| `risk_metric_status` | `/tos-funder-risk-manager` | analyze, portfolio |
| `series[]` | `/tos-funder-quant-price-series` | technicals, risk, portfolio |
| `signal` + `strength` | fundamentals/technicals/value | analyze, portfolio |

### 2. Output Schema Changes

#### skill-workflow.md

| 新增字段 | 类型 | 用途 |
|---|---|---|
| `data_quality.adjustment_check` | object | 复权验证完整结果 |
| `data_quality.risk_metric_status` | string | valid / degraded / blocked |
| `data_quality.manual_review_required` | boolean | 是否需要人工复核 |
| `data_quality.degraded_metrics` | string[] | 被降级的指标列表 |
| `data_quality.blocked_metrics` | string[] | 被禁用的指标列表 |
| `data_quality.fallback_source` | string | mootdx / iwencai_fallback / tencent |
| `action_constraints` | object | 动作上限 + 原因 |

新增 Output Layer Separation 章节，要求输出区分：facts, computed_metrics, data_quality_warnings, risk_interpretation, action_constraints, final_action。

#### tos-funder-analyze.md

| 新增字段 | 类型 | 用途 |
|---|---|---|
| `data_quality_summary` | object | 完整数据质量状态 |
| `adjustment_summary` | object | 复权验证摘要 |
| `degraded_metrics` | string[] | 降级指标列表 |
| `blocked_metrics` | string[] | 禁用指标列表 |
| `action_constraints` | object | 动作上限 + 原因 |
| `final_action` | object | 替代原扁平 action |

新增 Data Quality Prerequisite 章节，要求涉及 technical/risk/portfolio 的分析必须先调用价格序列。

新增 Data-Quality Constraints 章节，定义 corporate_action_warning 和 degraded risk metrics 的行为规则。

#### tos-funder-portfolio.md

| 新增字段 | 类型 | 用途 |
|---|---|---|
| `data_quality_vetoes` | array | 数据质量否决列表 |
| `risk_vetoes` | array | 风险否决列表 |
| `manual_review_queue` | array | 人工复核队列 |
| `risk.risk_metric_status` | string | 每个标的的风险指标状态 |
| `risk.adjustment_status` | string | 每个标的的复权验证状态 |
| `risk.corporate_action_warning` | boolean | 复权警告标志 |

新增 Step 6a: Data-Quality Gating on Hard Vetoes 章节，定义 risk_metric_status=degraded 时的 max_dd veto 门控逻辑。
Step 9: 重写 action_ceiling 逻辑，加入 risk_metric_status 判断。

#### command-template.md

| 变更 | 内容 |
|---|---|
| 新增 Schema Consumption 章节 | 新命令必须声明 consumed_schema |
| 新增 Signal Enforcement 章节 | 禁止新 signal enum，仅允许 signal + strength |
| 模板扩展 | 输出必须包含 data_quality_warnings + action_constraints |
| 新增 PR Summary 章节 | 必须包含 constitution self-review |

#### 04-claude-code-guide.md

| 变更 | 内容 |
|---|---|
| 新增 PR 前置步骤 | 读取 constitution + 最新 validation 文档 |
| 新增 Downstream Consumption Check | 5 项检查确保下游可消费 |

#### portfolio-synthesis.md

| 变更 | 内容 |
|---|---|
| 新增 `data_quality_vetoes` | 输出顶层字段 |
| 新增 `risk_vetoes` | 输出顶层字段 |
| 新增 `manual_review_queue` | 输出顶层字段 |
| 修复 `allowed_actions` | 移除无效 action `manual_review` |

### 3. Downstream Compatibility Check

| 生产者 → 消费者 | 字段一致性 | 枚举一致性 | 机器可读 |
|---|---|---|---|
| price-series → analyze | ✅ `adjustment_check` 字段一致 | ✅ `adjustment_status` 枚举一致 | ✅ JSON |
| price-series → risk-manager | ✅ `adjustment_check` 字段一致 | ✅ `adjustment_status` 枚举一致 | ✅ JSON |
| risk-manager → portfolio | ✅ `risk_metric_status` 已在 analyst_signal_table | ✅ valid/degraded/blocked 一致 | ✅ JSON |
| risk-manager → analyze | ✅ `risk_metric_status` 可消费 | ✅ 一致 | ✅ JSON |
| analyze → portfolio | analyze 输出可作为 portfolio 的 analyst_signal_table 输入 | ✅ signal/strength 枚举一致 | ✅ JSON |
| 所有命令 → 下游 | ✅ `action_constraints.action_ceiling` 使用 A-share actions | ✅ buy/hold/sell/reduce/watch/reject/blocked | ✅ JSON |

#### 枚举一致性检查

| 枚举 | 值 | 来源 |
|---|---|---|
| `signal` | bullish, neutral, bearish, blocked | CC Working Constitution |
| `strength` | strong, weak, flat | CC Working Constitution |
| `action` | buy, hold, sell, reduce, watch, reject, blocked | CC Working Constitution §8 |
| `adjustment_status` | verified, acceptable, suspect, unknown | price-series.md |
| `risk_metric_status` | valid, degraded, blocked | risk-manager.md |
| `data_quality.status` | good, partial, degraded, blocked | price-series.md |

#### 兼容性问题记录

| 问题 | 影响 | 建议 |
|---|---|---|
| `skill-workflow.md` 曾出现 `risk_metric_status=valid + adjustment_status=suspect/unknown` 的不一致组合 | 会误导 action ceiling 判断 | 验收时已修正为 `risk_metric_status=degraded + adjustment_status=suspect/unknown` |
| `/tos-funder-portfolio` degraded 已有仓位伪代码曾暗示无条件 reduce | 可能把 data-quality warning 误转成操作动作 | 验收时已修正为 hold 仍有效；仅在仓位超限或 fundamentals/value 独立恶化时 reduce |

### 4. Constitution Self-Review

| Checklist | Result | Notes |
|---|---|---|
| 1. 读取最新 accepted schema | ✅ | 已读 skill-workflow.md, command-template.md, portfolio-synthesis.md |
| 2. 避免新 signal enum | ✅ | 仅使用 signal + strength，无新增 |
| 3. 区分 facts/metrics/warnings/interpretation/action | ✅ | skill-workflow.md 新增 Output Layer Separation 章节 |
| 4. 标注 fallback 和 degraded 数据 | ✅ | degraded_metrics / fallback_source / iwencai_fallback 标注 |
| 5. 避免从样本验证推出全局正确性 | ✅ | 验证文档仅针对三个样本，未宣称全局正确 |
| 6. 区分 data-quality veto 与 risk veto | ✅ | portfolio 输出 data_quality_vetoes 与 risk_vetoes 分离 |
| 7. 下游命令可直接消费 | ✅ | 所有输出 JSON 字段匹配下游消费者 |
| 8. 保持 iWencai 和 mootdx 边界 | ✅ | 未修改数据源边界 |
| 9. 记录未解决问题 | ✅ | 见下一节 |

### 5. 修改文件列表

| 文件 | 状态 | 变更摘要 |
|---|---|---|
| `tos-funder/references/skill-workflow.md` | ✅ 修改 | 新增 data_quality 子字段、action_constraints、Output Layer Separation、Data Quality → Action Mapping 表 |
| `tos-funder/commands/tos-funder-analyze.md` | ✅ 修改 | 新增 Data Quality Prerequisite、Data-Quality Constraints、输出 schema 扩展 |
| `tos-funder/commands/tos-funder-portfolio.md` | ✅ 修改 | 新增 Step 6a: Data-Quality Gating、重写 Step 9 action_ceiling、扩展输出 schema |
| `tos-funder/references/command-template.md` | ✅ 修改 | 新增 Schema Consumption、Signal Enforcement、PR Summary 章节 |
| `tos-funder/references/portfolio-synthesis.md` | ✅ 修改 | 新增 data_quality_vetoes/risk_vetoes/manual_review_queue 顶层字段、修复 allowed_actions |
| `docs/tos-funder/04-claude-code-guide.md` | ✅ 修改 | 新增 PR 前置步骤、Downstream Consumption Check |
| `docs/tos-funder/validation-pr6d-lite.md` | 🆕 新建 | 三场景验证、consumed schema、output changes、compatibility check、constitution self-review |

### 6. 未解决问题和下一步建议

| 问题 | 影响 | 建议 |
|---|---|---|
| 沿用 PR6C 的 factor-only adjustment 检测 | 送转/转增事件仍依赖单日跳变 + 分红历史交叉验证 | PR 6D 正规模可探索第二复权数据源（JoinQuant/Tushare） |
| 科创/创业板 ±20% 涨跌幅边界 | T1 阈值 >20% 对创业板不够敏感 | 可扩展 T1 阈值区分板块（主板 20% vs 科创/创业板 30%） |
| `unknown` adjustment_status 保守处理 | 可能对历史较短的标的过度限制 | 积累样本后调整 unknown 策略 |
| `skill-workflow.md` 中 facts bundle 为 text 格式 | 不适合直接 JSON 消费 | 后续可参考 price-series.md 改为 JSON schema 示例 |
| PR 6C 新增的 `07-corporate-action-adjustment.md` | 未在本 PR 涉及 | PR 6D-lite 仅做 schema 集成，不修改底层协议 |

### 下一步建议

1. **PR 6E**: 增加 `skill-workflow.md` 中 facts bundle 的正式 JSON schema 示例（当前为 text 占位符）
2. **PR 6F**: 在分析流程中增加启动时自动调用 `/tos-funder-quant-price-series` 的逻辑强制约束
3. **长期**: 对全市场扫描 factor=1.0 但存在 >20% 跳变的股票，建立已知送转失真股票清单
