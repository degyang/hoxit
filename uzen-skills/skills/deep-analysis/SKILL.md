---
name: deep-analysis
description: A-share stock research workflow backed by hoxit. Use for analyze-stock, quick-scan, dcf, comps, panel-only, scan-trap, and lhb-analyzer requests.
---

# UZEN Deep Analysis Protocol

This is the master A-share UZEN workflow protocol. It defines how agents execute stock research using hoxit as the primary data substrate.

## 1. Scope and Boundaries

### 1.1 A-Share Only

UZEN first version supports A-share stocks only. If a request targets Hong Kong, US, futures, ETF, convertible bonds, or other non-A-share instruments:

- Do not attempt the analysis.
- Report the market as deferred.
- Do not fabricate data or fall back to non-hoxit sources.

### 1.2 hoxit-First Data Boundary

All data must come from hoxit modules first:

| Layer | Module | Primary Functions |
|-------|--------|-------------------|
| Quote/K-line | `hoxit.market` | `mootdx_quote`, `mootdx_bars`, `tencent_metrics` |
| Valuation | `hoxit.valuation` | `full_valuation`, `forward_pe`, `calc_peg` |
| Fundamentals | `hoxit.fundamentals` | `individual_info`, `finance_snapshot`, `f10` |
| Research | `hoxit.reports` | `eastmoney_reports`, `iwencai_search` |
| News | `hoxit.news` | `stock_news`, `cls_flash`, `global_news` |
| Filings | `hoxit.filings` | `cninfo_reports` |
| Signals | `hoxit.signals` | `ths_hot_reason`, `baidu_concept_blocks`, `baidu_fund_flow_history`, `dragon_tiger_board`, `lockup_expiry`, `industry_comparison`, `margin_trading`, `block_trade`, `holder_num_change`, `dividend_history` |
| Fallback | `hoxit.iwencai` | `query_rows`, `search_rows` |

If hoxit cannot cover a capability, mark it as deferred. Do not add one-off scrapers under `uzen-skills`.

### 1.3 Agent Role

The agent acts as:

- **Analyst**: Interpret data, identify patterns, assess risks.
- **Protocol executor**: Follow this workflow consistently across sessions.
- **Quality gate**: Enforce hard gates before producing output.

The agent does not act as:

- A financial advisor.
- A data source.
- A predictor of market movements.

## 2. Command Routing

### 2.1 Available Commands

| Command | Mode | Primary Section | Depth |
|---------|------|-----------------|-------|
| `analyze-stock` | Full A-share report | `full_report` | standard |
| `quick-scan` | Compact scan | `summary` | lite |
| `dcf` | Light DCF valuation view | `valuation` | focused |
| `comps` | Peer/industry comparison | `industry` | focused |
| `panel-only` | Investor-panel summary | `panel` | focused |
| `scan-trap` | Market data risk scan | `market_risk` | focused |
| `lhb-analyzer` | Dragon-tiger-board analysis | `dragon_tiger` | focused |

### 2.2 CLI Invocation

```bash
hoxit uzen <command> <code> [--trade-date YYYY-MM-DD] [--agent-analysis <json-file>] [--output-dir <path>]
```

Default output directory: `uzen-skills/reports/`

`--agent-analysis` accepts a JSON file containing an optional qualitative analysis envelope (see §6.4).

### 2.3 Mode Selection

- Use `analyze-stock` for comprehensive analysis.
- Use `quick-scan` for rapid assessment or when only key metrics are needed.
- Use focused modes (`dcf`, `comps`, `panel-only`, `scan-trap`, `lhb-analyzer`) when the user explicitly requests a specific dimension.

## 3. Execution Order

### 3.1 Input Validation

Before executing any command:

1. **Code validation**: Stock code must be 6 digits (A-share format). Reject invalid codes.
2. **Market check**: Confirm A-share. Reject non-A-share with deferred status.
3. **Trade date**: For `lhb-analyzer`, `--trade-date` is required. Default to today if not specified for other commands.

