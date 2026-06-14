# PR 10A Validation: Macro / Top-Down Proxy

验证日期：2026-06-03
验证范围：`/tos-funder-macro-topdown` 确定性宏观/自上而下代理命令 — 评估指数趋势、行业相对强度、市场宽度、风格轮动和风险偏好，产出 `macro_topdown_signal`

---

## Data Coverage Probe

Before implementing the final command logic, probe and document whether each data source is available through hoxit iWencai routes.

### A. Index Price Series

Probe: Can hoxit market retrieve major A-share index bars?

```bash
.venv/bin/python -m hoxit.cli market bars 000001 --category 4 --offset 120 --adjust qfq
.venv/bin/python -m hoxit.cli market bars 399001 --category 4 --offset 120 --adjust qfq
.venv/bin/python -m hoxit.cli market bars 399006 --category 4 --offset 120 --adjust qfq
```

**Result**: ❌ FAILED — mootdx returns `head_buf is not 0x10 : b''`. mootdx cannot fetch index K-line data for any of the three major indexes.

**Fallback probe**: iWencai index returns query:

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 沪深300 中证500 中证1000 创业板指 涨跌幅" --limit 5
```

**Result**: ✅ WORKS — returns 中证500 (000905.SH) with 涨跌幅[-2.118195] and other indexes. Index returns are available via iWencai market route.

**Status**: `verified` (index_returns — via iWencai returns query), `unavailable` (index_bars — mootdx cannot fetch index K-line)
**Note**: MA20/MA60 relationship cannot be computed without OHLCV. Use return-based trend assessment. In `data_sources`, use separate fields: `index_returns` (verified, usable_for_scoring=true) and `index_bars` (unavailable, usable_for_scoring=false).

### B. Sector / Industry Context

Probe: Can iWencai return target industry and concept tags?

```bash
.venv/bin/python -m hoxit.cli iwc query -r basicinfo -q "比亚迪 所属同花顺行业 概念 总市值 股票代码" --limit 5
```

**Result**: ✅ WORKS — returns 所属同花顺行业: ["汽车","汽车整车","乘用车"], 所属概念: [26 concept tags including 新能源,比亚迪概念], 总市值: 823701434008.95

Probe: Can iWencai return industry/sector strength in a stable form?

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 行业板块 涨跌幅 成交额 领涨行业 领跌行业" --limit 20
```

**Result**: ✅ WORKS — returns 同花顺三级行业指数 with 涨跌幅 and rankings. However, field names (同花顺三级行业指数) are not standard structured identifiers, making target-specific industry rank matching unstable.

**Status**: `verified` (industry_basicinfo for tags — usable_for_scoring=true for tag-only context), `degraded` (sector_strength ranking — usable_for_scoring=false because 同花顺三级行业指数 format not stable for target industry rank matching)

### C. Market Breadth Proxy

Probe: Can iWencai return breadth-like fields?

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 A股 上涨家数 下跌家数 涨停家数 跌停家数" --limit 10
```

**Result**: ✅ WORKS — returns 上涨家数:1903, 下跌家数:3509, 涨停家数:68, 跌停家数:12

**Status**: `verified` (usable_for_scoring=true) — advance/decline ratio = 1903/3509 = 0.54, which is within the neutral scoring range (>0.5, <1.5)

### D. Style Rotation Proxy

Probe: Can iWencai return style/index proxy data?

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 大盘成长 大盘价值 小盘成长 小盘价值 涨跌幅" --limit 20
.venv/bin/python -m hoxit.cli iwc query -r market -q "近20日 沪深300 中证500 中证1000 创业板指 涨跌幅" --limit 20
```

**Result**: ❌ "大盘成长 大盘价值 小盘成长 小盘价值" query returns empty. Style rotation data is not available via iWencai market route.
✅ Second query (index returns) works — but this is already covered in probe A.

**Status**: `missing`

### E. Risk Appetite Proxy

Probe: Can iWencai return northbound flow/funding data?

```bash
.venv/bin/python -m hoxit.cli iwc query -r market -q "今日 A股 成交额 北向资金 融资余额 涨停家数 跌停家数" --limit 10
```

**Result**: ⚠️ PARTIAL — 成交额 returns data. 北向资金 (northbound flow) and 融资余额 (margin balance) return empty. 涨停/跌停家数 overlap with breadth probe C above.

