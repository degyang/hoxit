# Trading Funder Overview

Trading Funder is the hoxit A-share, skill-first adaptation of `Reference/ai-hedge-fund`.

It does not port LangGraph, the web app, the original CLI runtime, or Financial Datasets as the default data layer. Instead, it converts the original analyst logic into Claude Code skills and commands backed by hoxit A-share data routes.

## Goals

- Preserve the useful analyst strategies from ai-hedge-fund.
- Make every workflow executable as a Claude Code command.
- Use iWencai for fundamentals, valuation snapshots, announcements, and reports.
- Use hoxit `mootdx`/TDX for OHLCV, quote, intraday, technical, and risk workflows.
- Document missing data and A-share substitutions.
- Provide a framework that Claude Code can extend command by command.

## Directory Layout

```text
tos-funder/
  SKILL.md
  commands/
    tos-funder-analyze.md
    tos-funder-value-buffett.md
    tos-funder-portfolio.md
  references/
    agent-taxonomy.md
    iwencai-adapter.md
    price-series.md
    skill-workflow.md
    value-investors.md
    command-template.md

docs/tos-funder/
  00-overview.md
  01-interface-coverage.md
  02-architecture.md
  03-build-plan.md
  04-claude-code-guide.md
  05-sample-buffett-ningbo-bank.md
  06-cc-collaboration-plan.md
```

## Source Inputs

- Reference source: `$HOME/Projects/hoxit/Reference/ai-hedge-fund`
- A-share data reference: `$HOME/Projects/hoxit/Reference/a-stock-data`
- Real source path: `$HOME/Developments/ai-hedge-fund`
- POS analysis: `$YDG_CORE_VAULT/10-Projects/Tracking/11.27 AI Hedge Fund`
- hoxit iWencai routes: `hoxit/routes.json`
- hoxit market layer: `hoxit/market.py`

## Classification Decision

The POS five-category split is retained because it is useful for skill routing:

1. Value investors.
2. Growth investors.
3. Activist/macro investors.
4. Quantitative/systematic analysts.
5. Risk and portfolio managers.

This classification is better for Claude Code than source-file mirroring because each family maps to different command behavior, data routes, and output expectations.
