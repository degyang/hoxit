# lhb-analyzer

Run dragon-tiger-board focused analysis.

## Execution Path

```bash
hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD --output-dir uzen-skills/reports
```

## Required Parameters

- `code`: 6-digit A-share stock code
- `--trade-date`: Date of LHB data (`YYYY-MM-DD` format)

## Current Behavior

First-version LHB analysis using hoxit stock-level data.

### Data Inputs

- Dragon-tiger board from `hoxit.signals.dragon_tiger_board`
- Daily dragon-tiger from `hoxit.signals.daily_dragon_tiger`
- Fund flow from `hoxit.signals.baidu_fund_flow_history`
- Block trades from `hoxit.signals.block_trade`
- Margin trading from `hoxit.signals.margin_trading`
- Lockup expiry from `hoxit.signals.lockup_expiry`

### Output

- `<code>-lhb-analyzer.json` — Structured LHB data
- `<code>-lhb-analyzer.md` — Markdown summary

### Current Limitations

- Stock-level data only (no seat-level detail)
- No seat classification (institution vs hot money)
- No peer ranking or leadership comparison
- No historical pattern analysis

## What This Does

- Reports LHB appearance and basic metrics
- Cross-references with fund flow and block trade data
- Identifies LHB reason (涨幅偏离、跌幅偏离、换手率达20%)
- Notes data availability and gaps

## What This Does Not Do

- Classify individual trading seats
- Identify institutional vs hot-money activity
- Compare stock leadership within sector
- Analyze historical LHB patterns

## Future Enhancements

See `uzen-skills/skills/lhb-analyzer/SKILL.md` for:
- Target seat schema with classification
- Institution vs hot-money analysis framework
- Board and peer leadership comparison
- Deferred hoxit APIs (seat database, peer ranking)