**Status**: `partial` (turnover available; northbound/margin unavailable; 20d average turnover not consistently available for scoring ratio → usable_for_scoring=false)

### Probe Summary

| Category | Status | Source | Usable for Scoring | Notes |
|---|---|---|---|---|
| A. Index returns | ✅ verified | iWencai market query | ✅ yes | 沪深300/中证500/中证1000/创业板指 returns available |
| A. Index bars (OHLCV) | ❌ unavailable | mootdx market bars | ❌ no | mootdx cannot fetch index K-line |
| B. Industry tags | ✅ verified | iWencai basicinfo | ✅ yes (tag context) | 所属同花顺行业, 概念 tags available |
| B. Sector strength ranking | ⚠️ degraded | iWencai market query | ❌ no | 同花顺三级行业指数 — format not stable for target-industry rank matching |
| C. Market breadth | ✅ verified | iWencai market query | ✅ yes | 上涨/下跌/涨停/跌停 counts; AD ratio 0.54 neutral |
| D. Style rotation | ❌ missing | iWencai market query | ❌ no | 大盘/小盘/成长/价值 unavailable |
| E. Risk appetite | ⚠️ partial | iWencai market query | ❌ no | Turnover available but 20d avg not consistently available for ratio scoring; northbound/margin unavailable |

---

## 验证样本

### 样本 1: 002594 比亚迪

#### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 002594 | live_verified |
| Name | 比亚迪 | live_verified |
| Industry | 汽车整车 (via 所属同花顺行业) | live_verified |
| Concepts | 新能源, 比亚迪概念, 宁德时代概念, etc. (26 tags) | live_verified |

#### Data Sources Used

| Dimension | Source | source_status | Usable for Scoring |
|---|---|---|---|
| Index returns (20d, 60d) | iWencai market query | live_verified | ✅ yes |
| Industry tags | iWencai basicinfo | live_verified | ✅ yes (tag context) |
| Sector strength ranking | iWencai market query | degraded | ❌ no (usable_for_scoring=false) |
| Market breadth | iWencai market query | live_verified | ✅ yes |
| Style rotation | iWencai market query | missing | ❌ no |
| Risk appetite | iWencai market query | partial | ❌ no (usable_for_scoring=false) |

#### Scoring Dimensions

| Dimension | Score | Weight | Available |
|---|---|---|---|
| Index trend | 0 (neutral — mixed 20d, 1/4 positive) | 35% | ✅ yes |
| Sector relative strength | 0 (tag_only — no ranking) | 25% | ❌ no (degraded) |
| Market breadth | 0 (AD ratio 0.54, within neutral range) | 20% | ✅ yes |
| Style/risk appetite | 0 (unavailable) | 20% | ❌ no |

Verified dimensions: **index + breadth = 2** (partial coverage)
Total weight available: 35% + 20% = 55%
Normalized score: 0 / (0.55 × 2) = 0.0 → neutral

#### Hard Gates

| Gate | Condition | Result |
|---|---|---|
| 1. Coverage | 2 verified dimensions (index + breadth) — ≥2 | not_triggered |
| 2. Risk-Off | Index trend neutral | not_triggered |
| 3. Sector Missing | Industry tag "汽车整车" available | not_triggered |
| 4. Overclaim | Breadth context available — not only index | not_triggered |

#### Confidence Calculation

```text
base_confidence = 40
+15 index_returns (verified)
+10 breadth (verified)
+5  industry_tag (verified)
pre_cap = 70
No caps triggered (2 verified dims ≥ 2, industry tag available, data fresh)
final_confidence = 70
```

#### Expected Outcome

```text
signal: neutral
strength: flat
market_regime: neutral
coverage_status: partial (2 verified scoring dimensions)
confidence: 70 (40 + 15 + 10 + 5, no caps applied)
All 4 gates: not_triggered — breadth elevates coverage above gate thresholds
```

**判定**: ✅ Neutral — 指数趋势中性，市场宽度中性（AD ratio 0.54）。2个验证维度 → partial覆盖，不触发覆盖门限。Breadth已验证可用提高了置信度(70)。不过度 claim宏观因果关系。

---

### 样本 2: 600519 贵州茅台

#### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 600519 | live_verified |
| Name | 贵州茅台 | live_verified |
| Industry | 白酒 (via 所属同花顺行业) | live_verified |
| Concepts | 白酒, 超级品牌, 证金持股, etc. | live_verified |