### 3.2 Data Collection

Execute `hoxit.uzen.collect_snapshot()` which:

1. Calls `provider.quote([code])` for real-time price.
2. Calls `provider.bars(code)` for K-line data.
3. Calls `provider.metrics([code])` for PE/PB/market cap.
4. Calls `provider.valuation(code)` for forward PE/PEG.
5. Calls `provider.fundamentals(code)` for basic info.
6. Calls `provider.finance(code)` for financial snapshot.
7. Calls `provider.f10(code)` for F10 data (may return unsupported).
8. Calls `provider.reports(code)` for research reports.
9. Calls `provider.news(code)` for news articles.
10. Calls `provider.filings(code, start, end)` for regulatory filings.
11. Calls signal providers for hot themes, concept blocks, fund flow, dragon-tiger, lockup, industry, margin trading, block trades, holder changes, dividends.

Each call is wrapped in `_safe_call()` — exceptions become warnings, not failures.

### 3.3 Analysis

Execute `hoxit.uzen.analyze_snapshot()` which:

1. Extracts summary (name, price, change_pct).
2. Computes panel summary with 5 investor signals (score, verdict, reasons, signals, vote_distribution).
3. Computes market risk (level, basis, flags) from observable market data.
4. Computes trap risk (status, basis, evidence, warnings) — currently unsupported.
5. Computes DCF valuation (intrinsic value, margin of safety, sensitivity, input_quality).
6. Computes comps summary (median PE/PB, position, input_quality).
7. Computes LHB summary (rows, net_buy, signals) for lhb-analyzer mode.
8. Assigns mode profile (depth, primary_section).
9. Includes agent_analysis envelope if provided.

### 3.4 Rendering

Execute `hoxit.uzen.render_markdown()` which produces mode-specific sections. Each mode only renders relevant sections:

| Mode | Visible Sections |
|------|-----------------|
| `analyze-stock` | All sections |
| `quick-scan` | Core, data quality, market/valuation, fundamentals, capital flow, followups |
| `dcf` | Core, data quality, market/valuation, fundamentals, DCF, followups |
| `comps` | Core, data quality, market/valuation, fundamentals, industry, comps, followups |
| `panel-only` | Core, data quality, market/valuation, fundamentals, panel, followups |
| `scan-trap` | Core, data quality, market/valuation, fundamentals, market risk, trap risk, followups |
| `lhb-analyzer` | Core, data quality, market/valuation, fundamentals, capital flow, LHB, followups |

All modes include the investment disclaimer.

Available sections in order:
1. Core conclusion
2. Data completeness and caveats
3. Market and valuation
4. Fundamentals and financials
5. Research, news, and filings
6. Capital flow, dragon-tiger board, and hot themes
7. Industry and peer comparison
8. Investor panel summary (with vote distribution and individual signals)
9. Market data risk checks
10. Social/trap risk checks (currently unsupported)
11. DCF valuation (with input quality)
12. Peer comparison/comps (with input quality)
13. LHB analysis (lhb-analyzer mode only)
14. Agent qualitative analysis (when provided)
15. Follow-up watchlist

### 3.5 Artifact Review

Before delivering output:

1. Verify JSON artifact exists and is valid.
2. Verify Markdown artifact exists and has all required sections.
3. Verify no raw data fabrication occurred.
4. Verify qualitative judgments are separated from raw data.

## 4. Hard Gates

These gates must pass before producing output. If any gate fails, report the failure and stop.

### 4.1 Missing Code

If stock code is not provided or invalid:

- **Gate**: FAIL
- **Action**: Request valid 6-digit A-share code.
- **Do not**: Proceed with placeholder or fabricated code.

### 4.2 Unsupported Market

If stock is not A-share:

- **Gate**: FAIL
- **Action**: Report market as deferred.
- **Do not**: Attempt analysis with non-hoxit sources.

### 4.3 Missing Output Artifacts

If JSON or Markdown file cannot be written:

- **Gate**: FAIL
- **Action**: Report file system error.
- **Do not**: Return partial output.

