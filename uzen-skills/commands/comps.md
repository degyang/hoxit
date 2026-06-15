# comps

Run peer and industry comparison.

## Execution Path

```bash
hoxit uzen comps <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls 4 providers:
- quote, metrics, fundamentals, industry

## Output

- `<code>-comps.json` — Industry-focused snapshot
- `<code>-comps.md` — Compact Markdown report

## Mode Profile

- depth: `focused`
- primary_section: `industry`

## Notes

Current behavior uses `hoxit.signals.industry_comparison` for peer data.

iwencai peer fallback is deferred — not wired into UZEN comps runtime.
