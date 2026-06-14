# PR9B Review — Tactical Synthesizer

Review time: 2026-06-03 10:24:19 Asia/Shanghai
Reviewer: Codex
Status: Needs fixes before acceptance

## Scope

Reviewed PR9B implementation for `/tos-funder-tactical`.

Files reviewed:

- `tos-funder/commands/tos-funder-tactical.md`
- `tos-funder/references/tactical-synthesis.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr9b.md`
- `tos-funder/SKILL.md`
- `tos-funder/commands/tos-funder-analyze.md`
- `tos-funder/references/agent-taxonomy.md`
- `tos-funder/references/skill-workflow.md`
- `docs/tos-funder/quick-guide.md`

## What Is Good

PR9B is structurally complete:

- `/tos-funder-tactical` exists with frontmatter.
- `tactical_synthesis_signal` schema exists in `output-schema-examples.md`.
- `SKILL.md`, `tos-funder-analyze.md`, `agent-taxonomy.md`, and `skill-workflow.md` route the new command.
- The command correctly treats PR8A catalyst and PR9A tail-risk outputs as the primary inputs.
- The main architectural boundaries are present:
  - low tail risk is not bullish
  - report polarization blocks bullish synthesis
  - data-quality anomaly is not bearish
  - tactical stance is not portfolio action

However, several consistency and rule-priority issues need fixing before acceptance.

## Findings

### 1. Output JSON Example Is Malformed

Files:

- `tos-funder/commands/tos-funder-tactical.md`
- `tos-funder/references/output-schema-examples.md`

In the BYD sample JSON, `confidence_calculation.adjustments` is missing a closing brace:

```json
"adjustments": [
  {"rule": "aligned_signals", "value": 5, "reason": "Both catalyst and tail-risk are neutral"
],
```

Required:

```json
"adjustments": [
  {"rule": "aligned_signals", "value": 5, "reason": "Both catalyst and tail-risk are neutral"},
  {"rule": "price_confirmation_gate", "value": -10, "reason": "price confirmation gate triggered"}
],
```

The schema examples must remain parseable enough for downstream readers. Even when embedded in markdown, malformed JSON examples become bad implementation guidance for CC.

### 2. BYD Confidence Calculation Is Inconsistent

Files:

- `tos-funder/commands/tos-funder-tactical.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr9b.md`

Current BYD validation says:

```text
base = 58
+5 aligned
-10 price_confirmation
= 53
```

But the sample JSON says:

```json
"confidence": 52,
"confidence_calculation": {
  "base_confidence": 58,
  "adjustments": [
    {"rule": "aligned_signals", "value": 5}
  ],
  "final_confidence": 52
}
```

Problems:

1. The `-10 price_confirmation` adjustment is missing from the JSON.
2. `58 + 5 - 10 = 53`, not 52.
3. The validation text says expected confidence is `~53`, while the JSON says 52.

Required fix:

Use one deterministic result everywhere. Recommended:

```json
"confidence": 53,
"confidence_calculation": {
  "base_confidence": 58,
  "details": "round((55 + 60) / 2) = 58",
  "adjustments": [
    {"rule": "aligned_signals", "value": 5, "reason": "Both catalyst and tail-risk are neutral"},
    {"rule": "price_confirmation_gate", "value": -10, "reason": "price confirmation gate triggered"}
  ],
  "caps_applied": [
    {"gate": "data_quality", "scope": "synthesis", "cap": 60, "reason": "adjustment_status=suspect — stricter upstream cap applied"}
  ],
  "final_confidence": 53
}
```

If CC wants to keep 52, it must document the missing arithmetic step. There is no reason to do that here; use 53.

### 3. Rule 1 vs Rule 7 Priority Is Not Defined In Command/Reference

Files:

- `tos-funder/commands/tos-funder-tactical.md`
- `tos-funder/references/tactical-synthesis.md`
- `docs/tos-funder/validation-pr9b.md`

Validation sample 4 says:

```text
When tail-risk is critical but catalyst is missing, Rule 1 should take precedence over Rule 7.
```

That is the correct decision for `000820 *ST节能`.

But the command/reference still say:

```text
If catalyst output is missing: signal = blocked, stance = blocked
Do not synthesize from only one side unless explicitly marked as partial and signal = blocked.
```

This conflicts with sample 4. If the command follows Rule 7 strictly, `000820` becomes blocked instead of bearish, even though PR9A independently verified critical tail risk.

Required fix:

Add explicit priority:

```text
Rule priority:
1. Critical tail-risk override runs before missing catalyst handling.
2. If tail-risk output is available and independently verifies critical event risk, missing catalyst output does NOT block synthesis.
3. In that case:
   signal = bearish
   tactical_stance.stance = avoid
   conflict_resolution.state = risk_overrides_opportunity
   missing_data includes catalyst
   synthesis_mode = "risk_only_critical_override"
4. Missing tail-risk output still blocks synthesis because risk veto cannot be evaluated.
5. Missing catalyst output blocks only non-critical cases.
```

Add `synthesis_mode` to schema:

```json
"synthesis_mode": "full | risk_only_critical_override | blocked_missing_input"
```

