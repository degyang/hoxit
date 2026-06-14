---
name: investor-panel
description: A-share investor-panel summary backed by hoxit.uzen.
---

# UZEN Investor Panel Protocol

This protocol defines how to generate and interpret A-share investor panel summaries using hoxit data.

## 1. Current Behavior

### 1.1 Lightweight Panel (First Version)

The current `panel-only` command produces a lightweight panel summary based on:

- **Valuation metrics**: Forward PE, PE TTM, PB from `hoxit.valuation` and `hoxit.market`
- **Financial quality**: ROE from `hoxit.fundamentals.finance_snapshot`
- **Simple scoring**: +10 for PE < 20, -15 for PE > 60, +10 for ROE ≥ 10

This is **not** a full investor panel. It is a deterministic first-version approximation.

### 1.2 Current Output Schema

```json
{
  "score": 50,
  "verdict": "neutral",
  "reasons": ["估值低于 20 倍 PE 区间", "ROE 达到双位数"]
}
```

- `score`: Integer 0-100. Base is 50, adjusted by valuation/finance rules.
- `verdict`: `"bullish"` (≥65), `"bearish"` (≤40), or `"neutral"` (41-64).
- `reasons`: List of human-readable strings explaining the score adjustment.

## 2. Target Investor Signal Schema

### 2.1 Individual Investor Signal

Each investor in the panel should produce:

```json
{
  "investor_id": "value_investor",
  "investor_name": "价值投资者",
  "signal": "pass",
  "confidence": 0.8,
  "evidence": ["PE 15 低于行业均值 22", "ROE 12% 持续三年"],
  "reasoning": "估值合理且盈利质量稳定，符合价值投资标准",
  "weight": 0.15
}
```

Fields:

- `investor_id`: Unique identifier for the investor archetype.
- `investor_name`: Human-readable name (Chinese).
- `signal`: One of `pass`, `fail`, `neutral`, `data_needed`.
- `confidence`: Float 0-1 indicating data completeness and signal clarity.
- `evidence`: List of factual statements from hoxit data.
- `reasoning`: Qualitative interpretation separated from raw data.
- `weight`: Float 0-1 for aggregation weight.

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
  "panel_score": 62,
  "panel_verdict": "neutral",
  "total_investors": 8,
  "signals": {
    "pass": 3,
    "fail": 1,
    "neutral": 2,
    "data_needed": 2
  },
  "investors": [...]
}
```

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

**Current status**: Deferred. The first version uses a lightweight deterministic scoring, not persona-based analysis.

**Future path**: Implement investor archetypes one group at a time, starting with:

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
3. Call `hoxit.uzen.analyze_snapshot()` which computes `_panel_summary()`
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
