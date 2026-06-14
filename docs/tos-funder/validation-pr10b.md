# PR10B Validation: Portfolio / Decision Synthesizer

## Scope

Validates `/tos-funder-portfolio` upgrade for PR10B: consuming all 7 upstream signal families (value, growth, quant, sentiment, risk, tactical, macro) with five-layer decision model, conflict resolution, and deterministic confidence rules.

## Data Source Notes

All samples in this validation use:
- `accepted_prior_validation` — signal values from previously accepted PR validation docs (PR2A, PR5B, PR8A, PR9A, PR9B, PR10A)
- `assumed_fixture` — synthetic but realistic signal values for layers not previously validated per-stock
- `live_query_result` — where noted, from live probe runs

Sources are labeled per cell. No unlabeled mixing.

---

## Sample 1: 002142 宁波银行 (Held Position)

### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 002142 | accepted_prior_validation |
| Name | 宁波银行 | accepted_prior_validation |
| Industry | 银行 | accepted_prior_validation |
| Sector type | financial (bank) | accepted_prior_validation |

### Consumed Signals

| Layer | Source | Signal | Confidence | source_status |
|---|---|---|---|---|
| Thesis | Buffett | bullish | 75 | accepted_prior_validation (PR2A) |
| Thesis | Graham | neutral | 65 | accepted_prior_validation (PR2A) |
| Thesis | Growth agg | bullish | 70 | assumed_fixture |
| Thesis | Quant fundamentals | bullish | 80 | accepted_prior_validation |
| Timing | Technicals | bearish (weak) | 55 | accepted_prior_validation |
| Timing | Sentiment | neutral | 60 | assumed_fixture |
| Tactical | Tactical synthesis | neutral | 55 | assumed_fixture |
| Macro | Macro top-down | neutral | 70 | accepted_prior_validation (PR10A) |
| Risk | Risk-manager | moderate (valid) | — | accepted_prior_validation |

### Required Inputs Present

| Input | Present |
|---|---|
| Directional thesis (value/growth/quant) | ✅ Buffett bullish, quant bullish |
| Risk-manager | ✅ moderate, valid |

### Layer Scores

```
Thesis:
  Buffett:  +1.0 × 1.2 =  1.20
  Graham:    0.0 × 1.0 =  0.00
  Growth:   +1.0 × 1.1 =  1.10
  Quant F:  +1.0 × 1.0 =  1.00
  Total weight: 4.3
  Thesis score: (1.20 + 0.00 + 1.10 + 1.00) / 4.3 = 0.77

Timing:
  Technicals: -1.0 × 0.6 = -0.60 (weak strength → -0.5 × 0.6 = -0.30)
  Sentiment:   0.0 × 0.4 =  0.00
  Total weight: 1.0
  Timing score: (-0.30 + 0.00) / 1.0 = -0.30

Context:
  Tactical: 0.0 × 0.6 = 0.00
  Macro:    0.0 × 0.5 = 0.00
  Context score: 0.00

Net score = 0.77 + (-0.30 × 0.3) + (0.00 × 0.2) = 0.77 - 0.09 = 0.68
```

### Consensus

Signals: bullish (Buffett, growth, quant), neutral (Graham, sentiment, tactical, macro), bearish (technicals). 3 bullish, 4 neutral, 1 bearish → Moderate consensus.

### Conflict Resolution

| Rule | Applied | Result |
|---|---|---|
| 1. Risk hard veto | Not triggered | Risk level moderate, no hard veto |
| 2. Critical tail risk | Not triggered | Tactical neutral |
| 3. Bearish thesis vs timing | Not applicable | Thesis is bullish, not bearish |
| 4. Bullish thesis + bearish timing | ✅ Applied | Watch for technical reversal before adding |
| 5. Macro cap | Not triggered | Macro neutral |
| 6. Data-quality gate | Not triggered | All sources valid |

### Confidence Calculation

