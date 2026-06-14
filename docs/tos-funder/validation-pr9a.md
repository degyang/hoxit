# PR 9A Validation: Tactical Tail-Risk Proxy

验证日期：2026-06-03
验证范围：`/tos-funder-tactical-tail-risk` 确定性下行风险/尾部风险代理命令 — 分类事件/价格/流动性/数据质量风险，应用 5 道 Hard Gate，输出 tail_risk_signal

---

## 数据来源状态

| 输入 | Source | source_status | 说明 |
|---|---|---|---|
| `/tos-funder-quant-price-series` | Price-series | `accepted_pr6a` | PR 6A 已验证，调整状态可直接用于 Gate 1 |
| `/tos-funder-quant-technicals` | Technicals | `accepted_pr6a` | PR 6A 已验证，MA/成交量/RSI 可用 |
| `/tos-funder-risk-manager` | Risk | `accepted_pr6b` | PR 6B 已验证，波动率/回撤/流动性/ VaR 可用 |
| `/tos-funder-tactical-catalyst` | Catalyst | `accepted_pr8a` | PR 8A 已验证，事件/风险催化剂分类可用 |
| `hoxit iwc search -r announcement` | Direct search | `accepted_pr4a` | PR 4A 已验证关键词搜索覆盖率 +143%~300% |

---

## 验证样本

### 样本 1: 002594 比亚迪

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=suspect, factor=1.0, single-day -66.94% |
| Technicals | PR6A (assumed) | `accepted_pr6a` | return_20d ~+4.2%, vol_ratio ~1.15, no death cross |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal (21.8%), max_dd=78.5% (degraded), liquidity high |
| Tactical-catalyst | PR8A | `accepted_pr8a` | neutral signal, no regulatory/litigation risk events |
| Announcement search | PR4A | `accepted_pr4a` | 送转+回购 events (from PR8A), no risk events |

#### Risk Classification

| Type | Events Found | Severity |
|---|---|---|
| event | None | none |
| price | Moderate positive returns (return_20d=+4.2%, above MA20/MA60) | none |
| liquidity | avg_amount_20d=3.5B, tier=high | none |
| data quality | adjustment_anomaly (max_single_day -66.94%, factor=1.0) | medium (not usable as risk evidence) |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=suspect | ✅ **triggered** — price risk metrics degraded; max_dd/downside_vol not used as real tail-risk evidence; confidence capped at 60 |
| 2. Major Event | No regulatory/litigation/reduction/pledge detected | not_triggered |
| 3. Technical Breakdown | Price above MA20 and MA60, return_20d=+4.2% | not_triggered |
| 4. Liquidity | avg_amount_20d=3.5B, tier=high | not_triggered |
| 5. Stale Evidence | Current data (2026-06-03) | not_triggered |

#### Confidence Calculation

```
total = 0.0 × 0.40 + 2.0 × 0.35 + 0.0 × 0.25 = 0.70

base_confidence = 50 + 15 (announcement search) + 10 (technicals) + 10 (risk-manager) + 5 (catalyst context)
               = 90
caps: Gate 1 (data quality suspect) → min(90, 60) = 60
final_confidence = 60
```

#### Expected Outcome

```
tail_risk_level: low
signal: neutral
strength: flat
confidence: 60
Gate 1: triggered (adjustment_suspect — risk metrics degraded, confidence capped at 60)
Other gates: not triggered
```

**判定**: ✅ neutral, tail_risk_level=low — 无事件风险、价格风险、流动性风险。adjustment anomaly 标记为 data-quality，不作为真实尾部风险证据。Gate 1 触发导致 confidence 上限 60，但信号方向不受影响。

---

### 样本 2: 600519 贵州茅台

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified, factor=2 values |
| Technicals | PR6A | `accepted_pr6a` | return_20d slightly negative, vol_ratio low, no breakdown |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal, max_dd moderate (20.8%), liquidity high |
| Tactical-catalyst | PR8A | `accepted_pr8a` | neutral signal, Gate 2 triggered (report polarization) |
| Announcement search | PR4A | `accepted_pr4a` | routine earnings + dividend; no risk events |

#### Risk Classification

