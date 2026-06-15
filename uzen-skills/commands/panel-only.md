# panel-only

Run investor-panel summary without the full report.

## Execution Path

```bash
hoxit uzen panel-only <code> --output-dir uzen-skills/reports
```

## Data Providers

Calls 5 providers:
- quote, metrics, valuation, fundamentals, finance

## Mode Profile

- depth: `focused`
- primary_section: `panel`

## Current Behavior

First-version lightweight panel based on valuation and financial quality metrics.

### Scoring Rules

- Base score: 50
- +10 if PE < 20 (attractive valuation)
- -15 if PE > 60 (expensive valuation)
- +10 if ROE ≥ 10 (quality earnings)

### Output

- `<code>-panel-only.json` — Structured panel data
- `<code>-panel-only.md` — Compact Markdown summary

### JSON Schema (Current)

```json
{
  "score": 50,
  "verdict": "neutral",
  "reasons": ["..."]
}
```

- `score`: Integer 0-100
- `verdict`: `"bullish"` (≥65), `"bearish"` (≤40), `"neutral"` (41-64)
- `reasons`: List of explanation strings

## Limitations

This is **not** equivalent to UZI's full 65-investor panel. It is a deterministic first-version approximation.

See `uzen-skills/skills/investor-panel/SKILL.md` for:
- Target investor signal schema
- Full UZI investor parity status
- Recommended future investor groups
