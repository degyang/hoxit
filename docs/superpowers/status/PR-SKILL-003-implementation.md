# PR-SKILL-003 Implementation Report

## Status

COMPLETED

## Branch

`agent/cc/pr-skill-003-uzen-trap-detector-protocol`

## Commit

`<hash>` — `docs: rewrite uzen trap detector protocol`

## Scope Delivered

Rewrote trap detector skill and command documentation with market risk vs trap risk distinction.

### Files Changed

| File | Before | After |
|------|--------|-------|
| `uzen-skills/skills/trap-detector/SKILL.md` | 6 lines (placeholder) | 192 lines (full protocol) |
| `uzen-skills/commands/scan-trap.md` | 7 lines (minimal) | 69 lines (detailed) |
| `docs/superpowers/status/PR-SKILL-003-implementation.md` | — | This report |

### Protocol Sections

1. **Risk Category Distinction** — Market risk vs trap risk, current scope clarification
2. **Supported hoxit Inputs** — 8 data sources with risk relevance mapping
3. **Deferred: UZI-Style Social/Manipulation Evidence** — Social sentiment, keyword monitoring, manipulation patterns
4. **Output States** — `clear`, `watch`, `risk`, `data_needed` semantics
5. **No-Fabrication Rule** — Strict rules for market signals and social claims
6. **Execution Protocol** — CLI invocation, execution flow, interpretation rules

## Acceptance Criteria

- [x] Skill no longer presents hoxit market-risk flags as full UZI trap detection (§1.1 explicitly distinguishes market risk from trap risk)
- [x] Missing social evidence is explicitly represented (§3.1-3.2 mark all social evidence as deferred)
- [x] Protocol is A-share-first and hoxit-first (§2 hoxit data boundary, §5 no-fabrication rule)
- [x] Implementation report records summary, files changed, verification command, and deferred gaps

## Verification

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-003-implementation.md
# Output: no whitespace errors
```

## Deferred Gaps

- Social sentiment analysis (WeChat, forums, media)
- Keyword monitoring for manipulation terms
- Fake news detection algorithms
- Influencer/paid promotion tracking
- Evidence URL collection infrastructure
- Manipulation pattern recognition