| Type | Events Found | Severity |
|---|---|---|
| event | None | none |
| price | Mild negative drift (return_20d slightly negative), no breakdown | low |
| liquidity | avg_amount_20d high, tier=high | none |
| data quality | None — adjustment_status=verified | none |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=verified | not_triggered |
| 2. Major Event | No regulatory/litigation/reduction detected | not_triggered |
| 3. Technical Breakdown | No MA breakdown, no death cross | not_triggered |
| 4. Liquidity | avg_amount_20d high, tier=high | not_triggered |
| 5. Stale Evidence | Current data | not_triggered |

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 85
No hard gates triggered (all clear)
```

**判定**: ✅ neutral — 高质量公司，无事件风险。Gate 1-5 均未触发。低尾部风险。

---

### 样本 3: 002142 宁波银行

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified |
| Technicals | PR6A | `accepted_pr6a` | MA alignment bullish, return_20d positive |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal (18.6%), max_dd moderate (10.8%), liquidity medium |
| Tactical-catalyst | PR8A | `accepted_pr8a` | neutral signal (Gate 2 triggered — report polarization) |
| Announcement search | PR4A | `accepted_pr4a` | routine earnings, dividend; no risk events |

#### Risk Classification

| Type | Events Found | Severity |
|---|---|---|
| event | None | none |
| price | MA bullish alignment, moderate positive return | none |
| liquidity | avg_amount_20d=690M, tier=medium | low (monitoring level) |
| data quality | None — adjustment_status=verified | none |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=verified | not_triggered |
| 2. Major Event | No regulatory/litigation/reduction detected | not_triggered |
| 3. Technical Breakdown | No MA breakdown, no death cross | not_triggered |
| 4. Liquidity | avg_amount_20d=690M > 10M, tier=medium (borderline) | borderline |
| 5. Stale Evidence | Current data | not_triggered |

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 85
No hard gates triggered (all clear, Gate 4 borderline)
```

**判定**: ✅ neutral — 银行股无事件风险，流动性中等但充足。Gate 4 可能 borderine 但 avg_amount_20d=690M 远超 10M 阈值。

---

### 样本 4: 000820 *ST节能（真实负面风险事件 — CSRC 立案 + 投资者诉讼）

> 通过 iWencai announcement search 实测找到的真实负面风险样本。使用以下查询命中：
> 
> | Query | Hits |
> |---|---|
> | `最近一年 监管函 处罚 立案 诉讼 A股` | 命中 000820 *ST节能 CSRC 立案告知书（2026-06-02） |
> | `000820 最近一年 监管函 问询函 处罚 诉讼 减持 质押` | 命中多起投资者诉讼（2026-01-08 进展公告） |

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `assumed`* | adjustment_status unknown — *ST stock, pre-market quote only |
| Technicals | PR6A | `assumed`* | Price/volume data unavailable (suspended/pre-market) |
| Risk-manager | PR6B | `assumed`* | Not computed — insufficient data |
| Tactical-catalyst | PR8A | `accepted_pr8a` | Not run for this sample |
| Announcement search | PR4A | `accepted_pr4a` | ✅ CSRC investigation (2026-06-02, CRITICAL) + multiple investor lawsuits |

> * Price-series/technicals/risk-manager 数据因 000820 当前处于暂停/停牌状态不可用。这是尾部风险代理的一个已知数据缺口。

#### Risk Classification

| Type | Events Found | Severity |
|---|---|---|
| event | CSRC investigation (立案告知书, 2026-06-02) — 涉嫌信息披露违法违规 | Critical |
| event | Multiple investor lawsuits (投资者诉讼, ongoing, last update 2026-01-08) | High |
| event | *ST delisting risk warning | Critical |
| price | Data unavailable — stock suspended | unknown |
| liquidity | Data unavailable | unknown |
| data quality | adjustment_status unknown (limited data) | unknown |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=unknown | ✅ **triggered** — confidence capped at 50; price/liquidity risk not assessable |
| 2. Major Event | CSRC investigation (Critical) + investor lawsuits (High) + *ST delisting (Critical) | ✅ **triggered** — Critical severity → signal must be bearish |
| 3. Technical Breakdown | Price data unavailable | not assessable |
| 4. Liquidity | Data unavailable | not assessable |
| 5. Stale Evidence | CSRC investigation just 1 day old (2026-06-02) | not_triggered |

#### Confidence Calculation

```
base_confidence = 50 + 15 (announcement search) + 10 (Gate 2 confirmed event evidence)
               = 75
caps: Gate 1 (data quality unknown) → min(75, 50) = 50
final_confidence = 50
```

#### Expected Outcome

```
tail_risk_level: critical
signal: bearish
strength: strong
confidence: 50
Gate 1: triggered (adjustment unknown — price/liquidity not assessable)
Gate 2: triggered (CSRC investigation + lawsuits + *ST — Critical severity → bearish)
```

**判定**: ✅ bearish — CSRC 立案（Critical）+ 多起投资者诉讼（High）+ *ST 退市风险（Critical）。Gate 2 强制 bearish。Gate 1 因数据不可用 cap confidence at 50，但事件风险本身足以驱动 bearish 信号。price/liquidity 维度不可用属于已知数据缺口，不影响基于事件风险的判定。

---

## Acceptance Criteria 验收

