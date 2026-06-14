# PR10B Review: Portfolio / Decision Synthesizer

Created: 2026-06-03 11:49:54 Asia/Shanghai

## Verdict

Not accepted yet.

PR10B correctly moves the architecture in the intended direction:

- `/tos-funder-portfolio` is framed as the only command producing final portfolio actions.
- The five-layer model is present: thesis, timing, tactical, macro, risk/portfolio constraints.
- The command now consumes value, growth, quant, sentiment, tactical, macro, and risk families.
- Routing updates are present in `SKILL.md`, `skill-workflow.md`, `agent-taxonomy.md`, `tos-funder-analyze.md`, and `quick-guide.md`.

However, several schema/math issues make the PR unsafe to accept as the canonical portfolio decision layer.

## Findings

### 1. `flat` strength multiplier is applied incorrectly in validation

Severity: High

Files:

- `docs/tos-funder/validation-pr10b.md:134`
- `docs/tos-funder/validation-pr10b.md:159`
- `tos-funder/commands/tos-funder-portfolio.md:124`
- `tos-funder/references/portfolio-synthesis.md:182`

The command/reference correctly define:

```text
flat = 0.0
```

But the 贵州茅台 validation sample computes:

```text
Technicals: -1.0 × 1.0 × 0.6 = -0.60 (flat = 1.0 mult but bearish flat → -1.0)
```

This contradicts the canonical multiplier table. If `strength=flat`, the technical contribution must be:

```text
-1.0 × 0.0 × 0.6 = 0.00
```

Expected fix:

- Correct the 贵州茅台 validation math.
- Recompute `timing_score`, `net_score`, consensus explanation if needed, and confidence/action reasoning if affected.
- Decide whether the sample should be `technicals=bearish (weak)` or `technicals=bearish (flat)`.
  - If `flat`, it must not contribute negative score.
  - If CC wants negative timing pressure, use `weak`, not `flat`.

### 2. `confidence` and `confidence_calculation.final_confidence` mismatch in portfolio examples

Severity: High

Files:

- `tos-funder/commands/tos-funder-portfolio.md:437-443`
- `tos-funder/references/output-schema-examples.md:656-664`

Both examples contain:

```json
"confidence": 55,
"confidence_calculation": {
  "base_confidence": 65,
  "adjustments": [
    {"rule": "divergent", "value": -12}
  ],
  "caps_applied": [],
  "final_confidence": 53
}
```

This violates PR10B's hard rule:

```text
confidence_calculation.final_confidence == confidence
```

Expected fix:

- Set top-level `confidence` to `53`, or set `final_confidence` to `55` with a mathematically valid derivation.
- Apply the same correction in both:
  - `tos-funder/commands/tos-funder-portfolio.md`
  - `tos-funder/references/output-schema-examples.md`
- Add a validation check in `docs/tos-funder/validation-pr10b.md` confirming all examples satisfy this equality.

### 3. `action_ceiling = min(action_ceiling, "...")` is not executable decision logic

Severity: Medium-High

File:

- `tos-funder/commands/tos-funder-portfolio.md:265-272`

Current pseudo-code:

```text
action_ceiling = min(action_ceiling, "reduce")
action_ceiling = min(action_ceiling, "reject")
action_ceiling = min(action_ceiling, "watch")
```

This is ambiguous because action strings do not have a natural ordering. It invites implementation drift: Python/string ordering or ad hoc interpretation would produce nonsensical priority.

Expected fix:

- Replace `min(action_ceiling, "...")` with an explicit action ceiling precedence table and helper rule.
- Example:

```text
action_ceiling_rank:
  blocked = 0
  reject = 1   # new-position terminal avoidance
  watch = 2
  reduce = 3   # existing-position max reduction
  hold = 4
  buy = 5
  none = 6

apply_ceiling(current, candidate, position_state):
  choose the more restrictive ceiling according to the table appropriate for new vs held position
```

Better:

```text
For new positions:
  blocked < reject < watch < buy

For existing positions:
  blocked < sell < reduce < hold < buy

Data-quality degraded:
  new: max watch
  held: max reduce, but sell blocked unless thesis independently bearish

Critical tail-risk:
  new: max reject/watch depending whether thesis/risk confirm
  held: max reduce; sell only if thesis bearish + genuine risk veto
```

The command should avoid implying that string `min()` is valid logic.

### 4. `risk_limits` is declared required but absent from canonical examples

Severity: Medium

Files:

- `tos-funder/commands/tos-funder-portfolio.md:345`
- `tos-funder/references/output-schema-examples.md:711`
- `tos-funder/references/output-schema-examples.md:576-706`
- `tos-funder/references/portfolio-synthesis.md:432-518`

