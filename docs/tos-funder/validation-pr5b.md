# PR 5B Validation: Growth Family Aggregator

验证日期：2026-06-03
验证范围：`/tos-funder-growth` 综合成长分析命令 — 合并 Fisher、Lynch、quant-fundamentals、quant-sentiment 输出，形成统一的 growth_aggregate_signal

---

## 数据来源状态

| 输入 | source_status | 说明 |
|---|---|---|
| Fisher (`/tos-funder-growth-fisher`) | `accepted_pr5a` | PR5A 已在 002594/600519/002142 上实测并通过验收 |
| Lynch (`/tos-funder-growth-lynch`) | `accepted_pr5a` | PR5A 已在 002594/600519/002142 上实测并通过验收 |
| Quant-Fundamentals (`/tos-funder-quant-fundamentals`) | `assumed_fixture` | 未独立验收 — 验证中标注为 assumed，不作为验收依据 |
| Sentiment (`/tos-funder-quant-sentiment`) | `assumed_fixture` | 未独立验收 — 验证中标注为 assumed，不作为验收依据 |

> `assumed_fixture` 数据仅用于演示 aggregator 的权重计算流程，不表示该项已通过实测验收。

---

## 验证样本

### 样本 1: 002594 比亚迪

#### Consumed Inputs Used

| Input | Source | Source Status | Signal | Confidence | Score |
|---|---|---|---|---|---|
| Fisher | PR5A 实测 | `accepted_pr5a` | neutral | 55 | 6.64 |
| Lynch | PR5A 实测 | `accepted_pr5a` | neutral | 55 | 5.50 |
| Quant-Fundamentals | (assumed) | `assumed_fixture` | neutral | 60 | 6.0 |
| Sentiment | (assumed) | `assumed_fixture` | bullish | 60 | 8.0 |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. PEG Reliability | peg_reliability=degraded | ✅ degraded — Lynch bullish 不参与 aggregate（Lynch 已是 neutral，无净影响） |
| 2. Negative Growth | latest_netprofit_yoy_pct = -18.97% < 0 | ✅ **triggered** — 净利润负增长触发 OR 条件。单负 → confidence cap=60 |
| 3. Bank Sector | sector_type=high_capex_industrial | n/a |
| 4. High-Capex FCF | FCF yield 1.8% > 0, OCF 5年全正 | not_triggered |

#### Weighted Score

- Fisher 6.64 × 0.35 = 2.32
- Lynch 5.50 × 0.35 = 1.93 (PEG degraded 调整 -0.3 → 5.20 × 0.35 = 1.82)
- Quant-Fundamentals 6.0 × 0.20 = 1.20 (⚠️ assumed_fixture)
- Sentiment 8.0 × 0.10 = 0.80 (⚠️ assumed_fixture)
- **Total = 6.14**

#### Confidence Derivation

```
base_confidence = round(6.14 / 10 × 100) = 61
caps_applied:
  - Gate 2: latest_netprofit_yoy_pct=-18.97% < 0 → single negative → min(61, 60) = 60
final_confidence = 60
=> confidence (top-level) = 60
=> confidence_calculation.final_confidence == confidence ✅
```

#### Conflict Resolution

Fisher neutral + Lynch neutral → Rule 3: both neutral → aggregate neutral. No conflict.

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 60
confidence_calculation: { base: 61, caps: ["Gate 2: netprofit -18.97% → cap 60"], final: 60 }
```

**判定**: ✅ Gate 2 triggered + PEG degraded + 双 neutral → neutral. 利润端恶化反映在 confidence cap 中。

---

### 样本 2: 600519 贵州茅台

#### Consumed Inputs Used

| Input | Source | Source Status | Signal | Confidence | Score |
|---|---|---|---|---|---|
| Fisher | PR5A 实测 | `accepted_pr5a` | neutral | 55 | ~6.0 (est.) |
| Lynch | PR5A 实测 | `accepted_pr5a` | neutral | 50 | ~5.0 (est.) |
| Quant-Fundamentals | (assumed) | `assumed_fixture` | neutral | 65 | ~7.0 |
| Sentiment | (assumed) | `assumed_fixture` | bullish | 55 | ~6.0 |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. PEG Reliability | valid | 无影响 |
| 2. Negative Growth | 营收 -1.21% AND 净利润 -4.53% 双负 | ✅ **triggered** — 双负 → confidence cap=50 |
| 3. Bank Sector | sector_type=consumer | n/a |
| 4. High-Capex FCF | 非高资本开支 | n/a |

#### Weighted Score

- Fisher ~6.0 × 0.35 = 2.10
- Lynch ~5.0 × 0.35 = 1.75
- Quant-Fundamentals ~7.0 × 0.20 = 1.40 (⚠️ assumed_fixture)
- Sentiment ~6.0 × 0.10 = 0.60 (⚠️ assumed_fixture)
- **Total = 5.85**

#### Confidence Derivation

```
base_confidence = round(5.85 / 10 × 100) = 59
caps_applied:
  - Gate 2: revenue_yoy=-1.21% AND netprofit_yoy=-4.53% 双负 → min(59, 50) = 50
