# PR11 Instruction: Final Hardening

Created: 2026-06-03 12:41:27 Asia/Shanghai

## Context

PR10B Portfolio / Decision Synthesizer has been accepted.

The `tos-funder` project now has the main architecture in place:

- value layer
- growth layer
- quant layer
- sentiment/event proxy layer
- tactical catalyst / tail-risk / synthesis layer
- macro/top-down proxy layer
- risk-manager layer
- portfolio decision layer

PR11 is not a new strategy PR. It is a final hardening pass to make the current skill reliable for daily Claude Code usage.

## Objective

Clean up and verify the whole `tos-funder` skill so that:

1. Command routing is complete and non-contradictory.
2. Output schemas are canonical and internally consistent.
3. Signal/action enums do not drift.
4. Upstream commands do not accidentally produce final portfolio actions.
5. Dead iWencai routes are not used in command execution paths.
6. iWencai vs mootdx/TDX boundaries are explicit and consistent.
7. Validation docs and audit docs provide a clear handoff trail.
8. The skill is ready for repeated practical use without requiring project-history context.

## Scope

This is a cleanup / verification PR.

Do not create new analyst strategies.
Do not add new investment personas.
Do not rewrite existing commands unless needed to remove contradictions or schema drift.
Do not change accepted decision rules unless a direct inconsistency is found.

## Files To Review And Update

Primary skill files:

- `tos-funder/SKILL.md`
- `tos-funder/commands/*.md`
- `tos-funder/references/*.md`

Project docs:

- `docs/tos-funder/quick-guide.md`
- `docs/tos-funder/validation-*.md`
- `docs/tos-funder/audit/*.md`

Create:

- `docs/tos-funder/validation-pr11.md`

Optional, only if useful:

- `docs/tos-funder/final-hardening-report.md`

## Required Hardening Areas

### 1. Command Inventory And Frontmatter

Inspect every command under:

```text
tos-funder/commands/*.md
```

For each command, confirm:

- frontmatter has `name`
- frontmatter has `description`
- frontmatter has `command: true`
- frontmatter has `argument-hint`
- frontmatter has `type: command`
- command name matches file intent
- command is listed in `tos-funder/SKILL.md`
- command is routed or referenced in `tos-funder/commands/tos-funder-analyze.md` when applicable
- command schema is mapped in `tos-funder/references/skill-workflow.md` when it produces a canonical schema

In `docs/tos-funder/validation-pr11.md`, include a command inventory table:

```text
| Command file | Frontmatter OK | SKILL route | Analyze route | Schema anchor | Notes |
```

### 2. Schema Anchor Consistency

Use `tos-funder/references/output-schema-examples.md` as the single source of truth.

Verify anchors for:

- `price_series_output`
- `risk_manager_output`
- `analyze_output`
- `portfolio_output`
- `sentiment_output`
- `growth_analyst_signal`
- `growth_aggregate_signal`
- `tactical_catalyst_signal`
- `tail_risk_signal`
- `tactical_synthesis_signal`
- `macro_topdown_signal`

Check `tos-funder/references/skill-workflow.md` maps each command to the correct anchor.

If a command has no canonical schema anchor but should, add or document it.

If a schema anchor exists but no command produces it, document whether it is legacy, future, or active.

### 3. Enum Drift Check

Allowed directional signal values:

```text
bullish
neutral
bearish
blocked
```

Allowed strength values:

```text
strong
medium
weak
flat
```

Allowed portfolio action values:

```text
buy
hold
sell
reduce
watch
reject
blocked
```

Allowed tactical stance values:

```text
favorable
watch
cautious
avoid
blocked
```

Important: tactical `avoid` is allowed only as `tactical_stance.stance`, not as portfolio `action`.

