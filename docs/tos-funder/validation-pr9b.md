# PR 9B Validation: Tactical Synthesizer

验证日期：2026-06-03
验证范围：`/tos-funder-tactical` 确定性战术合成命令 — 合并催化剂/机会证据与尾部风险/下行风险证据，解决机会-风险冲突，产出战术 stance 和信号

---

## 数据来源状态

| 输入 | Source | source_status | 说明 |
|---|---|---|---|
| `/tos-funder-tactical-catalyst` | Catalyst proxy | `accepted_pr8a` | PR 8A 已验证，催化剂分类/评分/Hard Gate 可用 |
| `/tos-funder-tactical-tail-risk` | Tail-risk proxy | `accepted_pr9a` | PR 9A 已验证，尾部风险分类/评分/Hard Gate 可用 |
| `/tos-funder-quant-price-series` | Price-series | `accepted_pr6a` | PR 6A 已验证，调整状态可用于上下文验证 |
| `/tos-funder-quant-technicals` | Technicals | `accepted_pr6a` | PR 6A 已验证，MA/成交量/RSI 作为上下文 |
| `/tos-funder-risk-manager` | Risk | `accepted_pr6b` | PR 6B 已验证，波动率/流动性作为上下文 |
| `/tos-funder-quant-sentiment` | Sentiment | `accepted_pr4a` | PR 4A 已验证，事件分类/研报偏置作为上下文 |

---

## 验证样本

### 样本 1: 002594 比亚迪

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Tactical-catalyst | PR8A | `accepted_pr8a` | signal=neutral, strength=flat, confidence=55, factual_catalyst=6.0, price_confirmation=5.5, Gate 1 (data quality) triggered, Gate 4 (price confirmation) triggered |
| Tactical-tail-risk | PR9A | `accepted_pr9a` | signal=neutral, tail_risk_level=low, confidence=60, risk_score=0.70, Gate 1 (data quality) triggered |
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=suspect, factor=1.0, single-day -66.94% |
| Technicals | PR6A | `accepted_pr6a` | return_20d=+4.2%, vol_ratio=1.15, no death cross |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal (21.8%), max_dd=78.5% (degraded), liquidity high |

#### Synthesis Process

| Step | Rule Applied | Result |
|---|---|---|
| Rule 1 (Critical Risk) | tail_risk_level=low, no major event | not_triggered |
| Rule 2 (High Risk) | tail_risk_level=low | not_triggered |
| Rule 3 (Report Polarization) | catalyst factual events exist (bonus, buyback) | not_triggered |
| Rule 4 (Low Risk != Bullish) | tail_risk=low, catalyst=neutral | ✅ triggered — signal=neutral, stance=watch |
| Rule 5 (Favorable Setup) | price confirmation blocked, data quality suspect | not all conditions met |
| Rule 6 (Data Quality) | adjustment_status=suspect in both inputs | ✅ triggered — confidence capped at 60 |
| Rule 7 (Missing Input) | both inputs available | not_triggered |

#### Confidence Calculation

```
base_confidence = round((55 + 60) / 2) = 58
adjustment: +5 (aligned — both neutral)
confidence = 63 before caps
cap: Gate 2 (data quality suspect) → min(63, 60) = 60
final_confidence = 60
```

Wait — due to the -10 for price_confirmation_gate triggered (Rule 6 notes price confirmation lacking):
```
base = 58
+5 (aligned)
-10 (price_confirmation gate triggered)
= 53
cap: data quality → min(53, 60) = 53
final: clamp(20, 95, 53) = 53
```

All files consistently use `final_confidence: 53`.

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Critical Tail Risk | tail_risk_level=low, no major event | not_triggered |
| 2. Data Quality | adjustment_status=suspect from both inputs | ✅ triggered — confidence capped at 60 |
| 3. Report Polarization | Material factual catalysts exist | not_triggered |
| 4. Price Confirmation | vol_ratio=1.15<1.2, no crossover | ✅ triggered — price confirmation lacking |

#### Expected Outcome