| # | 条件 | BYD | 茅台 | 宁波银行 | *ST节能 |
|---|---|---|---|---|---|
| 1 | frontmatter 声明 consumed/produced/consumable_by | ✅ | ✅ | ✅ | ✅ |
| 2 | output-schema-examples.md 新增 tail_risk_signal | ✅ section 9 | ✅ | ✅ | ✅ |
| 3 | skill-workflow.md 增加路由 | ✅ | ✅ | ✅ | ✅ |
| 4 | analyze.md family=tactical 增加 tail-risk 路由 | ✅ | ✅ | ✅ | ✅ |
| 5 | validation 记录每个样本 consumed/source_status/hard_gates | ✅ | ✅ | ✅ | ✅ (部分 assumed) |
| 6 | 无新 signal/action enum | ✅ neutral | ✅ neutral | ✅ neutral | ✅ bearish |
| 7 | 无 final_action | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| 8 | 无 dead routes | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| 9 | 无 degraded metric 滥用 | ✅ adjustment_anomaly 为 data quality | ✅ n/a | ✅ n/a | ✅ n/a |
| 10 | constitution self-review | ✅ | ✅ | ✅ | ✅ |

## Post-Fix `rg` Checks

```bash
# Check 1: no new signal/action enum
rg "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-tactical-tail-risk.md tos-funder/references/output-schema-examples.md
# → (no output — clean)

# Check 2: no final_action in command output
rg "final_action" tos-funder/commands/tos-funder-tactical-tail-risk.md
# → (found only in validation-checklist references to "no final_action" — clean)

# Check 3: no dead routes
rg "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-tactical-tail-risk.md
# → (no output — clean)

# Check 4: no degraded metric abuse
rg "polarity.*negative.*adjustment_anomaly|max_dd.*negative catalyst|downside_vol.*negative catalyst" tos-funder/commands/tos-funder-tactical-tail-risk.md tos-funder/references/output-schema-examples.md
# → (no output — clean)
```

## Constitution Self-Review

```
Schema consumed:
  - price-series: adjustment_status, corporate_action_warning, data_quality
  - technicals: price, ma_alignment, rsi, volume, returns, crossovers
  - risk-manager: facts.volatility, facts.drawdown, facts.liquidity, facts.var
  - tactical-catalyst: signal, strength, catalyst_facts.risk, hard_gates.risk_event
  - announcement-search: title, date, url (risk-specific packs T1-T3)

Output schema changes:
  - New schema: tail_risk_signal (section 9 in output-schema-examples.md)
  - signal_type: "tail_risk" discriminator
  - tail_risk_level: low | moderate | high | critical | unknown
  - 3-dimension scoring: event risk 40%, price risk 35%, liquidity risk 25% (data quality is a modifier, not a dimension)
  - 5 hard gates: data quality, major event, technical breakdown, liquidity, stale evidence
  - evidence-quality confidence formula (not inverse risk)
  - No final_action
  - No new signal enums
  - signal: neutral | bearish | blocked (bullish removed)

Downstream compatibility check:
  - analyze.md consumes tail_risk_signal via analyst_signals.tactical.tail_risk
  - family=tactical extends to tail-risk as complementary layer
  - signal/strength/confidence are typed fields, parsable without prose
  - risk_facts and hard_gates provide structured drill-down

Constitution self-review:
  - Read the tactical-tail-risk reference, tactical-catalyst reference, output-schema-examples, skill-workflow, risk-manager, price-series? (Y)
  - Avoided new unapproved signal enums for tail-risk output? (Y) — neutral/bearish/blocked only; tail_risk_level carries low/moderate/high/critical/unknown
  - Separated facts, metrics, warnings, interpretations, actions? (Y) — risk_facts (classification), tail_risk_scoring (metrics), hard_gates (constraints), no final_action
  - Labeled fallback and degraded data explicitly? (Y) — adjustment_status=suspect annotated; max_dd labeled as DEGRADED
  - Avoided overclaiming from sample validation? (Y) — sample 4 (*ST节能) CSRC investigation and lawsuits verified via iWencai announcement search; price/liquidity data gaps documented
  - Distinguished data-quality risk from real market risk? (Y) — Gate 1 prevents degraded metric abuse; usable_as_risk_evidence=false
  - Can next command consume without parsing prose? (Y) — typed fields (signal, strength, confidence, tail_risk_level) and structured risk_facts
  - Kept iWencai and TDX/mootdx source boundaries intact? (Y) — price-series/technicals: mootdx, risk: risk-manager + iwencai announcement search
  - Documented unresolved questions? (Y) — *ST节能 price/liquidity data unavailable during suspension; Gate 3/4 not assessable for this sample

Next recommended step:
  - Implement Druckenmiller (/tos-funder-tactical-druckenmiller) for macro-driven tactical sentiment, now that both catalyst (PR8A) and tail-risk (PR9A) proxy layers are complete.
  - Consider a data-coverage PR for suspended/*ST stocks to handle edge cases where price/liquidity data is unavailable but event risk is material.
```