Then update sample 4 accordingly.

### 4. Validation Acceptance Table Separator Has One Extra Column

File:

- `docs/tos-funder/validation-pr9b.md`

Current:

```text
| # | 条件 | BYD | 茅台 | 宁波银行 | *ST节能 |
|---|---|---|---|---|---|---|
```

Header has 6 columns; separator has 7.

Required:

```text
| # | 条件 | BYD | 茅台 | 宁波银行 | *ST节能 |
|---|---|---|---|---|---|
```

### 5. Action-Term Self Check Needs More Precise Reporting

Files:

- `docs/tos-funder/validation-pr9b.md`
- possibly CC delivery summary

The PR9B instruction asked for `rg` against:

```text
final_action|buy|sell|hold|reduce|reject
```

These terms can appear in explanatory "do not output buy/sell" text and in inherited unrelated docs. That is acceptable only if there is no output schema field or tactical example using them as tactical result values.

Required fix:

In `validation-pr9b.md`, add a short section:

```text
Action-term rg interpretation:
- Matches for "buy/sell/hold/reduce/reject" appear only in constraint text or unrelated command docs.
- `tactical_synthesis_signal` does not contain final_action.
- `tactical_stance.stance` only uses favorable/watch/cautious/avoid/blocked.
- No output example uses buy/sell/hold/reduce/reject as tactical stance or signal.
```

## CC Fix Instructions

```text
PR9B-fix: 修复 tactical synthesis schema/example/rule priority 一致性

必须修复：

1. 修复 BYD sample JSON 的 `confidence_calculation.adjustments` 结构错误。
   - 文件：
     - tos-funder/commands/tos-funder-tactical.md
     - tos-funder/references/output-schema-examples.md
   - 补上 missing `}`。
   - 增加 `price_confirmation_gate` 的 -10 adjustment。

2. 统一 BYD confidence 为 53。
   - `base_confidence=58`
   - `+5 aligned`
   - `-10 price_confirmation_gate`
   - data_quality cap=60 不改变 53
   - `confidence=53`
   - `final_confidence=53`
   - 更新：
     - tos-funder/commands/tos-funder-tactical.md
     - tos-funder/references/output-schema-examples.md
     - docs/tos-funder/validation-pr9b.md

3. 明确 Rule 1 与 Rule 7 优先级。
   - Critical tail-risk override must run before missing catalyst handling.
   - Missing catalyst does NOT block if tail-risk independently verifies critical event risk.
   - Missing tail-risk still blocks synthesis.
   - Missing catalyst blocks non-critical synthesis.
   - Add `synthesis_mode`:
     - `full`
     - `risk_only_critical_override`
     - `blocked_missing_input`
   - Update:
     - tos-funder/commands/tos-funder-tactical.md
     - tos-funder/references/tactical-synthesis.md
     - tos-funder/references/output-schema-examples.md
     - docs/tos-funder/validation-pr9b.md

4. 修复 validation-pr9b Acceptance Criteria 表格 separator。
   - 改成 6 列：
     |---|---|---|---|---|---|

5. 在 validation-pr9b.md 添加 action-term rg interpretation。
   - 明确 buy/sell/hold/reduce/reject 只能出现在约束说明中，不能出现在 tactical_synthesis_signal 输出字段值中。

修复后运行并贴结果：

rg -n '"confidence": 52|"final_confidence": 52|price_confirmation_gate|risk_only_critical_override|blocked_missing_input|\\|---\\|---\\|---\\|---\\|---\\|---\\|---\\|' tos-funder/commands/tos-funder-tactical.md tos-funder/references/tactical-synthesis.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr9b.md

rg -n 'final_action|\"stance\": \"buy\"|\"stance\": \"sell\"|\"stance\": \"hold\"|\"stance\": \"reduce\"|\"stance\": \"reject\"|\"signal\": \"buy\"|\"signal\": \"sell\"' tos-funder/commands/tos-funder-tactical.md tos-funder/references/tactical-synthesis.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr9b.md

rg -n 'query2data|query -r event|query -r business|query -r management|weak_bullish|strong_bearish|weak_sell|strong_buy' tos-funder/commands/tos-funder-tactical.md tos-funder/references/output-schema-examples.md
```

## Verdict

PR9B is not accepted yet.

The tactical synthesis architecture is in the right shape, but the current delivery has a malformed JSON example, confidence arithmetic drift, and an unresolved critical-risk-vs-missing-input priority conflict. Fix those before moving to PR10A.

---

## CC Fix Response (2026-06-03)

All 5 issues resolved:

### Fix 1 — BYD JSON `adjustments` Malformed

Fixed in `tos-funder/commands/tos-funder-tactical.md` and `tos-funder/references/output-schema-examples.md`:
- Added missing closing `}` to the `adjustments` array element
- Added `price_confirmation_gate` -10 adjustment entry

### Fix 2 — BYD Confidence Unified to 53

Updated in 3 files (command, output-schema-examples, validation-pr9b):

```text
base_confidence = 58
adjustments: +5 (aligned) + -10 (price_confirmation_gate) = 53
cap: data quality → min(53, 60) = 53
final_confidence = 53
```

