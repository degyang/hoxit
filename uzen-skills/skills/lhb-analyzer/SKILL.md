---
name: lhb-analyzer
description: A-share dragon-tiger-board analysis backed by hoxit signals.
---

# UZEN LHB Analyzer Protocol

This protocol defines how to analyze A-share dragon-tiger-board (龙虎榜) data using hoxit signals.

## 1. Input Requirements

### 1.1 Required Parameters

| Parameter | Required | Format | Description |
|-----------|----------|--------|-------------|
| `code` | Yes | 6-digit A-share code | Stock to analyze |
| `trade-date` | Conditional | `YYYY-MM-DD` | Date of LHB data. Required for `lhb-analyzer` command. |
| `output-dir` | No | Path | Output directory (default: `uzen-skills/reports`) |

### 1.2 Date Handling

- For `lhb-analyzer` command: `--trade-date` is required
- For other UZEN commands: defaults to today if not specified
- LHB data is typically published T+1 after trading day

## 2. hoxit LHB Data Boundary

### 2.1 Data Availability Tiers

| Tier | Data Point | hoxit Source | Description |
|------|------------|--------------|-------------|
| **Currently wired** | Dragon-tiger board | `hoxit.signals.dragon_tiger_board` | Single-stock LHB records via `provider.dragon_tiger` |
| **Currently wired** | Lockup expiry | `hoxit.signals.lockup_expiry` | Supply pressure context |
| **Currently wired** | Block trades | `hoxit.signals.block_trade` | Institutional activity |
| **Currently wired** | Margin trading | `hoxit.signals.margin_trading` | Leverage sentiment |
| **Currently wired** | Fund flow | `hoxit.signals.baidu_fund_flow_history` | Capital direction |
| **Available, not wired** | Daily dragon-tiger | `hoxit.signals.daily_dragon_tiger` | Market-wide LHB summary (exists in hoxit, not yet in UZEN provider) |
| **Deferred** | Seat database | N/A | Historical seat patterns, institution vs 游资 classification |
| **Deferred** | Peer ranking | N/A | Sector/概念 peer LHB comparison |
| **Deferred** | Historical patterns | N/A | Seat repetition, turnaround patterns |

### 2.2 Current LHB Record Schema

```json
{
  "trade_date": "2026-06-14",
  "code": "600519",
  "name": "贵州茅台",
  "close": 1800.00,
  "change_pct": 5.2,
  "turnover_rate": 1.2,
  "net_buy": 50000000,
  "buy_amount": 120000000,
  "sell_amount": 70000000,
  "reason": "涨幅偏离值达7%的证券"
}
```

### 2.3 Data Quality Gates

- If LHB data is missing for requested date → report as `data_needed`
- If only partial records available → analyze with available data, note gaps
- If stock not on LHB for that date → report "not on dragon-tiger board"

## 3. Target Seat Schema

### 3.1 Individual Seat Record

Each buy/sell seat should produce:

```json
{
  "seat_id": "SEC001",
  "seat_name": "机构专用",
  "seat_type": "institution",
  "buy_amount": 80000000,
  "sell_amount": 0,
  "net_amount": 80000000,
  "rank": 1,
  "confidence": 0.9,
  "classification_basis": "机构专用席位标识"
}
```

Fields:

- `seat_id`: Unique identifier for the trading seat
- `seat_name`: Human-readable name (Chinese)
- `seat_type`: `"institution"`, `"hot_money"`, `"unknown"`, `"data_needed"`
- `buy_amount`: Buy volume in CNY
- `sell_amount`: Sell volume in CNY
- `net_amount`: Net position change (buy - sell)
- `rank`: Position in top buy/sell list (1 = largest)
- `confidence`: Float 0-1 indicating classification certainty
- `classification_basis`: Reason for seat type classification

### 3.2 Seat Type Classification

| Type | Definition | Classification Criteria |
|------|------------|------------------------|
| `institution` | Institutional investor | Seat name contains "机构", "基金", "保险", "社保" |
| `hot_money` | 游资/短线资金 | Known hot-money seat names, high-frequency LHB presence |
| `unknown` | Cannot classify | No classification data available |
| `data_needed` | No seat data | hoxit does not expose seat-level detail |

### 3.3 Current Limitation

**hoxit currently provides stock-level LHB data only**, not seat-level detail. The target seat schema above is for future implementation when seat data becomes available through hoxit APIs.

## 4. Analysis Framework

### 4.1 Institution vs Hot-Money Classification

When seat data is available:

**Institutional Indicators**:
- Seat name contains institutional keywords
- Consistent buy/sell patterns over time
- Large position sizes
- Lower trading frequency

**Hot-Money Indicators**:
- Known 游资 seat names
- High-frequency LHB appearances
- Short holding periods
- Theme-driven trading patterns

### 4.2 Buy/Sell Seat Interpretation

**Buy-Side Analysis**:
- Top buyer concentration: High → potential institutional accumulation
- Multiple institutions buying → strong fundamental case
- Hot money leading buy → short-term momentum play

**Sell-Side Analysis**:
- Institutional selling → potential profit-taking or fundamental concern
- Hot money exiting → short-term reversal risk
- High sell concentration → distribution pattern