### 4.4 Unsupported Data

If critical data source returns unsupported status (e.g., F10):

- **Gate**: WARN (not FAIL)
- **Action**: Include warning in `data_quality.warnings`, continue with available data.
- **Do not**: Fabricate missing data.

## 5. Data Integrity Rules

### 5.1 No Data Fabrication

Raw hoxit data must never be fabricated. This means:

- Do not invent price, PE, PB, or other numeric values.
- Do not create fake news articles, filings, or research reports.
- Do not generate plausible-sounding but unverified facts.
- If data is missing, report it as missing.

### 5.2 Separation of Judgment

Qualitative judgment must be separated from raw data:

- **Raw data**: Price, PE, fund flow amounts, filing dates — these come from hoxit.
- **Judgment**: "Valuation is attractive", "Risk is elevated", "Momentum is positive" — these are agent interpretations.
- **Rule**: Never present judgment as if it were raw data. Use clear language like "Based on PE of 15, the valuation appears reasonable" rather than "PE is 15, which means it's cheap."

### 5.3 Disclaimer

Every report must include:

```
> 本报告仅用于信息整理，不构成投资建议。
```

## 6. Output Contract

### 6.1 JSON Artifact

File: `<code>-<mode>.json`

Structure:
```json
{
  "code": "600519",
  "market": "A",
  "mode": "analyze-stock",
  "generated_at": "2026-06-14T00:00:00+08:00",
  "data_quality": {
    "complete": false,
    "warnings": [],
    "sources": {
      "quote": { "label": "quote", "quality": "full", "source": "provider.quote", "warnings": [], "required": true, "optional_missing": [] }
    }
  },
  "sources": {
    "quote": {},
    "bars": [],
    "metrics": {},
    "valuation": {},
    "fundamentals": {},
    "finance": {},
    "f10": {},
    "reports": [],
    "news": [],
    "filings": [],
    "signals": {}
  },
  "analysis": {
    "summary": { "name": "贵州茅台", "price": 1800.0, "change_pct": 1.5 },
    "valuation": {},
    "industry": { "rows": [] },
    "panel": {
      "score": 65,
      "verdict": "bullish",
      "reasons": ["价值投资者：PE 15.0 倍，估值偏低"],
      "signals": [
        { "investor_id": "value", "name": "价值投资者", "group": "fundamental", "signal": "pass", "score": 70, "confidence": 0.75, "reasoning": ["PE 15.0 倍，估值偏低"] }
      ],
      "vote_distribution": { "pass": 3, "fail": 0, "neutral": 1, "data_needed": 1 }
    },
    "market_risk": { "level": "low", "basis": "market_data", "flags": [] },
    "trap_risk": { "status": "unsupported", "basis": "social_evidence", "evidence": [], "warnings": ["社交/操纵证据采集尚未实现"] },
    "dcf": {
      "status": "computed",
      "inputs": { "market_price": 1800.0, "net_profit": 50000000000, "share_count": 1256197800, "growth_rate": 15.0 },
      "assumptions": { "discount_rate": { "value": 10.0 }, "terminal_growth": { "value": 3.0 } },
      "intrinsic_value_per_share": 2500.00,
      "market_price": 1800.0,
      "margin_of_safety": 38.89,
      "sensitivity": [],
      "input_quality": {
        "required": ["net_profit", "share_count"],
        "available": ["market_price", "net_profit", "share_count"],
        "missing": [],
        "proxy_used": ["net_profit_as_cash_flow"]
      },
      "warnings": []
    },
    "comps": {
      "status": "computed",
      "subject": { "name": "贵州茅台", "industry": "白酒", "pe_ttm": 30.0, "pb": 10.0 },
      "rows": [],
      "median_pe": 25.0,
      "median_pb": 5.0,
      "position": "above_median",
      "input_quality": {
        "peer_rows": 5,
        "pe_samples": 5,
        "pb_samples": 5,
        "missing": []
      },
      "warnings": []
    },
    "lhb": {
      "status": "computed",
      "rows": 1,
      "net_buy": 2000.0,
      "has_dragon_tiger": true,
      "signals": ["龙虎榜净买入为正"],
      "warnings": []
    },
    "agent_analysis": {
      "status": "not_provided",
      "basis": "agent_qualitative_input",
      "thesis": "",
      "assumptions": [],
      "conflicts": [],
      "followups": [],
      "warnings": []
    },
    "mode_profile": { "depth": "standard", "primary_section": "full_report" },
    "followups": []
  }
}
```

