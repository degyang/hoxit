# UZEN Skills

UZEN is the A-share-first migration layer inspired by `Reference/UZI-Skill`.
It keeps the research workflow, command intent, investor-panel concept, and risk checks, but uses hoxit as the primary data substrate.

## First-Version Scope

- A-share stocks only.
- JSON and Markdown output first.
- hoxit Python APIs and CLI behavior are the primary execution path.
- iwencai fallback is allowed only through `hoxit.iwencai`.

## Commands

- `analyze-stock`: full A-share report.
- `quick-scan`: compact report for quote, valuation, flow, themes, and risk.
- `dcf`: light valuation view.
- `comps`: peer and industry comparison.
- `panel-only`: investor-panel vote summary.
- `scan-trap`: trap and manipulation-risk scan.
- `lhb-analyzer`: dragon-tiger-board focused analysis.

## Deferred

HTML reports, share images, Playwright repair, remote hosting, full UZI 22-dimension parity, portfolio commands, and non-A-share markets are recorded in `docs/superpowers/specs/2026-06-14-uzen-skills-design.md` for later phases.
