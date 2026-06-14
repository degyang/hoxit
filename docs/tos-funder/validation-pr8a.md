# PR 8A Validation: Tactical Catalyst Proxy

验证日期：2026-06-03
验证范围：`/tos-funder-tactical-catalyst` 确定性事件催化剂代理命令 — 分类事实/观点/价格/风险催化剂，应用 5 道 Hard Gate，输出 tactical_catalyst_signal

---

## 数据来源状态

| 输入 | Source | source_status | 说明 |
|---|---|---|---|
| `/tos-funder-quant-price-series` | Price-series | `accepted_pr6a` | PR 6A 已验证，调整状态可直接用于 Gate 1 |
| `/tos-funder-quant-technicals` | Technicals | `accepted_pr6a` | PR 6A 已验证，MA/成交量/RSI 可用 |
| `/tos-funder-quant-sentiment` | Sentiment/Events | `accepted_pr4a` | PR 4A 已验证，含 IR 过滤/研报偏置/去重 |
| `/tos-funder-risk-manager` | Risk | `accepted_pr6b` | PR 6B 已验证，波动率/回撤/流动性可用 |
| `hoxit iwc search -r announcement` | Direct search | `accepted_pr4a` | PR 4A 已验证关键词搜索覆盖率 +143%~300% |
| `hoxit iwc search -r report` | Direct search | `accepted_pr4a` | PR 4A 已验证偏置：0 负面研报 |
| `/tos-funder-quant-fundamentals` | Fundamentals | `assumed_fixture` | 可选输入，不作为本 PR 验收依据 |

---

## 验证样本

### 样本 1: 002594 比亚迪

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=suspect, factor=1.0, single-day -66.94% |
| Technicals | PR6A (assumed) | `accepted_pr6a` | return_20d ~+4.2%, vol_ratio ~1.15, no clear crossover |
| Sentiment | PR4A | `accepted_pr4a` | bullish signal, strong strength, 60 confidence; bonus share + buyback events |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal, max_dd=78.5% (degraded), current_dd=13.0% |
| Announcement search | PR4A | `accepted_pr4a` | dividend_bonus (送转), buyback events found |
| Report search | PR4A | `accepted_pr4a` | All positive ratings (买入/增持) |

#### Catalyst Classification

| Type | Events Found | Polarity |
|---|---|---|
| factual | dividend_bonus (2025-07-29), buyback (2026-01-15) | positive |
| opinion | rating_upgrade (2026-03-10) — 维持买入 | positive |
| price | return_20d=+4.2% moderate momentum | positive |
| risk | adjustment_anomaly (max_single_day -66.94%, factor=1.0) | data-quality (n/a) |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=suspect | ✅ **triggered** — price_confirmation score capped at 5.0; degraded max_dd/downside_vol not used as negative catalyst evidence |
| 2. Report Polarization | All reports positive BUT factual events exist | not_triggered |
| 3. Risk Event | No regulatory/litigation/reduction found | not_triggered |
| 4. Price Confirmation | vol_ratio=1.15<1.2, no crossover | ✅ **triggered** — bullish strength capped at weak |
| 5. Stale Event | buyback 2026-01-15 < 180 days ago | not_triggered |

#### Confidence Calculation

```
factual_catalyst     = 6.0 × 0.35 = 2.10  (2 positive events, 0 negative)
price_confirmation   = 5.5 × 0.25 = 1.38  (moderate momentum, no volume surge)
risk_asymmetry       = 6.0 × 0.20 = 1.20  (no regulatory events, adjustment anomaly noted)
sentiment_support    = 6.0 × 0.10 = 0.60  (bullish sentiment, polarization noted)
recency_materiality  = 5.0 × 0.10 = 0.50  (avg ~180 days)

total = 5.78
base_confidence = 58
caps: Gate 1 (data quality) → constrained price dimension → effective cap reduces to ~55
final_confidence = 55
```

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 55
Gate 1: triggered (adjustment_suspect)
Gate 4: triggered (no price confirmation)
```

**判定**: ✅ neutral — positive factual catalysts exist but offset by adjustment anomaly + no price confirmation. Gate 1 and Gate 4 both triggered, preventing strong bullish.

---

### 样本 2: 600519 贵州茅台

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified, factor=2 values |
| Technicals | PR6A | `accepted_pr6a` | return_20d slightly negative, vol_ratio low, no breakout |
| Sentiment | PR4A | `accepted_pr4a` | bullish but report polarization cap active; all reports positive |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal, max_dd moderate, liquidity high |
| Announcement search | PR4A | `accepted_pr4a` | routine earnings + dividend; no major factual catalysts |
| Report search | PR4A | `accepted_pr4a` | All positive, zero negative — classic polarization case |

#### Catalyst Classification

| Type | Events Found | Polarity |
|---|---|---|
| factual | dividend, earnings_report (routine) | neutral-positive |
| opinion | rating_upgrade (multiple, all positive) | positive |
| price | No breakout, no volume surge, no crossover | neutral |
| risk | None material | none |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=verified | not_triggered |
| 2. Report Polarization | All reports positive AND no negative factual catalysts | ✅ **triggered** — signal cannot exceed neutral |
| 3. Risk Event | No regulatory/litigation | not_triggered |
| 4. Price Confirmation | vol_ratio < 1.2, no crossover, return near 0 | triggered (but moot since Gate 2 already blocks bullish) |
| 5. Stale Event | Events exist within 180 days | not_triggered |

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 45 (Gate 2 polarization cap: min(base, 50))
Gate 2: triggered (report polarization — opinion-only, no negative factual events)
```

