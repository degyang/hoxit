---
name: deep-analysis
description: A-share stock research workflow backed by hoxit. Use for analyze-stock, quick-scan, dcf, comps, panel-only, scan-trap, and lhb-analyzer requests.
---

# UZEN Deep Analysis

Use this skill for A-share stock research. The execution layer is `hoxit.uzen`.

## Guardrails

- A-share only in the first version.
- JSON and Markdown output first.
- Use hoxit data APIs first.
- Mark unavailable non-A-share or HTML/share-card requests as deferred.