```text
base_confidence = round((75×1.2 + 65×1.0 + 70×1.1 + 80×1.0 + 55×0.6 + 60×0.4 + 55×0.6 + 70×0.5) / (1.2+1.0+1.1+1.0+0.6+0.4+0.6+0.5))
                = round(443.0 / 6.4) = round(69.2) = 69
adjustments: []
caps_applied: []
final_confidence = 69
```

### Expected Outcome

```text
position: held (5000 shares)
action: hold
confidence: 69
reasoning: Thesis bullish (Buffett + quant + growth) but technicals bearish (weak).
  Risk moderate, all sources valid. Rule 4: bullish thesis + bearish timing delays entry.
  Hold existing position, watch for technical reversal before adding.
```

**判定**: ✅ Hold — 论点多层看涨（巴菲特、量化、增长），但技术面偏弱。冲突规则 4 适用：看涨论点 + 看跌时机 = 延迟建仓。现有持仓继续持有。

---

## Sample 2: 600519 贵州茅台 (Watchlist / No Position)

### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 600519 | accepted_prior_validation |
| Name | 贵州茅台 | accepted_prior_validation |
| Industry | 白酒 | accepted_prior_validation |
| Sector type | consumer | accepted_prior_validation |

### Consumed Signals

| Layer | Source | Signal | Confidence | source_status |
|---|---|---|---|---|
| Thesis | Buffett | bullish | 75 | accepted_prior_validation (PR2A) |
| Thesis | Graham | neutral | 65 | accepted_prior_validation (PR2A) |
| Thesis | Growth agg | bearish (weak) | 50 | assumed_fixture — growth slowing |
| Thesis | Quant fundamentals | neutral | 65 | accepted_prior_validation |
| Timing | Technicals | bearish (weak) | 70 | accepted_prior_validation |
| Timing | Sentiment | neutral | 55 | assumed_fixture |
| Tactical | Tactical synthesis | neutral | 55 | assumed_fixture |
| Macro | Macro top-down | neutral | 70 | accepted_prior_validation (PR10A) |
| Risk | Risk-manager | moderate (valid) | — | accepted_prior_validation |

### Required Inputs Present

| Input | Present |
|---|---|
| Directional thesis | ✅ Buffett bullish |
| Risk-manager | ✅ moderate, valid |

### Layer Scores

```
Thesis:
  Buffett:  +1.0 × 1.2 =  1.20
  Graham:    0.0 × 1.0 =  0.00
  Growth:   -1.0 × 0.5 × 1.1 = -0.55
  Quant F:   0.0 × 1.0 =  0.00
  Total weight: 4.3
  Thesis score: (1.20 + 0.00 - 0.55 + 0.00) / 4.3 = 0.15

Timing:
  Technicals: -1.0 × 0.5 × 0.6 = -0.30 (bearish weak = -1.0 × 0.5 = -0.5)
  Sentiment:   0.0 × 0.4 =  0.00
  Total weight: 1.0
  Timing score: (-0.30 + 0.00) / 1.0 = -0.30

Context:
  Tactical: 0.0 × 0.6 = 0.00
  Macro:    0.0 × 0.5 = 0.00
  Context score: 0.00

Net score = 0.15 + (-0.30 × 0.3) + 0.00 = 0.15 - 0.09 = 0.06
```

### Consensus

Signals: bullish (Buffett), neutral (Graham, quant, sentiment, tactical, macro), bearish (growth, technicals). 1 bullish, 5 neutral, 2 bearish → Moderate consensus.

### Conflict Resolution

| Rule | Applied | Result |
|---|---|---|
| 1. Risk hard veto | Not triggered | Risk moderate, valid |
| 2. Critical tail risk | Not triggered | Tactical neutral |
| 3. Bearish thesis vs timing | Not triggered | Thesis is weakly positive, not bearish |
| 4. Bullish thesis + bearish timing | ✅ Applied | Watch for technical reversal |
| 5. Macro cap | Not triggered | Macro neutral |
| 6. Data-quality gate | Not triggered | All sources valid |

