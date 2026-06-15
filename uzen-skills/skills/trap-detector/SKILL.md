---
name: trap-detector
description: A-share trap and manipulation-risk scan backed by hoxit signals.
---

# UZEN Trap Detector Protocol

This protocol defines how to detect and report A-share market risks and trap signals using hoxit data.

## 1. Risk Category Distinction

### 1.1 Market Risk vs Trap Risk

| Category | Definition | Detection Source |
|----------|------------|------------------|
| **Market Risk** | Observable market signals suggesting elevated downside probability | hoxit quantitative data |
| **Trap Risk** | Social/manipulation evidence suggesting coordinated deception | External qualitative evidence (deferred) |

**Critical distinction**: hoxit provides market risk signals, not trap detection. Full UZI trap detection requires social sentiment analysis, keyword monitoring, and manipulation pattern recognition that are currently deferred.

### 1.2 Current Scope

The first version detects **market risk flags** only:

- Block trade activity
- Margin trading anomalies
- Holder concentration changes
- Fund flow patterns
- Concept/theme heat
- Dragon-tiger board activity
- Lockup expiry pressure

These are **risk indicators**, not proof of manipulation.

## 2. Supported hoxit Inputs

### 2.1 Market Risk Data Sources

| Data Point | hoxit Source | Risk Relevance |
|------------|--------------|----------------|
| Block trades | `hoxit.signals.block_trade` | Large position moves, potential insider activity |
| Margin trading | `hoxit.signals.margin_trading` | Leverage sentiment, forced liquidation risk |
| Holder changes | `hoxit.signals.holder_num_change` | Concentration shifts, potential accumulation/distribution |
| Fund flow | `hoxit.signals.baidu_fund_flow_history` | Capital direction, momentum strength |
| Concept heat | `hoxit.signals.baidu_concept_blocks` | Theme crowding, reversal risk |
| Dragon-tiger | `hoxit.signals.dragon_tiger_board` | Institutional/游资 activity, short-term volatility |
| Lockup expiry | `hoxit.signals.lockup_expiry` | Supply pressure, potential selling wave |
| Dividend history | `hoxit.signals.dividend_history` | Payout consistency, yield sustainability |

### 2.2 Data Quality Gates

- If core signal data is missing → mark risk level as `data_needed`
- If only partial signals available → compute risk with available data, note gaps
- Never fabricate data to fill signal gaps

## 3. Deferred: UZI-Style Social/Manipulation Evidence

### 3.1 Deferred Evidence Categories

UZI-Skill detects trap signals through:

- **Social sentiment analysis**: WeChat groups, stock forums, media campaigns
- **Keyword monitoring**: Coordinated promotion terms, "杀猪盘" indicators
- **Manipulation patterns**: Pump-and-dump signatures, wash trading signals
- **Fake news detection**: Fabricated announcements, misleading information
- **Influencer tracking**: Key opinion leader activity, paid promotion signals

**Current status**: All deferred. hoxit does not have access to social sentiment data or manipulation detection algorithms.

### 3.2 Evidence Requirements (When Implemented)

When trap evidence becomes available, it must include:

```json
{
  "evidence_type": "social_sentiment",
  "source": "stock_forum",
  "url": "https://example.com/post/123",
  "keywords": ["杀猪盘", "内幕消息", "暴涨"],
  "confidence": 0.7,
  "timestamp": "2026-06-14T10:30:00+08:00"
}
```

- `evidence_type`: Category of evidence
- `source`: Where evidence was found
- `url`: Direct link to evidence (required for verification)
- `keywords`: Trigger terms detected
- `confidence`: Float 0-1 indicating evidence strength
- `timestamp`: When evidence was observed

## 4. Output States

### 4.1 Risk Levels

| State | Meaning | Criteria |
|-------|---------|----------|
| `clear` | No significant risk flags | 0-1 minor flags |
| `watch` | Elevated risk, monitor closely | 2-3 flags or single strong flag |
| `risk` | High risk, exercise caution | 4+ flags or critical combination |
| `data_needed` | Cannot assess | Critical data missing |

### 4.2 Current Output Schema

```json
{
  "level": "low",
  "flags": ["存在大宗交易记录", "资金流数据缺失"]
}
```

**Note**: Current implementation maps to `low`/`medium`/`high` which correspond to `clear`/`watch`/`risk`. The `data_needed` state is added for missing critical data.

### 4.3 Target Output Schema

```json
{
  "market_risk": {
    "level": "watch",
    "flags": [
      {
        "type": "block_trade",
        "severity": "medium",
        "description": "近30天存在3笔大宗交易，合计金额1.2亿",
        "data_source": "hoxit.signals.block_trade"
      }
    ],
    "data_quality": {
      "complete": false,
      "missing": ["margin_trading", "holder_num_change"]
    }
  },
  "trap_risk": {
    "level": "data_needed",
    "evidence": [],
    "reason": "社交舆情数据不可用"
  },
  "overall_risk": "watch"
}
```

## 5. No-Fabrication Rule

### 5.1 Market Risk Signals

- Do not invent block trades, margin data, or fund flow records
- Do not create fake holder changes or lockup dates
- Do not generate plausible but unverified risk flags
- If data is missing, report as `data_needed`

### 5.2 Social/Manipulation Claims

**Strictly forbidden**:

- Claiming social sentiment without data source and URL
- Alleging manipulation without verifiable evidence
- Creating fake forum posts, WeChat messages, or news articles
- Implying coordination without keyword and timestamp evidence

**Required for any trap claim**:

- Direct URL to evidence source
- Specific keywords detected
- Timestamp of observation
- Confidence level with justification

## 6. Execution Protocol

### 6.1 CLI Invocation

```bash
hoxit uzen scan-trap <code> [--output-dir <path>]
```

### 6.2 Current Execution Flow

1. Validate stock code (6 digits, A-share)
2. Call `hoxit.uzen.collect_snapshot()` with `mode="scan-trap"`
3. Call `hoxit.uzen.analyze_snapshot()` which computes `_trap_risk()`
4. Write `<code>-scan-trap.json` and `<code>-scan-trap.md`
5. Return artifact paths

### 6.3 Interpretation Rules

When interpreting risk output:

- **Do**: Report observable market risk flags as computed
- **Do**: Explain what data was available and what was missing
- **Do**: Distinguish between "no risk detected" and "data insufficient"
- **Don't**: Claim trap detection when only market risk is assessed
- **Don't**: Invent social sentiment or manipulation evidence
- **Don't**: Present market risk flags as proof of coordinated deception
