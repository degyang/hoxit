# UZEN Agent Instructions

Use UZEN for A-share stock research workflows only.

## Rules

- Prefer `hoxit.uzen` or `hoxit uzen` commands.
- Do not call UZI's original provider chain as the primary path.
- Do not add one-off scrapers under `uzen-skills`; add reusable A-share data capabilities to hoxit first.
- If a requested capability is outside first-version scope, report it as deferred instead of fabricating data.
- Reports are informational and must not present unsupported investment advice.

## Required Data Boundary

Use hoxit modules first:

- `hoxit.market`
- `hoxit.valuation`
- `hoxit.fundamentals`
- `hoxit.reports`
- `hoxit.news`
- `hoxit.filings`
- `hoxit.signals`
- `hoxit.iwencai`