### Fix 3 — Rule 1 vs Rule 7 Priority

Added explicit rule priority to `tos-funder/references/tactical-synthesis.md`:

```
Priority 1: Critical tail-risk override (Rule 1) runs before missing catalyst handling (Rule 7)
            → missing catalyst does NOT block if tail-risk independently verifies critical risk
Priority 2: Remaining rules (Rule 2-6) apply based on input data conditions
Priority 3: Missing tail-risk blocks synthesis; missing catalyst blocks non-critical cases only
```

Added `synthesis_mode: full | risk_only_critical_override | blocked_missing_input` to:
- `tos-funder/references/tactical-synthesis.md` (schema + rule priority)
- `tos-funder/commands/tos-funder-tactical.md` (Rule 7, required fields table, JSON example)
- `tos-funder/references/output-schema-examples.md` (JSON example, key fields table)
- `docs/tos-funder/validation-pr9b.md` (sample 4 expected outcome, constitution self-review)

### Fix 4 — Table Separator

Fixed `docs/tos-funder/validation-pr9b.md` Acceptance Criteria separator from 7 columns to 6.

### Fix 5 — Action-Term rg Interpretation

Added section in `docs/tos-funder/validation-pr9b.md` with explicit rg results explanation.

### rg Acceptance Checks

```
# Check 1: no old confidence:52, verify new fields
grep '"confidence": 52|price_confirmation_gate|risk_only_critical_override|synthesis_mode'
→ All matches are correct new fields (price_confirmation_gate, risk_only_critical_override, synthesis_mode)
→ No remaining "confidence": 52 or "final_confidence": 52

# Check 2: no action terms as output values
grep 'final_action|"stance": "buy"|"stance": "sell"|"stance": "hold"'
→ Matches only in constraint text ("no final_action"), validation checklist, and unrelated schemas
→ tactical_synthesis_signal has no action-term output values

# Check 3: no dead routes / new enums in tactical files
grep 'query2data|query -r event|weak_bullish|strong_bearish'
→ Matches only in unrelated sentiment schemas in output-schema-examples.md
→ No matches in tos-funder-tactical.md or tactical-synthesis.md
```

**Status**: All 5 fixes verified. PR9B ready for re-review.

---

## Re-Audit After PR9B-fix

Review time: 2026-06-03 Asia/Shanghai
Reviewer: Codex
Status: Accepted

### Verification

Reviewed the PR9B fix across:

- `tos-funder/commands/tos-funder-tactical.md`
- `tos-funder/references/tactical-synthesis.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr9b.md`

The previous blockers are resolved:

1. BYD sample JSON is now structurally valid.
   - `confidence_calculation.adjustments[]` entries are closed correctly.
   - `price_confirmation_gate` is present as a `-10` adjustment.

2. BYD confidence arithmetic is now consistent.
   - `base_confidence = 58`
   - `+5 aligned_signals`
   - `-10 price_confirmation_gate`
   - data-quality cap `60` does not change the result
   - `confidence = 53`
   - `final_confidence = 53`

3. Rule 1 vs Rule 7 priority is now defined in command and reference.
   - Critical tail-risk override runs before missing catalyst handling.
   - Missing catalyst does not block synthesis when tail-risk independently verifies critical event risk.
   - Missing tail-risk still blocks synthesis.
   - `synthesis_mode` now covers:
     - `full`
     - `risk_only_critical_override`
     - `blocked_missing_input`

4. `validation-pr9b.md` Acceptance Criteria table separator is fixed.

5. Action-term interpretation is documented.
   - `tactical_synthesis_signal` does not contain `final_action`.
   - `tactical_stance.stance` uses only `favorable/watch/cautious/avoid/blocked`.
   - No tactical output example uses `buy/sell/hold/reduce/reject` as a stance or signal value.

### Residual Notes

The `rg` check for dead routes returns matches inside unrelated `sentiment_output` examples in `output-schema-examples.md`, such as:

```text
event query2data is BLOCKED — announcement search used instead
```

These are not PR9B issues. `/tos-funder-tactical` itself does not query dead routes and only consumes structured proxy outputs.

Sample 4 validation still includes a row explaining the strict Rule 7 blocked behavior, followed by the priority note. This is acceptable because the command and reference now explicitly define Rule 1 priority over Rule 7 for independently verified critical tail risk.

### Final Verdict

PR9B Tactical Synthesizer is accepted.

Accepted behavior:

1. Tactical synthesis consumes PR8A catalyst and PR9A tail-risk outputs.
2. Low tail risk does not create bullish output.
3. Report polarization cannot drive bullish synthesis.
4. Data-quality anomalies do not become bearish evidence.
5. Critical tail-risk overrides opportunity and can proceed in `risk_only_critical_override` mode when catalyst is missing.
6. Tactical stance remains analytical and does not become final portfolio action.

Recommended next PR: PR10A Macro/Top-Down Proxy, limited to A-share index trend, sector strength, market breadth, style rotation, and risk-appetite proxies. Do not attempt full Druckenmiller-style macro prediction until macro data coverage is explicitly validated.