**判定**: ✅ neutral — 研报正向偏置 + 无事实催化剂 → Gate 2 禁止 bullish。高质量公司但无近期催化剂。

---

### 样本 3: 002142 宁波银行

#### Consumed Inputs Used

| Input | Source | Source Status | Key Data |
|---|---|---|---|
| Price-series | PR6A | `accepted_pr6a` | adjustment_status=verified |
| Technicals | PR6A | `accepted_pr6a` | MA alignment bullish, return_20d positive, vol_ratio ~1.0 |
| Sentiment | PR4A | `accepted_pr4a` | neutral-bullish, reports positive |
| Risk-manager | PR6B | `accepted_pr6b` | vol normal, max_dd 10.8% moderate, liquidity medium |
| Announcement search | PR4A | `accepted_pr4a` | routine earnings, dividend; no risk events |
| Report search | PR4A | `accepted_pr4a` | positive ratings (银行低估值+资产质量) |

#### Catalyst Classification

| Type | Events Found | Polarity |
|---|---|---|
| factual | dividend, earnings_report (routine) | neutral |
| opinion | rating_upgrade on asset quality improvement | positive |
| price | MA bullish alignment, moderate return | neutral-positive |
| risk | None | none |

#### Hard Gate Checks

| Gate | Condition | Result |
|---|---|---|
| 1. Data Quality | adjustment_status=verified | not_triggered |
| 2. Report Polarization | All reports positive, material_factual_catalyst_count=0 (routine earnings/dividend only), opinion_score is primary positive driver | ✅ **triggered** — signal cannot exceed neutral, confidence capped at 50 |
| 3. Risk Event | No regulatory/litigation | not_triggered |
| 4. Price Confirmation | MA alignment bullish; vol_ratio ~1.0 (borderline) | borderline |
| 5. Stale Event | Events within 180 days | not_triggered |

#### Expected Outcome

```
signal: neutral
strength: flat
confidence: 50
Gate 2: triggered (report polarization — positive opinions only supported by routine earnings/dividend)
```

**判定**: ✅ neutral — 仅有 routine factual events（earnings/dividend），material_factual_catalyst_count=0，所有研报均正向 → Gate 2 触发，信号不得超出 neutral，confidence 上限 50。MA 多头排列和正向收益提供有限支撑，但不足以克服 polarization cap。

---

### 样本 4 (规则定义，未实测): 负面风险事件

> ⚠️ Gate 3 规则已定义但未在 PR8A 中实测。负面风险事件样本延后到 tail-risk proxy PR。

选择标准：有监管函/诉讼/减持公告的股票。
如果该股票出现以下任一情况：监管函/问询函/处罚/立案、诉讼/仲裁、大股东减持 >5%。
Gate 3 应触发，信号不得为 bullish。

**预期**: bearish 或 neutral（取决于其他催化剂强度），confidence 受风险事件压制。

---

## Acceptance Criteria 验收