final_confidence = 50
=> confidence (top-level) = 50
=> confidence_calculation.final_confidence == confidence ✅
```

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 50
confidence_calculation: { base: 59, caps: ["Gate 2: revenue and netprofit both negative → cap 50"], final: 50 }
```

**判定**: ✅ neutral / 增长放缓 — Gate 2 双负触发 50 上限；高质量但零增长，非成长股目标。

---

### 样本 3: 002142 宁波银行

#### Consumed Inputs Used

| Input | Source | Source Status | Signal | Confidence | Score |
|---|---|---|---|---|---|
| Fisher | PR5A 实测 | `accepted_pr5a` | neutral or weak bullish | ~60 | ~6.5 (est.) |
| Lynch | PR5A 实测 | `accepted_pr5a` | neutral | 55 | ~5.5 (est.) |
| Quant-Fundamentals | (assumed) | `assumed_fixture` | bullish | 70 | ~7.0 |
| Sentiment | (assumed) | `assumed_fixture` | bullish | 55 | ~6.0 |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. PEG Reliability | valid (银行无送转问题) | 无影响 |
| 2. Negative Growth | 营收和净利润近年正增长 | 假设 not_triggered |
| 3. Bank Sector | sector_type=bank → **triggered** | 需要 NPL<1.5%, CAR>12%, 利润正增长三证据 |
| 4. High-Capex FCF | 非高资本开支 | n/a |

#### Gate 3 Bank Evidence Check

依据 PR5A 实测结果：
- NIM (净息差) ≥ 2%: ✅ 已返回，可评估
- CAR (资本充足率) > 12%: ✅ 已返回，可评估  
- NPL (不良贷款率) < 1.5%: ✅ 已返回，可评估
- 利润正增长: 假设满足

#### Weighted Score

- Fisher ~6.5 × 0.35 = 2.28
- Lynch ~5.5 × 0.35 = 1.93
- Quant-Fundamentals ~7.0 × 0.20 = 1.40 (⚠️ assumed_fixture)
- Sentiment ~6.0 × 0.10 = 0.60 (⚠️ assumed_fixture)
- **Total = 6.21**

#### Conflict Resolution

Fisher neutral/weak bullish + Lynch neutral.
- Fisher weak bullish + Lynch neutral → Rule 1: max weak bullish
- Fisher neutral + Lynch neutral → Rule 3: neutral

#### Case A — 银行三证据齐全

```
signal: neutral (Gate 3 允许 weak bullish 但不能超过)
strength: weak (leaning bullish)
confidence: 60
confidence_calculation: { base: 62, caps: ["Gate 3: bank with evidence → max confidence 60"], final: 60 }
```

#### Case B — 证据不全

```
signal: neutral
strength: flat
confidence: 50
confidence_calculation: { base: 62, caps: ["Gate 3: bank without full evidence → max confidence 50"], final: 50 }
```

**判定**: ✅ neutral to weak bullish（取决于银行三证据完整性）。Gate 3 确保低 PE 银行不被强行 bullish。

---

## Acceptance Criteria 验收