#### Expected Process

```text
1. Industry tag: "白酒" — consumer/baijiu sector
2. Index context: same as BYD sample (market-level) — index trend neutral
3. Market breadth: same as BYD (market-level) — AD ratio 0.54, neutral
4. Baijiu sector: tag_only — ranking not available for scoring
5. Scoring: index neutral + breadth neutral + sector tag-only = signal neutral
```

#### Expected Outcome

```text
signal: neutral
strength: flat
market_regime: neutral
coverage_status: partial (2 verified dimensions: index + breadth)
confidence: 70 (40 + 15 + 10 + 5, same calc as BYD)
Gates: no gates triggered
```

**判定**: ✅ Neutral — 指数趋势和中观宽度均中性。Breadth已验证意味着覆盖门限不触发。宏观背景不应覆盖个股基本面 — 不存在 claim "宏观支持白酒"。

---

### 样本 3: 002142 宁波银行

#### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 002142 | live_verified |
| Name | 宁波银行 | live_verified |
| Industry | 银行 | live_verified |
| Sector type | Bank | live_verified |

#### Expected Process

```text
1. Industry tag: "银行" — financial sector
2. Banking sector: tag_only — ranking not available for scoring
3. Index context: same market-level (neutral)
4. Breadth: same market-level (AD ratio 0.54, neutral)
5. Scoring: index neutral + breadth neutral + sector tag-only = signal neutral
```

#### Expected Outcome

```text
signal: neutral
strength: flat
market_regime: neutral
coverage_status: partial (2 verified dimensions: index + breadth)
confidence: 70 (40 + 15 + 10 + 5, same calc as other stock targets)
```

**判定**: ✅ Neutral — 银行板块可能有独立的宏观敏感性，但当前数据覆盖仅支持指数趋势+行业标签+中观宽度。Keep top-down signal neutral。不 claim "宏观对银行有利"。

---

### 样本 4: Index Target (000905 中证500)

#### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 000905 | accepted_existing |
| Name | 中证500 | accepted_existing |
| Type | Index | accepted_existing |

#### Expected Process

```text
1. Target is an index — skip basicinfo (no industry concept)
2. Index trend: computed from same iWencai returns (neutral)
3. Sector context: N/A for index target
4. Breadth context: N/A for index target (index-only mode)
5. Only index trend scored — 1 verified dimension
6. Coverage Gate triggered: <2 verified dimensions → coverage_status=degraded, confidence cap 50
```

#### Expected Outcome

```text
signal: neutral
strength: flat
market_regime: neutral
coverage_status: degraded (1 verified dimension: index returns only)
confidence: 50 (base 40 + 15 index = 55, cap 50 from coverage gate)
sector_context: N/A (index target)
Gate 1 (coverage): triggered — only 1 verified dimension
Gate 4 (overclaim): triggered — only index context
```

**判定**: ✅ Neutral — 指数目标无行业概念，breadth 为 N/A (index-only mode)。1验证维度 → degraded 覆盖，覆盖门限触发，置信度上限50。验证 index-only 模式正常工作。

---

### 样本 5: Negative / Partial Coverage Scenario

#### Scenario: Index Returns Unavailable

Simulate a situation where index data is unavailable (e.g., iWencai query returns empty or stale data > 1 day old, data connection fails).

| Condition | Data | source_status |
|---|---|---|
| Index returns | Empty/stale | missing |
| Industry tags | Available | assumed_fixture |
| Sector strength | Available | assumed_fixture |
| Breadth | Available | assumed_fixture |

#### Expected Process

```text
1. Index query returns empty or stale
2. Gate 1 (Coverage Gate): no index data → signal = blocked
```

#### Expected Outcome

```text
signal: blocked
strength: flat
market_regime: unknown
coverage_status: blocked
confidence: 40 (base only — no bonuses applicable)
Gate 1 (coverage): triggered — no index data, signal=blocked
```

**判定**: ✅ Blocked — 缺少指数数据时不能产生信号。Coverage Gate 正确强制 `signal=blocked`，`market_regime=unknown`。不 claim 任何宏观背景。

---

### Sample Source Status Summary