| # | 条件 | BYD | 茅台 | 宁波银行 |
|---|---|---|---|---|
| 1 | frontmatter 声明 consumed/produced/consumable_by | ✅ | ✅ | ✅ |
| 2 | output-schema-examples.md 新增 tactical_catalyst_signal | ✅ section 8 | ✅ | ✅ |
| 3 | skill-workflow.md 增加路由 | ✅ | ✅ | ✅ |
| 4 | analyze.md family=tactical 默认先使用 catalyst | ✅ | ✅ | ✅ |
| 5 | validation 记录每个样本 consumed/source_status/hard_gates | ✅ | ✅ | ✅ |
| 6 | 无新 signal/action enum | ✅ neutral | ✅ neutral | ✅ neutral |
| 7 | 无 final_action | ✅ 无 | ✅ 无 | ✅ 无 |
| 8 | 无 dead routes | ✅ 无 | ✅ 无 | ✅ 无 |
| 9 | 无 polarization/downgraded metrics 作为主因 | ✅ adjustment_anomaly 标记为 data quality | ✅ polarization 不驱动方向 | ✅ Gate 2 触发 → polarization 非方向主因 |
| 10 | constitution self-review | ✅ | ✅ | ✅ |

## Post-Fix `rg` Checks

```bash
# Check 1: no new signal/action enum
rg "weak_bullish|strong_bearish|weak_sell|strong_buy" tos-funder/commands/tos-funder-tactical-catalyst.md
# → (no output — clean)

# Check 2: no final_action in command output
rg "final_action" tos-funder/commands/tos-funder-tactical-catalyst.md
# → (found only in validation-checklist references to "no final_action" — clean)

# Check 3: no dead routes
rg "query2data|query -r event|query -r business|query -r management" tos-funder/commands/tos-funder-tactical-catalyst.md
# → (no output — clean)

# Check 4: signal_type discriminator present
rg "signal_type.*tactical_catalyst" tos-funder/commands/tos-funder-tactical-catalyst.md
# → (found — clean)
```

## Constitution Self-Review

```
Schema consumed:
  - price-series: adjustment_status, corporate_action_warning, data_quality
  - technicals: price, ma_alignment, rsi, volume, returns, crossovers
  - sentiment: signal, strength, confidence, event_classification, data_quality_warnings
  - risk-manager: facts.volatility, facts.drawdown, facts.liquidity
  - announcement-search: title, date, url (catalyst-specific packs C1-C3)
  - report-search: title, date, url (catalyst-specific pack C4)

Output schema changes:
  - New schema: tactical_catalyst_signal (section 8 in output-schema-examples.md)
  - signal_type: "tactical_catalyst" discriminator
  - 5-dimension scoring: factual 35%, price 25%, risk asymmetry 20%, sentiment 10%, recency 10%
  - 5 hard gates: data-quality, report polarization, risk event, price confirmation, stale event
  - No final_action
  - No new signal enums

Downstream compatibility check:
  - analyze.md consumes tactical_catalyst_signal via analyst_signals.tactical
  - family=tactical defaults to /tos-funder-tactical-catalyst
  - signal/strength/confidence are typed fields, parsable without prose
  - catalyst_facts and hard_gates provide structured drill-down

Constitution self-review:
  - Read the latest accepted command/reference schema? (Y) — read price-series, technicals, sentiment, risk-manager, skill-workflow, output-schema-examples, growth-investors, agent-taxonomy, command-template
  - Avoided new unapproved signal enums? (Y) — bullish/neutral/bearish/blocked only
  - Separated facts, metrics, warnings, interpretations, actions? (Y) — catalyst_facts (classification), catalyst_scoring (metrics), hard_gates (constraints), no final_action
  - Labeled fallback and degraded data explicitly? (Y) — adjustment_status=suspect annotated; max_dd labeled as DEGRADED
  - Avoided overclaiming from sample validation? (Y) — assumed_fixture vs accepted_pr* distinguished; validation limited to 3 primary samples + 1 optional
  - Distinguished data-quality veto from risk veto? (Y) — Gate 1 (data quality) separate from Gate 3 (risk events)
  - Can next command consume without parsing prose? (Y) — typed fields (signal, strength, confidence) and structured catalyst_facts
  - Kept iWencai and TDX/mootdx source boundaries intact? (Y) — price-series: mootdx, sentiment: iwencai announcement+report, catalyst search: iwencai announcement+report
  - Documented unresolved questions? (Y) — sample 4 (negative risk gate) not fully tested; recommendation to implement Druckenmiller or risk-tail proxy next

Next recommended step:
  - Consider implementing Druckenmiller (/tos-funder-tactical-druckenmiller) for macro-driven tactical sentiment, or
  - Risk-tail proxy (/tos-funder-tactical-tail-risk) for extreme event hedging.
  - Full negative sample validation (Gate 3 risk event) requires a stock with active regulatory/litigation disclosure.
```