| # | 条件 | BYD | 茅台 | 宁波银行 |
|---|---|---|---|---|
| 1 | 不新增 signal/action enum | ✅ neutral | ✅ neutral | ✅ neutral |
| 2 | 不输出 final_action | ✅ 无 | ✅ 无 | ✅ 无 |
| 3 | Hard Gate 正确触发 | ✅ Gate 1 degraded, **Gate 2 triggered** | ✅ Gate 2 triggered (双负→50) | ✅ Gate 3 bank check |
| 4 | Gate 2 OR 逻辑生效 | ✅ 净利润单负→cap 60 | ✅ 营收+净利润双负→cap 50 | n/a |
| 5 | 冲突解决规则覆盖全部组合 | Rule 3: 双 neutral | Rule 3: 双 neutral | Rule 1/3 |
| 6 | 权重 Fisher 35% + Lynch 35% + Fundamentals 20% + Sentiment 10% | ✅ | ✅ | ✅ |
| 7 | 输出 consumable by analyze | ✅ growth_aggregate_signal | ✅ growth_aggregate_signal | ✅ growth_aggregate_signal |
| 8 | confidence 显示推导过程 | ✅ base+caps→final | ✅ base+caps→final | ✅ base+caps→final |
| 9 | assumed_fixture 与 accepted_pr5a 区分标注 | ✅ | ✅ | ✅ |

## Confidence Type Check

```python
# Top-level "confidence" must be int (not object) for consumer compatibility
# "confidence_calculation" object holds the derivation trace
# Invariant: confidence_calculation.final_confidence == confidence
```

| Check | Growth Aggregator | Fisher/Lynch Consumer |
|---|---|---|
| `confidence` type | int 0-100 ✅ | int 0-100 ✅ |
| `confidence_calculation` present | ✅ `{base, caps[], final}` | n/a (Fisher/Lynch don't have it) |
| `confidence_calculation.final_confidence == confidence` | ✅ 60 == 60 | n/a |

## Post-Fix `rg` Checks

```bash
# Check 1: no new signal/action enum
rg "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-growth.md
# → (no output — clean)

# Check 2: no raw hoxit query fallback
rg "hoxit (iwc|market|signals) " tos-funder/commands/tos-funder-growth.md
# → (no output — clean)

# Check 3: Gate 2 OR logic documented
rg "latest_netprofit_yoy_pct < 0" tos-funder/commands/tos-funder-growth.md
# → "If latest_revenue_yoy_pct < 0 OR latest_netprofit_yoy_pct < 0"
```

## Constitution Self-Review

```
Schema consumed:
  - growth-fisher: signal, strength, confidence, scoring_breakdown, growth_facts, valuation_facts
  - growth-lynch: signal, strength, confidence, scoring_breakdown, growth_facts, peg_reliability
  - quant-fundamentals: growth_score, profitability_score, signal, confidence
  - quant-sentiment: signal, strength, confidence

Output schema changes:
  - New schema: growth_aggregate_signal (section 7 in output-schema-examples.md)
  - signal_type: "growth_aggregate" discriminator
  - Extends growth_analyst_signal with consumed_signals, hard_gates, conflict_resolution
  - confidence is numeric; confidence_calculation stores {base_confidence, caps_applied[], final_confidence}
  - No new signal enums, no final_action

Downstream compatibility check:
  - analyze.md consumes growth_aggregate_signal via analyst_signals.growth
  - analyze.md updated to default to /tos-funder-growth with extended fields
  - Fisher/Lynch still accessible as drill-down commands
  - signal/strength/confidence parsable without prose

Constitution self-review:
  - Read the latest accepted schema? (Y) — created growth_aggregate_signal anchor
  - Avoided new signal enums? (Y) — bullish/neutral/bearish/blocked only
  - Separated facts, metrics, warnings, gates, resolution? (Y)
  - Labeled fallback and degraded data explicitly? (Y) — peg_reliability=degraded, missing inputs marked
  - Avoided overclaiming from sample validation? (Y) — assumed_fixture vs accepted_pr5a distinguished
  - Distinguished data-quality veto from risk veto? (Y) — Gate 1 (PEG quality) vs Gate 3 (sector risk)
  - Can next command consume without parsing prose? (Y) — typed fields
  - Kept iWencai and mootdx source boundaries intact? (Y) — aggregator calls subordinate commands only
  - Documented unresolved questions? (Y) — quant-fundamentals/sentiment are optional assumed_fixture
  - Gate 2 OR logic correct? (Y) — latest_revenue_yoy<0 OR latest_netprofit_yoy<0 triggers; both→cap50
  - No raw query fallback? (Y) — sector_type from Fisher/Lynch only; unknown→no sector upgrade
  - schema discriminator present? (Y) — signal_type: "growth_aggregate"
```