### 4.3 Board and Peer Leadership Comparison

**Leadership Assessment**:
- Compare stock's LHB activity vs industry peers
- Check if stock is leading or following sector moves
- Assess if LHB activity is stock-specific or sector-wide

**Peer Comparison Data**:
- Use `hoxit.signals.industry_comparison` for sector context
- Compare change_pct, turnover_rate, net_buy amounts
- Identify if stock is sector leader or laggard

## 5. Fallback: Partial LHB Data

### 5.1 When Only Stock-Level Data Available

Current hoxit provides:

- Stock appeared on LHB
- Date and basic metrics (change_pct, turnover, amounts)
- LHB reason (涨幅偏离、跌幅偏离、换手率达20%)

**Fallback analysis**:

1. Report basic LHB metrics
2. Cross-reference with fund flow data
3. Check block trade activity
4. Note that seat-level analysis requires additional data

### 5.2 When No LHB Data Available

- Report as `data_needed`
- Suggest checking different date
- Do not fabricate LHB records

## 6. Deferred: Missing hoxit APIs

### 6.1 Seat Database API

**Status**: Deferred

UZI-Skill maintains a database of known trading seats with:

- Seat classification (institution, hot money, unknown)
- Historical LHB frequency
- Trading pattern profiles
- Known affiliations

**hoxit gap**: No seat database API exists.

**Future implementation**: Add `hoxit.signals.seat_profile()` with:

```python
def seat_profile(seat_id: str) -> dict:
    """
    Returns:
    - seat_name: str
    - seat_type: "institution" | "hot_money" | "unknown"
    - lhb_frequency: int (appearances in last 90 days)
    - avg_holding_days: float
    - known_themes: list[str]
    """
```

### 6.2 Peer Ranking API

**Status**: Deferred

UZI-Skill ranks stocks within sectors by:

- LHB frequency
- Institutional interest level
- Momentum strength
- Theme relevance

**hoxit gap**: No peer ranking API exists.

**Future implementation**: Add `hoxit.signals.peer_ranking()` with:

```python
def peer_ranking(code: str, sector: str) -> dict:
    """
    Returns:
    - rank: int
    - total_peers: int
    - metrics: dict (lhb_count, institutional_interest, momentum)
    - top_peers: list[dict]
    """
```

### 6.3 Historical LHB Pattern API

**Status**: Deferred

UZI-Skill analyzes LHB patterns over time:

- Seat loyalty (same seat appears repeatedly)
- Buy-sell timing patterns
- Success rate of LHB-based trades

**hoxit gap**: No historical pattern API exists.

## 7. Output Contract

### 7.1 Current Output

```json
{
  "lhb_data": {
    "trade_date": "2026-06-14",
    "code": "600519",
    "net_buy": 50000000,
    "reason": "涨幅偏离值达7%的证券"
  },
  "analysis": {
    "lhb": {
      "status": "computed",
      "rows": 1,
      "net_buy": 2000.0,
      "has_dragon_tiger": true,
      "signals": ["龙虎榜净买入为正", "龙虎榜共 1 条记录"],
      "warnings": []
    }
  }
}
```

### 7.2 LHB Summary (analysis["lhb"])

Deterministic LHB summary derived from `sources.signals.dragon_tiger`:

- `status`: `"computed"` or `"data_needed"`
- `rows`: Number of dragon-tiger records
- `net_buy`: Sum of net buy amounts across all rows
- `has_dragon_tiger`: Whether any records exist
- `signals`: Simple signals (net buy/sell/balance, row count)
- `warnings`: Data quality warnings

Limitations:
- No seat-level identity inference (institution vs 游资)
- No historical pattern analysis
- No peer comparison

### 7.2 Target Output (When Seat Data Available)

```json
{
  "lhb_data": {...},
  "seats": {
    "buy_side": [...],
    "sell_side": [...]
  },
  "classification": {
    "institutional_interest": "high",
    "hot_money_activity": "low",
    "confidence": 0.8
  },
  "peer_context": {
    "sector_rank": 3,
    "total_peers": 20,
    "leadership": "follower"
  }
}
```

## 8. Execution Protocol

### 8.1 CLI Invocation

```bash
hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD [--agent-analysis <json-file>] [--output-dir <path>]
```

### 8.2 Current Execution Flow

1. Validate stock code (6 digits, A-share)
2. Validate trade-date is provided
3. Call `hoxit.uzen.collect_snapshot()` with `mode="lhb-analyzer"`
4. Call `hoxit.uzen.analyze_snapshot()` which processes LHB data
5. Write `<code>-lhb-analyzer.json` and `<code>-lhb-analyzer.md`
6. Return artifact paths

### 8.3 Interpretation Rules

When interpreting LHB output:

- **Do**: Report LHB metrics as provided by hoxit
- **Do**: Cross-reference with fund flow and block trade data
- **Do**: Note when seat-level analysis is unavailable
- **Don't**: Invent seat classifications without data
- **Don't**: Claim institutional interest without seat evidence
- **Don't**: Fabricate historical patterns or success rates