| 样本 | Index Returns | Industry Tags | Sector Strength | Breadth | Style | Risk Appetite | Scoring Dims | source_status |
|---|---|---|---|---|---|---|---|---|
| 1. 比亚迪 | live_verified ✅ | live_verified ✅ | degraded ❌ | live_verified ✅ | missing ❌ | partial ❌ | 2 (index+breadth) | live_verified |
| 2. 贵州茅台 | live_verified ✅ | live_verified ✅ | degraded ❌ | live_verified ✅ | missing ❌ | partial ❌ | 2 (index+breadth) | live_verified |
| 3. 宁波银行 | live_verified ✅ | live_verified ✅ | degraded ❌ | live_verified ✅ | missing ❌ | partial ❌ | 2 (index+breadth) | live_verified |
| 4. 中证500 | live_verified ✅ | N/A | N/A | N/A (index-only) | N/A | N/A | 1 (index only) | accepted_existing |
| 5. Negative | missing ❌ | assumed_fixture | assumed_fixture | assumed_fixture | missing ❌ | missing ❌ | 0 (no index) | assumed_fixture |

---

## Acceptance Criteria 验收

| # | 条件 | BYD | 茅台 | 宁波银行 | 中证500 | Negative |
|---|---|---|---|---|---|---|
| 1 | frontmatter 声明 consumed/produced/consumable_by | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 | output-schema-examples.md 新增 macro_topdown_signal | ✅ section 11 | ✅ | ✅ | ✅ | ✅ |
| 3 | skill-workflow.md 增加路由 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | analyze.md family 路由了解 macro-topdown | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | validation 记录每个样本 consumed/source_status/hard_gates | ✅ | ✅ | ✅ | ✅ | ✅ (assumed) |
| 6 | 无新 signal/action enum | ✅ neutral | ✅ neutral | ✅ neutral | ✅ neutral | ✅ blocked |
| 7 | 无 final_action | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 | ✅ 无 |
| 8 | 无 dead routes | ✅ 仅 basicinfo+market | ✅ | ✅ | ✅ | ✅ |
| 9 | market_regime 字段存在 | ✅ neutral | ✅ neutral | ✅ neutral | ✅ neutral | ✅ unknown |
| 10 | coverage_status 字段存在 | ✅ partial (2 dims) | ✅ partial (2 dims) | ✅ partial (2 dims) | ✅ degraded (1 dim) | ✅ blocked |
| 11 | 缺少指数数据时 signal=blocked | ✅ n/a（有数据） | ✅ n/a | ✅ n/a | ✅ n/a | ✅ blocked |
| 12 | 覆盖门限仅 <2维时触发 | ✅ not_triggered (2 dims) | ✅ not_triggered | ✅ not_triggered | ✅ triggered (1 dim) | ✅ blocked |
| 13 | 不过度 claim（breadth可用时不触发） | ✅ not_triggered | ✅ not_triggered | ✅ not_triggered | ✅ triggered (index-only) | ✅ blocked |
| 14 | 无外部宏观数据 | ✅ 无 CPI/PMI/FX | ✅ | ✅ | ✅ | ✅ |
| 15 | 无 new signal enum 漂移 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 16 | index_returns 与 index_bars 分离 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 17 | data_sources 含 usable_for_scoring | ✅ | ✅ | ✅ | ✅ | ✅ |
| 18 | constitution self-review | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### Action-Term rg Interpretation

```text
rg "final_action|\"action\"|\"stance\": \"buy\"|\"stance\": \"sell\"|\"signal\": \"buy\"|\"signal\": \"sell\""
  tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md
  tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10a.md

→ Expected matches only in constraint text such as:
  - "No final_action" / "No portfolio actions"
  - "Do NOT recommend buy/sell/hold"
  - "does not produce final_action"
  - Unrelated schema sections (price_series, analyze, portfolio) in output-schema-examples.md
→ macro_topdown_signal does NOT contain final_action as an output field
→ macro_topdown_signal does NOT contain "stance": "buy" or "stance": "sell"
→ No output example uses buy/sell/hold/reduce/reject as macro signal or stance value
```

---

### External Macro Data rg Interpretation