### Confidence Calculation

```text
base_confidence = round((75×1.2 + 65×1.0 + 50×1.1 + 65×1.0 + 70×0.6 + 55×0.4 + 55×0.6 + 70×0.5) / 6.4)
                = round(410.5 / 6.4) = round(64.1) = 64
adjustments: []
caps_applied: []
final_confidence = 64
```

### Expected Outcome

```text
position: no position (watchlist)
action: watch
confidence: 64
reasoning: Buffett quality positive but Graham neutral (expensive valuation),
  growth slowing (bearish). Thesis weakly positive (0.15). Technicals bearish (weak).
  Risk moderate, all sources valid. Watch — no strong buy signal.
  Macro does not force buy (Rule 5).
```

**判定**: ✅ Watch — 巴菲特质量正面但增长放缓，技术面偏弱。论点火头不足（0.15）。符合规则 4（看涨论点 + 看跌时机 = watch）和规则 5（宏观不能强制买入）。

---

## Sample 3: 002594 比亚迪 (Watchlist / New Position)

### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 002594 | accepted_prior_validation |
| Name | 比亚迪 | accepted_prior_validation |
| Industry | 汽车整车 | accepted_prior_validation |
| Concepts | 新能源汽车, 锂电池, etc. | accepted_prior_validation |
| Sector type | high_capex_industrial | accepted_prior_validation |

### Consumed Signals

| Layer | Source | Signal | Confidence | source_status |
|---|---|---|---|---|
| Thesis | Buffett | neutral | 60 | accepted_prior_validation (PR2A) |
| Thesis | Graham | neutral | 60 | accepted_prior_validation (PR2A) |
| Thesis | Growth agg | bullish | 65 | assumed_fixture |
| Thesis | Quant fundamentals | neutral | 60 | accepted_prior_validation |
| Timing | Technicals | bearish (weak) | 50 | accepted_prior_validation |
| Timing | Sentiment | neutral | 60 | assumed_fixture |
| Tactical | Tactical synthesis | neutral | 50 | assumed_fixture |
| Macro | Macro top-down | neutral | 70 | accepted_prior_validation (PR10A) |
| Risk | Risk-manager | degraded | — | accepted_prior_validation (adjustment_status=suspect) |

### Required Inputs Present

| Input | Present |
|---|---|
| Directional thesis | ✅ Growth bullish |
| Risk-manager | ✅ degraded (data-quality issues) |

### Layer Scores

```
Thesis:
  Buffett:   0.0 × 1.2 =  0.00
  Graham:    0.0 × 1.0 =  0.00
  Growth:   +1.0 × 1.1 =  1.10
  Quant F:   0.0 × 1.0 =  0.00
  Total weight: 4.3
  Thesis score: (0.00 + 0.00 + 1.10 + 0.00) / 4.3 = 0.26

Timing:
  Technicals: -1.0 × 0.5 × 0.6 = -0.30
  Sentiment:   0.0 × 0.4 =  0.00
  Total weight: 1.0
  Timing score: (-0.30 + 0.00) / 1.0 = -0.30

Context:
  Tactical: 0.0 × 0.6 = 0.00
  Macro:    0.0 × 0.5 = 0.00
  Context score: 0.00

Net score = 0.26 + (-0.30 × 0.3) + 0.00 = 0.26 - 0.09 = 0.17
```

### Consensus

Signals: bullish (growth), neutral (Buffett, Graham, quant, sentiment, tactical, macro), bearish (technicals). 1 bullish, 6 neutral, 1 bearish → Moderate consensus.

### Conflict Resolution