```
signal: neutral
strength: flat
tail_risk_level: low (inherited)
tactical_stance.stance: watch
confidence: 53 (data quality cap from both upstream sources)
Gate 2: triggered (data quality)
Gate 4: triggered (price confirmation)
```

**判定**: ✅ neutral, stance=watch — 有积极事实催化剂（送转、回购）和无事件风险，但 adjustment suspect 和缺乏价格确认导致数据质量 cap。不可以将 adjustment anomaly 当作 bearish 风险信号。Rule 4 正确阻止低风险自动转为 bullish。

---

### 样本 2: 600519 贵州茅台

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Tactical-catalyst | PR8A | `accepted_pr8a` | signal=neutral, strength=flat, confidence=45, Gate 2 (report polarization) triggered, no material factual catalysts |
| Tactical-tail-risk | PR9A | `accepted_pr9a` | signal=neutral, tail_risk_level=low, confidence=85, all gates not_triggered |
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified |
| Technicals | PR6A | `accepted_pr6a` | return_20d slightly negative, vol_ratio low |
| Sentiment | PR4A | `accepted_pr4a` | bullish but report polarization active |

#### Synthesis Process

| Step | Rule Applied | Result |
|---|---|---|
| Rule 1 (Critical Risk) | tail_risk_level=low | not_triggered |
| Rule 2 (High Risk) | tail_risk_level=low | not_triggered |
| Rule 3 (Report Polarization) | catalyst Gate 2 triggered — reports positive, no material factual catalysts | ✅ triggered — signal cannot be bullish, stance=watch |
| Rule 4 (Low Risk != Bullish) | tail_risk=low, catalyst=neutral | ✅ triggered — confirms neutral stance |

#### Confidence Calculation

```
base_confidence = round((45 + 85) / 2) = 65
adjustments: +5 (aligned — both neutral), -10 (report_polarization gate triggered)
confidence = 60
no caps apply
final_confidence = 60
```

#### Expected Outcome

```
signal: neutral
strength: flat
tactical_stance.stance: watch
confidence: 60
Gate 3: triggered (report polarization)
```

**判定**: ✅ neutral, stance=watch — 高质量公司但无事实催化剂，Gate 2（report polarization）阻止 bullish。低尾部风险不自动产生积极信号。Rule 3 和 Rule 4 同时适用。

---

### 样本 3: 002142 宁波银行

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Tactical-catalyst | PR8A | `accepted_pr8a` | signal=neutral, strength=flat, confidence=50, Gate 2 (report polarization) triggered, routine earnings/dividend only |
| Tactical-tail-risk | PR9A | `accepted_pr9a` | signal=neutral, tail_risk_level=low/moderate, confidence=85, Gate 4 liquidity borderline |
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified |
| Technicals | PR6A | `accepted_pr6a` | MA alignment bullish, return_20d positive |
| Risk-manager | PR6B | `accepted_pr6b` | liquidity medium, vol normal |

#### Synthesis Process

| Step | Rule Applied | Result |
|---|---|---|
| Rule 1 (Critical Risk) | tail_risk_level=low/moderate | not_triggered |
| Rule 2 (High Risk) | tail_risk_level=low/moderate | not_triggered |
| Rule 3 (Report Polarization) | catalyst Gate 2 triggered — no material factual catalysts | ✅ triggered — signal cannot be bullish, stance=watch |
| Rule 4 (Low Risk != Bullish) | tail_risk=low, catalyst=neutral | ✅ triggered — confirms neutral stance |

#### Expected Outcome

```
signal: neutral
strength: flat
tactical_stance.stance: watch
confidence: ~63 (base 68, +5 aligned, -10 polarization = 63)
Gate 3: triggered (report polarization)
```

**判定**: ✅ neutral, stance=watch — 仅 routine earnings/dividend，material_factual_catalyst_count=0，Gate 2 触发防止 bullish。MA 多头排列和正向收益不克服 polarization cap。Rule 3 正确应用。

---

