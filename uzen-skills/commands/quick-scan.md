# quick-scan

Run a compact A-share scan.

## Execution Path

```bash
hoxit uzen quick-scan <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls only 6 providers:
- quote, metrics, valuation, fundamentals
- concept, fund_flow

Skipped providers use neutral defaults (`{}` or `[]`).

## Focus Areas

Quote, valuation, capital flow, themes, and risk flags.

## Output

- `<code>-quick-scan.json` — Compact snapshot
- `<code>-quick-scan.md` — Compact Markdown report

## Mode Profile

- depth: `lite`
- primary_section: `summary`