| Rule | Applied | Result |
|---|---|---|
| 1. Risk hard veto | Not triggered (degraded) | Data-quality cap takes precedence |
| 2. Critical tail risk | Not triggered | Tactical neutral |
| 3. Bearish thesis vs timing | Not applicable | Thesis is positive |
| 4. Bullish thesis + bearish timing | ✅ Applied | Watch for technical reversal |
| 5. Macro cap | Not triggered | Macro neutral |
| 6. Data-quality gate | ✅ Applied | risk_metric_status=degraded → cap at watch |

### Confidence Calculation

```text
base_confidence = round((60×1.2 + 60×1.0 + 65×1.1 + 60×1.0 + 50×0.6 + 60×0.4 + 50×0.6 + 70×0.5) / 6.4)
                = round(400.5 / 6.4) = round(62.6) = 63
adjustments: []
caps_applied:
  - data_quality cap: 60 (risk_metric_status=degraded)
  - risk_degraded cap: 55 (risk-manager degraded)
final_confidence = min(63, 60, 55) = 55
```

### Expected Outcome

```text
position: no position (watchlist)
action: watch
confidence: 55
reasoning: Growth thesis bullish but value neutral. Technicals bearish (weak).
  Risk metrics degraded (adjustment_status=suspect, max_dd inflated by stock split).
  Data-quality gate caps action at watch (Rule 6).
  Degraded metrics do NOT force reject/sell (data-quality constraint, not risk signal).
```

**判定**: ✅ Watch — 增长论点看涨但价值中性。风险指标降级（送转导致 max_dd 失真）。数据质量门限将操作上限限制为 watch。降级指标不被视为真实风险信号。

---

## Sample 4: 000820 \*ST节能 (Negative / Tail-Risk Sample)

### Target Context

| Field | Data | source_status |
|---|---|---|
| Code | 000820 | accepted_prior_validation (PR9A) |
| Name | \*ST节能 | accepted_prior_validation (PR9A) |
| Status | \*ST (special treatment — delisting risk) | accepted_prior_validation |
| Events | CSRC 立案调查, 投资者诉讼, 持续经营重大不确定 | accepted_prior_validation |

### Consumed Signals

| Layer | Source | Signal | Confidence | source_status |
|---|---|---|---|---|
| Thesis | Buffett | bearish | 30 | assumed_fixture |
| Thesis | Graham | bearish | 25 | assumed_fixture |
| Thesis | Growth agg | blocked | 20 | assumed_fixture |
| Thesis | Quant fundamentals | bearish | 30 | assumed_fixture |
| Timing | Technicals | bearish (strong) | 40 | assumed_fixture |
| Timing | Sentiment | bearish | 30 | assumed_fixture |
| Tactical | Tactical synthesis | bearish (critical TR) | 25 | assumed_fixture |
| Macro | Macro top-down | bearish | 60 | assumed_fixture |
| Risk | Risk-manager | extreme | — | assumed_fixture |

### Required Inputs Present

| Input | Present |
|---|---|
| Directional thesis | ✅ bearish across all sources |
| Risk-manager | ✅ extreme |

### Layer Scores

```
Thesis:
  Buffett:  -1.0 × 1.2 = -1.20
  Graham:   -1.0 × 1.0 = -1.00
  Growth:   blocked — excluded
  Quant F:  -1.0 × 1.0 = -1.00
  Total weight: 3.2 (growth blocked)
  Thesis score: (-1.20 - 1.00 - 1.00) / 3.2 = -1.00

Timing:
  Technicals: -1.0 × 1.0 × 0.6 = -0.60
  Sentiment:  -1.0 × 0.4 = -0.40
  Total weight: 1.0
  Timing score: (-0.60 - 0.40) / 1.0 = -1.00

Context:
  Tactical: -1.0 × 0.6 = -0.60 (critical tail risk)
  Macro:   -1.0 × 0.5 = -0.50
  Context score: (-0.60 - 0.50) / 1.1 = -1.00

Net score = -1.00 + (-1.00 × 0.3) + (-1.00 × 0.2) = -1.00 - 0.30 - 0.20 = -1.50
```

### Consensus

