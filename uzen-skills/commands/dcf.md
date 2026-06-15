# dcf

Run the first-version light valuation view.

## Execution Path

```bash
hoxit uzen dcf <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls 5 providers:
- quote, metrics, valuation, fundamentals, finance

## Output

- `<code>-dcf.json` — Valuation-focused snapshot
- `<code>-dcf.md` — Compact Markdown report

## Mode Profile

- depth: `focused`
- primary_section: `valuation`

## Limitations

This first version uses available hoxit valuation and forecast fields. Full UZI DCF parity is deferred.