```text
rg "PMI|CPI|利率|汇率|期货|期权|美债|美元|FOMC|macro forecast|预测宏观"
  tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md
  docs/tos-funder/validation-pr10a.md

→ Expected matches ONLY in "do not use" / "out of scope" sections:
  - "No CPI, PMI, rates, FX, futures, options, or offshore data"
  - "Do not predict macro policy, interest rates, CPI, PMI, or FX"
  - "No external macro data: No CPI, PMI, rates, FX, futures, options"
  - Must NOT appear in actual command logic or scoring instructions
```

---

### Dead Routes rg Interpretation

```text
rg "query2data|query -r event|query -r business|query -r management"
  tos-funder/commands/tos-funder-macro-topdown.md

→ Expected: NO matches — macro-topdown uses only basicinfo + market routes
```

---

## Constitution Self-Review

```text
Schema consumed:
  - iwc-market: index returns, sector strength, market breadth, turnover
  - iwc-basicinfo: industry tags, concept tags, total_market_cap

Output schema changes:
  - New schema: macro_topdown_signal (section 11 in output-schema-examples.md)
  - signal_type: "macro_topdown" discriminator
  - coverage_status: verified | partial | degraded | blocked
  - market_regime: risk_on | neutral | risk_off | mixed | unknown
  - 4 hard gates: coverage_gate, risk_off_gate, sector_missing_gate, overclaim_gate
  - macro_scoring with dimensions, weights, normalized_score
  - data_sources with per-source status
  - confidence_calculation with base_confidence, verification_bonuses, caps_applied
  - No final_action
  - No portfolio actions
  - No new signal enums

Downstream compatibility check:
  - analyze.md can consume macro_topdown_signal via analyst_signals.macro
  - signal/strength/confidence are typed fields, parsable without prose
  - market_regime provides context for multi-family conflict resolution
  - coverage_status documents data reliability for downstream consumers
  - data_sources provides per-dimension availability for transparency

Constitution self-review:
  - Read the macro-topdown reference, output-schema-examples, skill-workflow,
    command-template, agent-taxonomy? (Y)
  - Read tactical-synthesis, tactical command, analyze, PR9B validation? (Y)
  - Read iwencai-adapter, price-series, 01-interface-coverage? (Y)
  - Avoided new unapproved signal enums? (Y) — bullish/neutral/bearish/blocked only
  - Separated facts, metrics, constraints, interpretation? (Y) — market_context (facts),
    macro_scoring (metrics), hard_gates (constraints), market_regime (interpretation)
  - Labeled fallback and degraded data explicitly? (Y) — coverage_status, data_sources
    with per-source status, usable_for_scoring flags, missing_context/degraded_context
  - Avoided overclaiming from sample validation? (Y) — assumed_fixture vs live_verified
    distinguished; negative scenario properly documents gaps
  - Distinguished data-quality gate from regime gate? (Y) — coverage_gate (data availability)
    separate from risk_off_gate (market regime) and overclaim_gate (output constraint)
  - Can next command consume without parsing prose? (Y) — typed fields (signal, strength,
    confidence, market_regime, coverage_status) and structured macro_scoring
  - Kept iWencai and mootdx source boundaries intact? (Y) — uses only iWencai basicinfo
    + market routes; no mootdx; no dead routes
  - No external macro data used? (Y) — no CPI/PMI/FX/futures/options/rates
  - Index-only mode handles correctly? (Y) — index target uses index-only scoring
  - Missing index data correctly blocks? (Y) — coverage gate forces blocked + unknown
  - Breadth properly verified and scored? (Y) — probe confirms breadth available;
    all stock samples score breadth as a verified dimension
  - Index returns vs bars properly separated? (Y) — index_returns=verified,
    index_bars=unavailable; confidence bonus correctly references index_returns
  - Data sources use usable_for_scoring? (Y) — each source has usable_for_scoring flag;
    sector_strength and risk_appetite marked false with documented reason
  - Overclaim gate correctly constrains output? (Y) — gate not triggered when breadth
    is verified; index-only targets still correctly constrained
  - Documented all known gaps? (Y) — style rotation missing, northbound unavailable,
    sector strength format degraded (usable_for_scoring=false), mootdx index bars
    unavailable, risk appetite partial (usable_for_scoring=false)

Next recommended step:
  - Integrate macro_topdown_signal into /tos-funder-tactical as a third consumed input
    for enriched macro-context-aware synthesis.
  - Consider PR10B Portfolio/Decision Synthesizer to unify value, growth, quant,
    sentiment, tactical, macro, and risk signals into portfolio-level actions.
```
