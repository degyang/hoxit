---
name: investor-panel
description: A-share investor-panel summary backed by hoxit.uzen.
---

# UZEN Investor Panel Protocol

This protocol defines how to generate and interpret A-share investor panel summaries using hoxit data.

## 1. Current Behavior

### 1.1 Deterministic Panel (Phase 3)

The current `panel-only` command produces a deterministic investor panel with 5 investor archetypes:

| 投资者 | ID | 分组 | 判断依据 |
|--------|-----|------|----------|
| 价值投资者 | `value` | 基本面 | PE、PB |
| 质量投资者 | `quality` | 基本面 | ROE、净利润 |
| 成长投资者 | `growth` | 基本面 | 盈利增长、PEG |
| 动量投资者 | `momentum` | 技术面 | 涨跌幅、资金流、龙虎榜 |
| 游资关注者 | `hot_money` | 技术面 | 大宗交易、融资融券、股东户数、龙虎榜 |

This is **not** a full UZI 65-investor panel. It is a deterministic baseline with 5 investor archetypes.

### 1.2 Current Output Schema

```json
{
  "score": 65,
  "verdict": "bullish",
  "reasons": ["价值投资者：PE 15.0 倍，估值偏低", "质量投资者：ROE 20.0%，盈利能力强"],
  "signals": [
    {
      "investor_id": "value",
      "name": "价值投资者",
      "group": "fundamental",
      "signal": "pass",
      "score": 70,
      "confidence": 0.75,
      "reasoning": ["PE 15.0 倍，估值偏低"]
    },
    {
      "investor_id": "quality",
      "name": "质量投资者",
      "group": "fundamental",
      "signal": "pass",
      "score": 80,
      "confidence": 0.85,
      "reasoning": ["ROE 20.0%，盈利能力强"]
    }
  ],
  "vote_distribution": {
    "pass": 3,
    "fail": 0,
    "neutral": 1,
    "data_needed": 1
  }
}
```

- `score`: Integer 0-100. Weighted average of non-`data_needed` signals.
- `verdict`: `"bullish"` (≥65), `"bearish"` (≤40), or `"neutral"` (41-64).
- `reasons`: List of human-readable strings from top signals.
- `signals`: List of 5 investor signals (see §2.1 for signal schema).
- `vote_distribution`: Counts of each signal type.

## 2. Current Investor Signal Schema

### 2.1 Individual Investor Signal

Each investor in the panel produces:

```json
{
  "investor_id": "value",
  "name": "价值投资者",
  "group": "fundamental",
  "signal": "pass",
  "score": 70,
  "confidence": 0.75,
  "reasoning": ["PE 15.0 倍，估值偏低"]
}
```

Fields:

- `investor_id`: Unique identifier for the investor archetype (`value`, `quality`, `growth`, `momentum`, `hot_money`).
- `name`: Human-readable name (Chinese).
- `group`: Investor group (`fundamental` or `technical`).
- `signal`: One of `pass`, `fail`, `neutral`, `data_needed`.
- `score`: Integer 0-100.
- `confidence`: Float 0-1 indicating data completeness and signal clarity.
- `reasoning`: List of human-readable strings explaining the signal.

### 2.2 Signal Semantics

| Signal | Meaning | When to Use |
|--------|---------|-------------|
| `pass` | Investor would likely approve | Data supports positive assessment |
| `fail` | Investor would likely reject | Data shows clear red flags |
| `neutral` | Mixed or inconclusive | Data shows both positive and negative signals |
| `data_needed` | Cannot assess | Critical data missing or unsupported |

### 2.3 Aggregated Panel

```json
{
  "score": 62,
  "verdict": "neutral",
  "reasons": ["价值投资者：PE 15.0 倍，估值偏低"],
  "signals": [...],
  "vote_distribution": {
    "pass": 3,
    "fail": 0,
    "neutral": 1,
    "data_needed": 1
  }
}
```

