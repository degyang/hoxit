# PR-SKILL-003 Codex Review

Verdict: APPROVED

Date: 2026-06-15
Branch: `agent/cc/pr-skill-003-uzen-trap-detector-protocol`
Reviewed commit: `f3b6725 docs: rewrite uzen trap detector protocol`
Base: `main` at `a13d23d`

## Review Scope

Reviewed the branch diff against `main`:

- `uzen-skills/skills/trap-detector/SKILL.md`
- `uzen-skills/commands/scan-trap.md`
- `docs/superpowers/status/PR-SKILL-003-implementation.md`

This matches the PR ticket scope. No production code, tests, or later skill files were modified.

## Findings

No blocking findings.

Non-blocking notes:

- The implementation report's commit field still says `<hash>` instead of `f3b6725`. This is the same reporting issue seen in earlier PRs. It is not blocking for this documentation PR, but cc should record the actual commit hash in future reports.
- `uzen-skills/commands/scan-trap.md` lists several collected signal inputs, while current `_trap_risk()` scoring only uses block trades, margin trading, holder rows, and missing fund flow. The doc still describes the current scoring rules correctly, so this is not blocking; later runtime work should either consume the broader inputs or tighten the command doc.

## Acceptance Check

- `market_risk` and `trap_risk` are clearly distinguished.
- Supported hoxit market-risk inputs are documented.
- UZI-style social/manipulation evidence is explicitly deferred or data-needed.
- Evidence URL, keyword, confidence, and timestamp requirements are defined for future trap evidence.
- Output states `clear`, `watch`, `risk`, and `data_needed` are defined, with mapping to current `low`/`medium`/`high`.
- No-fabrication rules for social sentiment and manipulation claims are explicit.
- The command doc no longer presents hoxit market-risk flags as full UZI trap detection.

## Runtime Consistency Check

Codex checked the protocol against current `hoxit/uzen.py`:

- `collect_snapshot(..., mode="scan-trap")` is supported.
- `_trap_risk()` returns current `level` values of `low`, `medium`, or `high`.
- Current scoring is flag-count based: no flags is `low`, one or two flags is `medium`, and three or more flags is `high`.
- `run_analysis()` writes `<code>-scan-trap.json` and `<code>-scan-trap.md`.

The documentation is consistent with the current first-version runtime behavior and explicitly marks UZI-style trap evidence as deferred.

## Verification

Codex reran:

```bash
git diff --check -- uzen-skills docs/superpowers/status/PR-SKILL-003-implementation.md
```

Result: passed with no output.

## Decision

APPROVED.

PR-SKILL-003 establishes the A-share trap detector protocol and is suitable to merge before starting PR-SKILL-004.