Run enum checks and record results:

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review\"" tos-funder docs/tos-funder
rg -n "\"action\"\\s*:\\s*\"(avoid|manual_review|trim|short|cover|strong_buy|weak_sell)\"" tos-funder docs/tos-funder
rg -n "\"signal\"\\s*:\\s*\"(weak_bullish|strong_bearish|buy|sell|hold|reduce|watch|reject)\"" tos-funder docs/tos-funder
```

Classify matches:

- active schema/command issue
- allowed tactical stance
- instruction/audit text only
- historical validation text

Fix active schema/command issues only.

Do not rewrite audit history just to remove old instruction text.

### 4. Confidence Shape Check

Top-level `confidence` must be integer `0-100`.

`confidence_calculation` may be an object, but top-level `confidence` must not be object-valued.

Run:

```bash
rg -n '"confidence"\\s*:\\s*\\{' tos-funder/commands tos-funder/references docs/tos-funder/validation-*.md
```

For every active command/schema example:

- ensure `confidence` is int
- ensure `confidence_calculation.final_confidence == confidence` when `confidence_calculation` exists

Historical audit files may contain old bad examples; do not edit audit history unless the current docs depend on it.

### 5. Final Action Boundary

Only these commands may produce action-level final decisions:

- `/tos-funder-analyze` may produce `final_action`
- `/tos-funder-portfolio` may produce `final_actions`

Upstream analyst/context commands must not produce final portfolio actions:

- value commands
- growth commands
- quant fundamentals / technicals / sentiment
- tactical commands
- macro topdown
- risk-manager

Run:

```bash
rg -n "final_action|final_actions|\"action\"\\s*:" tos-funder/commands tos-funder/references/output-schema-examples.md
```

Classify matches:

- allowed: analyze output
- allowed: portfolio output
- allowed: constraint text saying "does not produce final_action"
- issue: upstream command output schema includes final action

Fix active issues.

### 6. Dead iWencai Route Check

Dead or unreliable routes:

- `business`
- `event query2data`
- `management` insider fields

Run:

```bash
rg -n "query2data|query -r event|query -r business|query -r management|hoxit iwc query -r management" tos-funder/commands tos-funder/references
```

Rules:

- `event query2data` and `business` must not appear as executable command steps.
- `management` is allowed only for validated fields such as dividend/share-capital/shareholder-count where existing accepted commands already rely on it.
- `management` insider fields such as 高管持股/质押/减持 must remain marked unreliable or blocked.
- If a command still presents a dead route as executable without warning, fix it.

Do not remove historical reference documentation that explains why a route is dead.

### 7. Data Source Boundary Check

Confirm:

- fundamentals / valuation / announcements / reports use iWencai
- OHLCV / quote / intraday / technicals / risk metrics use mootdx/TDX
- iWencai OHLCV is fallback only
- technical indicators are computed locally from qfq OHLCV, not from iWencai indicator output
- risk-manager has no iWencai dependency

Run:

```bash
rg -n "RSI|MACD|ATR|OHLCV|mootdx|TDX|iwencai_fallback|iWencai fallback|hoxit iwc.*RSI|hoxit iwc.*MACD" tos-funder/commands tos-funder/references
```

Fix active contradictions.

### 8. Validation Document Index

In `docs/tos-funder/validation-pr11.md`, create a validation index table:

```text
| Validation doc | PR | Status | What it proves | Still active? |
```

Include at least:

- `validation-pr1.md`
- `validation-pr2a.md`
- `validation-pr5b.md`
- `validation-pr6a.md`
- `validation-pr8a.md`
- `validation-pr9a.md`
- `validation-pr9b.md`
- `validation-pr10a.md`
- `validation-pr10b.md`

Also mention any older validation docs that remain relevant or legacy.

### 9. Audit Trail Index

In `docs/tos-funder/validation-pr11.md`, create an audit index:

```text
| Audit file | PR | Type | Final status | Notes |
```

Include current accepted review files:

- `pr5b-20260603-001015.md`
- `pr8a-tactical-catalyst-review-20260603-002834.md`
- `pr9a-tactical-tail-risk-review-20260603-084817.md`
- `pr9b-tactical-synthesizer-review-20260603-102419.md`
- `pr10a-macro-topdown-proxy-review-20260603-110349.md`
- `pr10b-portfolio-decision-synthesizer-review-20260603-114954.md`

### 10. Quick Guide Finalization

Update `docs/tos-funder/quick-guide.md` so it can serve as the restart document after context loss.

It should clearly contain:

- accepted PR list
- current architecture
- command families
- data source boundaries
- review checklist
- how to resume work
- current next action

After PR11, current next action should become:

```text
Use tos-funder in practice and collect issues into the next improvement PR.
```

Do not leave quick-guide saying PR10B is merely submitted.

## Required `rg` Checks To Include In `validation-pr11.md`

Run and paste summarized results:

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review\"" tos-funder docs/tos-funder
rg -n "\"action\"\\s*:\\s*\"(avoid|manual_review|trim|short|cover|strong_buy|weak_sell)\"" tos-funder docs/tos-funder
rg -n "\"signal\"\\s*:\\s*\"(weak_bullish|strong_bearish|buy|sell|hold|reduce|watch|reject)\"" tos-funder docs/tos-funder
rg -n '"confidence"\\s*:\\s*\\{' tos-funder/commands tos-funder/references docs/tos-funder/validation-*.md
rg -n "final_action|final_actions|\"action\"\\s*:" tos-funder/commands tos-funder/references/output-schema-examples.md
rg -n "query2data|query -r event|query -r business|query -r management|hoxit iwc query -r management" tos-funder/commands tos-funder/references
rg -n "hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR|iWencai.*technical|iWencai.*技术指标" tos-funder/commands tos-funder/references
```

For each command, classify the result as:

- clean
- active issue fixed
- allowed reference/instruction text
- historical/audit only
- acceptable known exception

## Acceptance Criteria

PR11 is acceptable only if:

1. Every active command has valid frontmatter and routing.
2. Every active command maps to a schema or explicitly explains why not.
3. No active command introduces enum drift.
4. Top-level `confidence` remains integer.
5. Portfolio/analyze are the only final action layers.
6. Dead iWencai routes are not used as live execution paths.
7. Technical/risk workflows use mootdx/TDX, not iWencai indicators.
8. `quick-guide.md` reflects actual current progress.
9. `validation-pr11.md` provides a reusable final hardening report.
10. No accepted PR logic is weakened during cleanup.

## CC Delivery Summary Required

When finished, reply with:

```text
PR11 完成。

修改文件：
- ...

新增文件：
- docs/tos-funder/validation-pr11.md

检查结果摘要：
- command inventory: ...
- schema anchors: ...
- enum drift: ...
- confidence shape: ...
- final action boundary: ...
- dead route usage: ...
- data source boundary: ...
- quick-guide: ...

修复的问题：
- ...

保留的已知例外：
- ...

需要架构师复核的点：
- ...
```