All sources bearish or blocked → Strong consensus.

### Conflict Resolution

| Rule | Applied | Result |
|---|---|---|
| 1. Risk hard veto | ✅ Applied | EPS<0, extreme risk, *ST status → reject |
| 2. Critical tail risk | ✅ Applied | Tactical synthesis reports critical TR → new position blocked at reject |
| 3. Bearish thesis wins | ✅ Applied | Thesis bearish, all layers confirm |
| 4–6 | Not needed | Bearish consensus overrides |

### Confidence Calculation

```text
base_confidence = round((30×1.2 + 25×1.0 + 30×1.0 + 40×0.6 + 30×0.4 + 25×0.6 + 60×0.5) / (1.2+1.0+1.0+0.6+0.4+0.6+0.5))
                (growth blocked — excluded)
                = round(175.5 / 5.3) = round(33.1) = 33
adjustments:
  - strong consensus: +8
caps_applied:
  - data_quality cap: 60 (N/A — already below)
  - risk_degraded cap: 55 (N/A — already below)
  - critical tail-risk cap: 45 (N/A — already below)
  - missing thesis layer cap: N/A (thesis is present but bearish)
final_confidence = min(33 + 8, 45, 55, 60) = min(41, 45) = 41
```

### Expected Outcome

```text
position: no position (watchlist)
action: reject
confidence: 41
reasoning: All thesis layers bearish, critical tail risk active, risk-manager
  reports extreme risk. EPS<0, *ST delisting risk. CSRC investigation and
  investor lawsuits. Critical tail risk caps new position at reject (Rule 2).
  Bearish thesis confirmed across all layers (Rule 3).
```

**判定**: ✅ Reject — 全层看跌，重大尾部风险，退市风险警示（*ST）。规则 2（重大尾部风险限制看涨操作）和规则 3（看跌论点优先于看涨时机）均触发。与 PR9A 尾部风险样本一致。

---

## Required Input Edge Cases

### Edge Case A: Missing Risk-Manager

All upstream signals are available except `/tos-funder-risk-manager`.

```text
consumed_signals:
  value:       {buffett: bullish, graham: neutral}
  growth:      {signal: bullish}
  quant:       {fundamentals: bullish, technicals: neutral}
  sentiment:   {signal: neutral}
  tactical:    {signal: neutral}
  macro:       {signal: neutral}
  risk:        NOT AVAILABLE

required_inputs_present:
  directional thesis:  ✅ (value + quant both bullish)
  risk-manager:        ❌ MISSING

action: blocked
confidence: 30
reasoning: All thesis layers available and bullish. However, risk-manager is
  missing — position sizing cannot be computed, hard risk vetoes cannot be
  checked. Per PR10B rules, final action must be blocked.
  Confidence capped at 30 (missing required layer).
```

**判定**: ✅ Blocked — 缺少 risk-manager 无法计算仓位大小和硬风险否决。此为 PR10B 硬性规则。

### Edge Case B: No Directional Thesis Layer

Risk-manager is present but all thesis-layer sources (value, growth, quant fundamentals) are missing or blocked.

```text
consumed_signals:
  value:       {buffett: MISSING, graham: MISSING}
  growth:      {signal: blocked}
  quant:       {fundamentals: blocked}
  technicals:  {signal: bullish}      # timing layer alone
  sentiment:   {signal: neutral}
  tactical:    {signal: neutral}
  macro:       {signal: neutral}
  risk:        {level: moderate, valid}

required_inputs_present:
  directional thesis:  ❌ NONE (all missing or blocked)
  risk-manager:        ✅ present

action: blocked
confidence: 25
reasoning: No directional thesis layer is available. Technicals alone cannot
  form a thesis. Per PR10B rules, at least one of value/growth/quant fundamentals
  must be present for a final portfolio action. Action must be blocked.
  Confidence capped at 30 (missing required layer), further reduced by
  single-source equivalent (-10).
```

