# UZEN Skills

UZEN is the A-share-first migration layer inspired by `Reference/UZI-Skill`.
It keeps the research workflow, command intent, investor-panel concept, and risk checks, but uses hoxit as the primary data substrate.

## Runtime Behavior

### Mode Execution Profiles

Each command only calls the data providers it needs. Skipped sources use neutral defaults (`{}` or `[]`).

| Mode | Providers Called |
|------|-----------------|
| `analyze-stock` | All 20 providers (full coverage) |
| `quick-scan` | quote, metrics, valuation, fundamentals, concept, fund_flow |
| `panel-only` | quote, metrics, valuation, fundamentals, finance |
| `scan-trap` | quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger |
| `lhb-analyzer` | quote, concept, fund_flow, dragon_tiger, block_trade, margin_trading, lockup |
| `dcf` | quote, metrics, valuation, fundamentals, finance |
| `comps` | quote, metrics, fundamentals, industry |

Unknown modes fall back to `analyze-stock` behavior.

### Source Quality Records

JSON output includes structured `data_quality.sources` with quality values:
- `full`: data present
- `partial`: partial data (e.g., F10 unsupported)
- `missing`: data absent
- `error`: provider exception
- `skipped`: mode skipped this source

Skipped sources do not affect the top-level `complete` flag.

### Markdown Report Contract

Markdown uses compact, human-readable formatting:
- Quote: name, latest price, change percent
- Valuation: forward PE, PEG, PE TTM, PB, market cap
- Fundamentals: industry, ROE, net profit
- Reports/news/filings: count + top 3 titles
- Concepts: comma-separated names
- Missing data: `缺失` or Chinese text

## Commands

- `analyze-stock`: full A-share report.
- `quick-scan`: compact report for quote, valuation, flow, themes, and risk.
- `dcf`: light valuation view.
- `comps`: peer and industry comparison.
- `panel-only`: investor-panel vote summary.
- `scan-trap`: trap and manipulation-risk scan.
- `lhb-analyzer`: dragon-tiger-board focused analysis.

## Current Limitations

- A-share only
- No HTML rendering or share images
- No full UZI 22-dimension parity
- No portfolio commands
- F10 data depends on mootdx support

## Deferred

- HTML reports and share images
- Playwright repair
- Full 65-investor panel
- Social sentiment and manipulation evidence
- Historical LHB seat patterns
- Cross-market analysis