The required fields table says `risk_limits` is required / always present, but the portfolio JSON examples do not include a `risk_limits` object.

Expected fix:

- Add `risk_limits` to the JSON examples in:
  - `tos-funder/commands/tos-funder-portfolio.md`
  - `tos-funder/references/portfolio-synthesis.md`
  - `tos-funder/references/output-schema-examples.md`

Minimum shape:

```json
"risk_limits": {
  "max_single_position_pct": 25.0,
  "max_sector_exposure_pct": 40.0,
  "min_cash_reserve_pct": 10.0,
  "correlation_multiplier": 1.0,
  "source": "risk_manager"
}
```

If unavailable, include it with explicit missing status:

```json
"risk_limits": {
  "status": "blocked",
  "reason": "risk-manager missing"
}
```

### 5. Validation claims missing required-input cases are covered, but only marks them `n/a`

Severity: Medium

File:

- `docs/tos-funder/validation-pr10b.md:412-413`

The acceptance table says:

```text
缺少 risk-manager 时 blocked: ✅ n/a
无方向性论点时 blocked: ✅ n/a
```

This is not a validation. PR10B made these hard behavior rules:

- missing risk-manager -> `final_actions[].action=blocked`
- no directional thesis layer -> `final_actions[].action=blocked`

Expected fix:

- Add a compact "Required Input Edge Cases" section with two mini fixtures:
  1. Missing risk-manager -> action `blocked`, confidence <= 30.
  2. Risk-manager present but all thesis layers missing/blocked -> action `blocked`, confidence <= 30.
- These do not need full four-stock sample detail, but they must show expected schema and reason.

## Checks Run

Targeted checks were run against PR10B files and updated routing:

```text
rg -n "flat|confidence\": 55|final_confidence\": 53|min\\(action_ceiling|confidence.*final_confidence|risk_limits" \
  tos-funder/commands/tos-funder-portfolio.md \
  tos-funder/references/portfolio-synthesis.md \
  tos-funder/references/output-schema-examples.md \
  docs/tos-funder/validation-pr10b.md
```

Key matches:

- `docs/tos-funder/validation-pr10b.md:159` uses `flat = 1.0`.
- `tos-funder/commands/tos-funder-portfolio.md:437-443` has confidence mismatch.
- `tos-funder/references/output-schema-examples.md:656-664` has confidence mismatch.
- `tos-funder/commands/tos-funder-portfolio.md:265-272` uses `min(action_ceiling, "...")`.
- `risk_limits` is declared required but missing from JSON examples.

Routing presence check passed:

- `SKILL.md` exposes portfolio as final action command.
- `skill-workflow.md` maps `/tos-funder-portfolio` to `#portfolio_output`.
- `agent-taxonomy.md` updates Risk/portfolio family.
- `tos-funder-analyze.md` routes portfolio to `/tos-funder-portfolio`.
- `quick-guide.md` points to PR10B as current submitted implementation.

## CC Fix Instructions

```text
PR10B-fix: 修复 Portfolio Decision Synthesizer 的 schema/math 一致性问题

只改这些文件：
- tos-funder/commands/tos-funder-portfolio.md
- tos-funder/references/portfolio-synthesis.md
- tos-funder/references/output-schema-examples.md
- docs/tos-funder/validation-pr10b.md

修复 5 件事：

1. 修复 flat multiplier
   - flat 必须等于 0.0。
   - validation-pr10b 的贵州茅台样例不能再写 flat=1.0。
   - 如果想表达轻微看跌技术面，改为 bearish (weak) 并按 weak=0.5 计算。
   - 如果保留 bearish (flat)，技术面贡献必须是 0.00。

2. 修复 confidence mismatch
   - 所有 portfolio examples 中：
     confidence_calculation.final_confidence 必须等于顶层 confidence。
   - 当前 600519 样例 confidence=55 / final_confidence=53 必须修正。
   - command example 和 output-schema example 都要同步。

3. 修复 action ceiling 伪代码
   - 删除 `min(action_ceiling, "reduce/reject/watch")` 这种字符串 min 写法。
   - 改成显式 action ceiling precedence：
     new position: blocked < reject < watch < buy
     held position: blocked < sell < reduce < hold < buy
   - 明确 data-quality degraded 和 critical tail-risk 的 ceiling 规则。

4. 补齐 risk_limits
   - risk_limits 被声明为 required/always present，JSON examples 必须包含。
   - 在 command、portfolio-synthesis、output-schema-examples 的 portfolio JSON 示例中添加 risk_limits。

5. 增加 required-input edge cases
   - 在 validation-pr10b 中新增两个小节：
     a. missing risk-manager -> final action blocked, confidence <= 30
     b. no directional thesis layer -> final action blocked, confidence <= 30
   - 不要只在 acceptance table 写 n/a。

修复后运行并贴结果：

rg -n 'flat = 1\\.0|flat.*1\\.0|final_confidence": 53|min\\(action_ceiling' tos-funder/commands/tos-funder-portfolio.md tos-funder/references/portfolio-synthesis.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10b.md

rg -n '"confidence": 55|final_confidence": 53|"risk_limits"' tos-funder/commands/tos-funder-portfolio.md tos-funder/references/portfolio-synthesis.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10b.md

rg -n 'missing risk-manager|no directional thesis|缺少 risk-manager|无方向性论点|blocked.*confidence.*30' docs/tos-funder/validation-pr10b.md

预期：
- 第一条 rg 不应再出现旧错误。
- 第二条 rg 应能看到 risk_limits，并且 600519 confidence/final_confidence 不再矛盾。
- 第三条 rg 应能看到两个 required-input edge case。
```