**判定**: ✅ Blocked — 缺少方向性论点层。技术面和情绪面不能独立构成投资论点。此为 PR10B 硬性规则。

---

## Acceptance Criteria

| # | 条件 | 宁波银行 | 贵州茅台 | 比亚迪 | \*ST节能 | Edge A (missing RM) | Edge B (no thesis) |
|---|---|---|---|---|---|---|---|
| 1 | consumed_signals 含全部 7 层 | ✅ | ✅ | ✅ | ✅ | ✅ 无 risk | ✅ 无 thesis |
| 2 | layer_scores 含 thesis/timing/context/net | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 | 至少一个有方向性论点 + risk-manager | ✅ | ✅ | ✅ | ✅ | ❌ risk 缺 | ❌ thesis 缺 |
| 4 | 缺少 risk-manager 时 blocked | ✅ n/a | ✅ n/a | ✅ n/a | ✅ n/a | ✅ blocked | ✅ n/a |
| 5 | 无方向性论点时 blocked | ✅ n/a | ✅ n/a | ✅ n/a | ✅ n/a | ✅ n/a | ✅ blocked |
| 6 | confidence 为 int 0-100 | ✅ 69 | ✅ 64 | ✅ 55 | ✅ 41 | ✅ 30 | ✅ 25 |
| 7 | confidence_calculation 含 base/adjustments/caps/final | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8 | final_confidence = top-level confidence | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9 | 无 new action enum 漂移 | ✅ hold | ✅ watch | ✅ watch | ✅ reject | ✅ blocked | ✅ blocked |
| 10 | 无 final_action 在 portfolio 外 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 11 | 宏观不独立创建买入 | ✅ 不适用 | ✅ watch | ✅ watch | ✅ n/a | ✅ n/a | ✅ n/a |
| 12 | 降级指标不独立强制卖出 | ✅ n/a | ✅ n/a | ✅ watch 非 sell | ✅ n/a | ✅ n/a | ✅ n/a |
| 13 | 重大尾部风险限制操作 | ✅ n/a | ✅ n/a | ✅ n/a | ✅ reject | ✅ n/a | ✅ n/a |
| 14 | conflict_resolution 文档化 | ✅ 规则 4 | ✅ 规则 4,5 | ✅ 规则 4,6 | ✅ 规则 1,2,3 | ✅ n/a | ✅ n/a |
| 15 | data_quality_vetoes 与 risk_vetoes 分离 | ✅ 均空 | ✅ 均空 | ✅ dq 非空 | ✅ risk 非空 | ✅ n/a | ✅ n/a |
| 6 | confidence 为 int 0-100 | ✅ 69 | ✅ 64 | ✅ 55 | ✅ 41 |
| 7 | confidence_calculation 含 base/adjustments/caps/final | ✅ | ✅ | ✅ | ✅ |
| 8 | final_confidence = top-level confidence | ✅ | ✅ | ✅ | ✅ |
| 9 | 无 new action enum 漂移 | ✅ hold | ✅ watch | ✅ watch | ✅ reject |
| 10 | 无 final_action 在 portfolio 外 | ✅ | ✅ | ✅ | ✅ |
| 11 | 宏观不独立创建买入 | ✅ 不适用 | ✅ watch | ✅ watch | ✅ n/a |
| 12 | 降级指标不独立强制卖出 | ✅ n/a | ✅ n/a | ✅ watch 非 sell | ✅ n/a |
| 13 | 重大尾部风险限制操作 | ✅ n/a | ✅ n/a | ✅ n/a | ✅ reject |
| 14 | conflict_resolution 文档化 | ✅ 规则 4 | ✅ 规则 4,5 | ✅ 规则 4,6 | ✅ 规则 1,2,3 |
| 15 | data_quality_vetoes 与 risk_vetoes 分离 | ✅ 均空 | ✅ 均空 | ✅ dq 非空 | ✅ risk 非空 |