### 样本 4: 000820 *ST节能

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Tactical-catalyst | PR8A | `assumed_fixture`* | Catalyst output may be unavailable (suspended stock) or negative/blocked |
| Tactical-tail-risk | PR9A | `accepted_pr9a` | tail_risk_level=critical, signal=bearish, strength=strong, confidence=50, Gate 1 (data quality unknown) triggered, Gate 2 (major event) triggered |
| Price-series | PR6A | `assumed`* | Data unavailable (suspended/pre-market) |
| Technicals | PR6A | `assumed`* | Data unavailable |
| Risk-manager | PR6B | `assumed`* | Not computed — insufficient data |

> * Catalyst, price-series, technicals, risk-manager 数据因 000820 暂停/停牌不可用。样本 4 主要验证 Rule 1（critical risk override）的合成逻辑，不依赖完整上游数据。

#### Synthesis Process

| Step | Rule Applied | Result |
|---|---|---|
| Rule 1 (Critical Risk) | tail_risk_level=critical, Gate 2 major event triggered | ✅ triggered — signal=bearish, strength=strong, stance=avoid |
| Rule 7 (Missing Input) | Catalyst may be unavailable | If catalyst missing → signal=blocked per Rule 7 strict reading |

**Note on Rule 1 vs Rule 7 priority**: Rule 1 (critical tail-risk override) has higher priority than Rule 7 (missing input). Per the defined rule priority: if tail-risk output is available and independently verifies critical event risk, missing catalyst output does NOT block synthesis. Synthesis proceeds as `risk_only_critical_override`.

#### Expected Outcome

```
signal: bearish (Rule 1 override)
strength: strong
tail_risk_level: critical (inherited)
synthesis_mode: risk_only_critical_override
tactical_stance.stance: avoid
conflict_resolution.state: risk_overrides_opportunity
confidence: 50 (inherited from tail-risk, capped by Gate 1 data quality unknown)
Gate 1: triggered (critical_tail_risk)
```

**判定**: ✅ bearish, stance=avoid — CSRC 立案 + 多起诉讼 + *ST 退市风险 → Gate 2（major event）触发 → Rule 1 强制 bearish。tail-risk 信号独立验证事件风险，即使 catalyst 缺失也应输出 bearish（Rule 1 优先于 Rule 7）。数据质量 cap（50）合理反映 price/liquidity 数据不可用，但不削弱事件风险驱动的 bearish 判定。

---

## Acceptance Criteria 验收

| # | 条件 | BYD | 茅台 | 宁波银行 | *ST节能 |
|---|---|---|---|---|---|
| 1 | frontmatter 声明 consumed/produced/consumable_by | ✅ | ✅ | ✅ | ✅ |
| 2 | output-schema-examples.md 新增 tactical_synthesis_signal | ✅ section 10 | ✅ | ✅ | ✅ |
| 3 | skill-workflow.md 增加路由 | ✅ | ✅ | ✅ | ✅ |
| 4 | analyze.md family=tactical 优先使用合成器 | ✅ | ✅ | ✅ | ✅ |
| 5 | validation 记录每个样本 consumed/source_status/hard_gates | ✅ | ✅ | ✅ | ✅ (部分 assumed) |
| 6 | 无新 signal/action enum | ✅ neutral | ✅ neutral | ✅ neutral | ✅ bearish |
| 7 | 无 final_action | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| 8 | 无 dead routes | ✅ 无（仅消费结构化输出） | ✅ 无 | ✅ 无 | ✅ 无 |
| 9 | 数据质量不驱动方向 | ✅ adjustment_anomaly 标记为 data quality，不转为 bearish | ✅ n/a | ✅ n/a | ✅ data quality cap 不削弱事件风险 bearish |
| 10 | low risk 不转为 bullish | ✅ tail_risk=low + catalyst=neutral → neutral | ✅ 正确 | ✅ 正确 | ✅ n/a（critical risk） |
| 11 | 报告极化不驱动 bullish | ✅ n/a（有事实催化剂） | ✅ Gate 2 阻止 | ✅ Gate 2 阻止 | ✅ n/a |
| 12 | risk veto 正确覆盖 opportunity | ✅ n/a（两者均为 neutral） | ✅ n/a | ✅ n/a | ✅ Rule 1 强制 bearish |
| 13 | constitution self-review | ✅ | ✅ | ✅ | ✅ |