## PM Guidance For CC

This PR is architecturally on the right track, but portfolio is the final decision layer, so examples must be mechanically consistent. Treat every JSON sample as a contract. If a field table says "Always Present", the sample must include it. If a confidence rule says equality, every example must satisfy it. If pseudo-code could be interpreted as executable, it must avoid ambiguous string ordering.

---

## Re-Audit After PR10B-fix - 2026-06-03

### Verdict

Accepted.

PR10B-fix resolves the blocking schema/math issues identified in the first review.

### Verification Notes

#### 1. `flat` multiplier issue fixed

`docs/tos-funder/validation-pr10b.md` now uses `bearish (weak)` for the 贵州茅台 technical sample and computes:

```text
Technicals: -1.0 × 0.5 × 0.6 = -0.30
```

This is consistent with the canonical multiplier table:

```text
weak = 0.5
flat = 0.0
```

No stale `flat = 1.0` / `flat.*1.0` match remains in the PR10B target files.

#### 2. Confidence mismatch fixed

The 600519 portfolio examples now have matching top-level confidence and final confidence:

`tos-funder/commands/tos-funder-portfolio.md`:

```json
"confidence": 53,
"confidence_calculation": {
  "base_confidence": 65,
  "adjustments": [{"rule": "divergent", "value": -12}],
  "caps_applied": [],
  "final_confidence": 53
}
```

`tos-funder/references/output-schema-examples.md` has the same correction.

Note: the original review command `rg ... 'final_confidence": 53'` is too broad after the fix, because `53` can be a valid final confidence when top-level `confidence` is also `53`. The correct audit criterion is equality between `confidence` and `confidence_calculation.final_confidence`, not absence of value `53`.

#### 3. Action ceiling pseudo-code fixed

`tos-funder/commands/tos-funder-portfolio.md` no longer uses:

```text
min(action_ceiling, "...")
```

It now defines explicit action ceiling precedence:

```text
For new positions:
  blocked(0) < reject(1) < watch(2) < buy(3) < none(4)

For held positions:
  blocked(0) < sell(1) < reduce(2) < hold(3) < buy(4) < none(5)
```

The tactical and macro cap logic now applies explicit conditional rules instead of string ordering.

#### 4. `risk_limits` added

`risk_limits` now appears in the portfolio JSON examples:

- `tos-funder/commands/tos-funder-portfolio.md`
- `tos-funder/references/portfolio-synthesis.md`
- `tos-funder/references/output-schema-examples.md`

This resolves the previous mismatch where `risk_limits` was declared required but missing from examples.

#### 5. Required-input edge cases added

`docs/tos-funder/validation-pr10b.md` now includes compact edge cases:

- Missing risk-manager -> `action=blocked`, `confidence=30`
- No directional thesis layer -> `action=blocked`, `confidence=25`

The acceptance table still shows `n/a` for the original four stock samples, but now includes edge-case columns showing the required blocked behavior. This is acceptable.

### Residual Notes

Non-blocking:

- `output-schema-examples.md` still contains `final_confidence=53` in the tactical synthesis schema. That is unrelated to PR10B portfolio confidence and is not a regression.
- Generic references to `confidence: 55` remain across unrelated schemas and source signal examples. These are not top-level/final-confidence mismatches.

### Final PR10B Status

PR10B Portfolio / Decision Synthesizer is accepted.

The portfolio layer now satisfies the intended architecture:

- It is the only final portfolio action layer.
- It consumes the current value, growth, quant, sentiment, risk, tactical, and macro signal families.
- It separates thesis, timing, tactical context, macro context, and risk constraints.
- It keeps top-level `confidence` as an integer and preserves `confidence_calculation.final_confidence == confidence` in the portfolio examples.
- It keeps data-quality vetoes separate from genuine risk vetoes.
- It prevents macro/tactical context from bypassing thesis and risk logic.