### 6.2 Markdown Artifact

File: `<code>-<mode>.md`

Contains all sections listed in §3.4, with stable ordering and investment disclaimer.

### 6.3 Mode-Specific Output

| Mode | JSON sections populated | Markdown sections included |
|------|------------------------|---------------------------|
| `analyze-stock` | All | All |
| `quick-scan` | All (lite) | Summary-focused |
| `dcf` | Valuation-focused | Valuation-focused |
| `comps` | Industry-focused | Industry-focused |
| `panel-only` | Panel-focused | Panel-focused |
| `scan-trap` | Risk-focused | Risk-focused |
| `lhb-analyzer` | Dragon-tiger-focused | Dragon-tiger-focused |

### 6.4 Agent Analysis Envelope

Optional qualitative analysis envelope. Does not modify raw data or deterministic analysis.

CLI: `--agent-analysis <json-file>`

States:
- `not_provided` (default): No agent analysis, no Markdown section rendered
- `provided`: Agent analysis present, renders "Agent 定性分析" section

Schema:
```json
{
  "status": "provided",
  "basis": "agent_qualitative_input",
  "thesis": "核心论点",
  "assumptions": ["假设1"],
  "conflicts": ["矛盾/风险1"],
  "followups": ["后续验证项1"],
  "warnings": []
}
```

Boundaries:
- Does not modify `sources`, `data_quality`, DCF, Comps, panel, risk objects
- Does not inject LLM calls
- JSON format only

## 7. Capability Status

### 7.1 Current (Phase 5)

- A-share stock analysis
- 7 command modes
- JSON and Markdown output
- Injectable data providers
- Unit-testable without network
- hoxit-first data boundary
- iwencai fallback through `hoxit.iwencai`
- DCF valuation (light model, 5-year explicit forecast + terminal value, input quality)
- Comparable company summary (median PE/PB, position, input quality)
- Market data risk flags (block trade, margin trading, holder changes, fund flow)
- 5 deterministic investor signals (value, quality, growth, momentum, hot-money)
- LHB summary (row count, net buy, simple signals)
- Mode-specific Markdown sections
- Agent analysis envelope (optional qualitative input)
- Dimension layer (10 deterministic dimension summaries)
- Deterministic synthesis (stance, confidence, drivers, risks, conflicts, followups)
- Report self-review (5 non-blocking artifact contract checks)
- Deep review envelope fields (data_gap_acknowledged, dimension_commentary, panel_insights)

### 7.2 Deferred (Not Implemented)

- HTML report rendering
- Share-card and war-report images
- Playwright/browser data repair
- Cloudflare remote hosting
- Full UZI 65-investor parity
- Social sentiment and manipulation evidence
- Historical dragon-tiger seat pattern analysis
- Deep DCF (Free Cash Flow), Comps (full peer set), LBO, IC Memo
- Portfolio commands (returns, rebalance)
- Cross-market support (HK, US, futures, ETF, convertible bonds)
- Optional packaging as Claude/Codex/Cursor/Gemini plugin

## 8. Relationship to Specialized Skills

This deep-analysis skill is the master protocol. Specialized skills (`investor-panel`, `lhb-analyzer`, `trap-detector`) handle specific dimensions but must:

- Follow the same data boundary rules.
- Respect the same hard gates.
- Produce output compatible with the JSON/Markdown contract.
- Not bypass hoxit with one-off scrapers.

When a specialized skill is invoked, it operates within the framework defined here.