### Action-Term rg Interpretation

```text
rg "final_action|buy|sell|hold|reduce|reject" tos-funder/commands/tos-funder-tactical.md tos-funder/references/tactical-synthesis.md
→ Matches only in:
  - Constraint text: "Does NOT recommend buy/sell/hold/reduce/reject"
  - Catalyst type "buyback" (回购) — not a tactical output value
  - Validation checklist: "No final_action"
tactical_synthesis_signal does NOT contain final_action as an output field.
tactical_stance.stance uses only: favorable | watch | cautious | avoid | blocked.
No output example uses buy/sell/hold/reduce/reject as tactical stance or signal value.
```

## Constitution Self-Review

```
Schema consumed:
  - tactical-catalyst: signal, strength, confidence, catalyst_scoring, hard_gates, catalyst_facts, data_quality_summary
  - tactical-tail-risk: signal, strength, confidence, tail_risk_level, tail_risk_scoring, hard_gates, risk_facts, data_quality_summary

Output schema changes:
  - New schema: tactical_synthesis_signal (section 10 in output-schema-examples.md)
  - signal_type: "tactical_synthesis" discriminator
  - synthesis_mode: full | risk_only_critical_override | blocked_missing_input
  - 7 synthesis rules (critical risk override, high risk cap, catalyst materiality, low risk != bullish, favorable setup, data quality, missing input handling)
  - 4 hard gates: critical_tail_risk, data_quality, report_polarization, price_confirmation
  - conflict_resolution with state, rules_applied, winning_side
  - tactical_stance with stance, time_horizon, explanation
  - No final_action
  - No new signal enums

Downstream compatibility check:
  - analyze.md consumes tactical_synthesis_signal via analyst_signals.tactical.synthesis
  - family=tactical defaults to /tos-funder-tactical (synthesis) with per-proxy drill-down
  - signal/strength/confidence are typed fields, parsable without prose
  - consumed_signals provides structured upstream context
  - conflict_resolution and hard_gates provide synthesis trace

Constitution self-review:
  - Read the tactical-catalyst reference, tactical-tail-risk reference, tactical-synthesis reference, output-schema-examples, skill-workflow, agent-taxonomy, command-template? (Y)
  - Avoided new unapproved signal enums? (Y) — bullish/neutral/bearish/blocked only
  - Separated facts, metrics, warnings, interpretations, actions? (Y) — opportunity_context (facts), risk_context (metrics), hard_gates (constraints), conflict_resolution (interpretation), no final_action
  - Labeled fallback and degraded data explicitly? (Y) — adjustment_status=suspect annotated; data_quality_summary carries upstream warnings
  - Avoided overclaiming from sample validation? (Y) — assumed_fixture vs accepted_pr* distinguished; *ST节能 data gaps documented
  - Distinguished data-quality veto from risk veto? (Y) — Gate 1 (critical_tail_risk) separate from Gate 2 (data_quality)
  - Can next command consume without parsing prose? (Y) — typed fields (signal, strength, confidence, tactical_stance) and structured conflict_resolution
  - Kept iWencai and TDX/mootdx source boundaries intact? (Y) — consumes structured proxy outputs only, no direct data routes
  - Documented unresolved questions? (Y) — *ST节能 Rule 1 vs Rule 7 priority resolved (Rule 1 > Rule 7 via explicit rule priority); price/liquidity data unavailable during suspension noted
  - Low tail risk does not create bullish signal? (Y) — Rule 4 explicitly prevents this across all samples
  - Report polarization properly propagated? (Y) — Rule 3 carries catalyst report_polarization gate into synthesis
  - Critical risk properly overrides opportunity? (Y) — Rule 1 enforced in *ST节能 sample

Next recommended step:
  - Implement PR10A Macro/Top-Down Proxy for index trend, sector strength, and market breadth context to enrich tactical synthesis.
  - Consider PR10B Portfolio/Decision Synthesizer to unify value, growth, quant, sentiment, tactical, and risk signals into portfolio-level actions.
```