- `score`: Weighted average of non-`data_needed` signals.
- `verdict`: `"bullish"` (≥65), `"bearish"` (≤40), or `"neutral"` (41-64).
- `reasons`: Top reasons from passing/failing signals.
- `signals`: List of 5 investor signals.
- `vote_distribution`: Counts of each signal type.

## 3. A-Share Data Inputs from hoxit

### 3.1 Available Data

| Data Point | hoxit Source | Investor Relevance |
|------------|--------------|-------------------|
| PE/PB/Market Cap | `hoxit.market.tencent_metrics` | Value investors |
| Forward PE/PEG | `hoxit.valuation.full_valuation` | Growth investors |
| ROE/Net Profit | `hoxit.fundamentals.finance_snapshot` | Quality investors |
| Industry classification | `hoxit.signals.industry_comparison` | Sector investors |
| Capital flow | `hoxit.signals.baidu_fund_flow_history` | Momentum investors |
| Dragon-tiger board | `hoxit.signals.dragon_tiger_board` | Short-term traders |
| Block trades | `hoxit.signals.block_trade` | Institutional investors |
| Margin trading | `hoxit.signals.margin_trading` | Leverage sentiment |
| Holder changes | `hoxit.signals.holder_num_change` | Concentration analysis |
| Lockup expiry | `hoxit.signals.lockup_expiry` | Supply pressure |
| Concept blocks | `hoxit.signals.baidu_concept_blocks` | Theme investors |
| Dividend history | `hoxit.signals.dividend_history` | Income investors |

### 3.2 Data Quality Gates

- If core valuation data (PE, PB) is missing → mark affected investors as `data_needed`
- If financial snapshot fails → quality/value investors get `data_needed`
- If signal data is missing → affected signal-dependent investors get `data_needed`
- Never fabricate data to fill gaps

## 4. Deferred: Full UZI 65-Investor Parity

UZI-Skill defines 65 investor archetypes across categories:

- Value investors (Buffett, Graham, etc.)
- Growth investors (Lynch, O'Neil, etc.)
- Momentum investors
- Quantitative investors
- Macro investors
- Sector specialists
- Behavioral investors

**Current status**: Phase 3 implements 5 deterministic baseline investors (value, quality, growth, momentum, hot-money). Full 65-investor parity is deferred.

**Future path**: Expand investor archetypes one group at a time:

1. **Value group**: Buffett, Graham, Schloss — using PE/PB/ROE/dividend data
2. **Growth group**: Lynch, Fisher, O'Neil — using growth rates/PEG/momentum
3. **Quality group**: Greenblatt, Piotroski — using financial quality metrics

Each group should be implemented with:
- Deterministic scoring rules
- hoxit data inputs only
- Unit tests with injected providers
- No network access in default tests

## 5. Execution Protocol

### 5.1 CLI Invocation

```bash
hoxit uzen panel-only <code> [--output-dir <path>]
```

### 5.2 Current Execution Flow

1. Validate stock code (6 digits, A-share)
2. Call `hoxit.uzen.collect_snapshot()` with `mode="panel-only"`
3. Call `hoxit.uzen.analyze_snapshot()` which:
   - Runs 5 investor archetypes (`_value_investor`, `_quality_investor`, `_growth_investor`, `_momentum_investor`, `_hot_money_investor`)
   - Computes `vote_distribution` (pass/fail/neutral/data_needed counts)
   - Computes aggregate `score`, `verdict`, `reasons`
4. Write `<code>-panel-only.json` and `<code>-panel-only.md`
5. Return artifact paths

### 5.3 Interpretation Rules

When interpreting panel output:

- **Do**: Report the score, verdict, and reasons as computed.
- **Do**: Explain what data was available and what was missing.
- **Do**: Separate factual evidence from interpretive reasoning.
- **Don't**: Claim the panel represents 65 investor personas.
- **Don't**: Invent investor opinions not supported by data.
- **Don't**: Present the lightweight score as equivalent to UZI's full panel.
