# PR10A Review — Macro / Top-Down Proxy

Review time: 2026-06-03 11:03:49 Asia/Shanghai
Reviewer: Codex
Status: Needs fixes before acceptance

## Scope

Reviewed PR10A implementation for `/tos-funder-macro-topdown`.

Files reviewed:

- `tos-funder/commands/tos-funder-macro-topdown.md`
- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr10a.md`
- `tos-funder/SKILL.md`
- `tos-funder/commands/tos-funder-analyze.md`
- `tos-funder/references/agent-taxonomy.md`
- `tos-funder/references/skill-workflow.md`
- `docs/tos-funder/quick-guide.md`

## What Is Good

PR10A has the right architecture and restraint:

- `/tos-funder-macro-topdown` exists with frontmatter.
- `macro_topdown_signal` schema exists.
- `SKILL.md`, `tos-funder-analyze.md`, `agent-taxonomy.md`, and `skill-workflow.md` route the new command.
- The validation includes a `Data Coverage Probe`, which was the most important requirement.
- The implementation avoids full macro prediction and keeps CPI/PMI/rates/FX/futures/options out of scoring.
- Index OHLCV failure via mootdx is documented, and iWencai index-return fallback is documented.
- The command does not use dead `event/business/management` routes.

However, the current delivery is not internally consistent enough to accept.

## Findings

### 1. Coverage Probe Says Breadth Is Verified, But Samples And Schema Treat Breadth As Missing

Files:

- `docs/tos-funder/validation-pr10a.md`
- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`

Coverage Probe:

```text
Market Breadth Proxy:
Result: ✅ WORKS — returns 上涨家数:1903, 下跌家数:3509, 涨停家数:68, 跌停家数:12
Status: verified
```

But BYD sample says:

```text
Market breadth | live_verified | ✅
...
Only 1 dimension scorable
Coverage Gate triggered: <2 verified dimensions
```

And the schema example says:

```json
"missing_context": ["market_breadth", "style_rotation", "risk_appetite"],
"data_sources": {
  "breadth": {"status": "missing"}
},
"breadth_context": {
  "status": "missing"
}
```

Problem:

This contradicts the probe. If breadth is live verified, then macro-topdown has at least:

- index trend
- market breadth

That is two verified dimensions. The Coverage Gate should not say "only 1 dimension verified" for the main samples.

Required fix:

Choose one consistent truth:

Option A, preferred:

- Treat breadth as verified and score it.
- In BYD/Moutai/Ningbo samples:
  - verified dimensions = index + breadth
  - coverage gate should not trigger for `<2 verified dimensions`
  - breadth score should reflect `上涨家数=1903, 下跌家数=3509`.
  - advance/decline ratio ≈ `1903 / 3509 = 0.54`, which is weak but not below the current `<0.5` bearish threshold unless CC chooses to define a "mild negative" tier.

Option B:

- If breadth was not collected for sample runs, mark it as `accepted_probe_only` or `not_used_in_sample`.
- Do not list it as `live_verified` in sample tables.
- Explain why verified probe data was excluded from sample scoring.

Given the command is supposed to use breadth as one of the primary proxies, Option A is better.

### 2. Confidence Calculation Is Not Arithmetic

Files:

- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr10a.md`

Current BYD schema example:

```json
"base_confidence": 40,
"verification_bonuses": [
  {"source": "index_bars", "value": 15, "applied": true},
  {"source": "industry_tag", "value": 5, "applied": true}
],
"pre_cap_confidence": 60,
"caps_applied": [
  {"gate": "coverage_gate", "cap": 50}
],
"final_confidence": 45,
"note": "Coverage gate cap (50) reduces confidence from 60 to 50... final_confidence = min(60, 50) = 50, then effective 45 reflecting partial coverage."
```

Problem:

The documented formula does not include an "effective 45" haircut. If `pre_cap=60` and cap is 50, final confidence should be 50. The current `45` is unexplained and violates the deterministic confidence rule.

Required fix:

Use one deterministic result.

If using index + tag only:

```text
40 + 15 + 5 = 60
coverage cap 50
final_confidence = 50
```

If using index + breadth + tag:

```text
40 + 15 + 10 + 5 = 70
no <2 verified cap
final_confidence = 70
```

If CC wants a partial-coverage haircut, it must be an explicit adjustment in `confidence_calculation.adjustments[]`. But PR10A does not need that extra complexity; keep the current cap model.

### 3. Sector Strength Is Marked Verified And Degraded At The Same Time

Files:

- `docs/tos-funder/validation-pr10a.md`
- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`

Current language:

```text
Sector strength: ✅ verified (⚠️ degraded)
Status: verified (basicinfo), degraded (sector strength ranking format)
```

Problem:

This is ambiguous. A downstream command cannot tell whether sector strength can be scored.

Required fix:

Split the status:

```json
"industry_basicinfo": {"status": "verified"}
"sector_strength": {
  "status": "degraded",
  "usable_for_scoring": false,
  "reason": "同花顺三级行业指数 format not stable enough for target-industry rank matching"
}
```

Then:

- industry tag bonus may apply
- sector strength score must be neutral/not scored unless target industry rank is actually matched

### 4. Risk Appetite Is Partial But Schema Example Marks It Missing

Files:

- `docs/tos-funder/validation-pr10a.md`
- `tos-funder/references/output-schema-examples.md`

Probe says:

```text
Risk appetite: partial — turnover available; northbound/margin unavailable
```

Schema example says:

```json
"risk_appetite": {"status": "missing"}
```

Required fix:

Use:

```json
"risk_appetite": {
  "status": "partial",
  "source": "iwc market query — turnover available; northbound/margin unavailable",
  "usable_for_scoring": false
}
```

If no 20d average turnover exists, do not score it, but do not call it missing.

### 5. Index Field Is Named `index_bars` Even Though Bars Are Unavailable

Files:

- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr10a.md`

Current schema:

```json
"index_bars": {"status": "verified", "source": "iwc market query — index returns"}
```

Problem:

This is semantically wrong. Bars are not verified; returns are verified. The probe explicitly says mootdx index bars fail.

Required fix:

Rename to:

```json
"index_returns": {"status": "verified", "source": "iwc market query"}
"index_bars": {"status": "unavailable", "source": "mootdx market bars"}
```

Also update confidence bonus wording:

```text
+15 if index returns verified
```

not:

```text
+15 if index bars verified
```

### 6. `coverage_status=partial` With Coverage Gate Triggered Is Ambiguous

Files:

- `tos-funder/references/macro-topdown.md`
- `tos-funder/references/output-schema-examples.md`
- `docs/tos-funder/validation-pr10a.md`

Reference says:

```text
If fewer than 2 dimensions are verified:
coverage_status = degraded
```

But schema/validation say:

```text
coverage_status = partial
coverage_gate triggered — fewer than 2 verified dimensions
```

Required fix:

Use consistent mapping:

```text
verified: 3+ verified scoring dimensions
partial: 2 verified scoring dimensions
degraded: 1 verified scoring dimension
blocked: no verified index returns
```

Then update samples accordingly.

If breadth is used, the main stock samples are likely `partial`.
If breadth is not used, they are `degraded`.

### 7. Output Schema Section May Be Misleading About Missing Context

File:

- `tos-funder/references/output-schema-examples.md`

The BYD example currently says breadth is missing even though the probe says breadth is verified. This is the same root problem as Finding 1, but it matters because `output-schema-examples.md` is the canonical schema reference.

Required fix:

Update `macro_topdown_signal` example to match the chosen truth:

Preferred:

```json
"missing_context": ["style_rotation"],
"degraded_context": ["sector_strength", "risk_appetite"],
"data_sources": {
  "index_returns": {"status": "verified"},
  "index_bars": {"status": "unavailable"},
  "industry_basicinfo": {"status": "verified"},
  "sector_strength": {"status": "degraded", "usable_for_scoring": false},
  "breadth": {"status": "verified", "usable_for_scoring": true},
  "style_rotation": {"status": "missing"},
  "risk_appetite": {"status": "partial", "usable_for_scoring": false}
}
```

## CC Fix Instructions

```text
PR10A-fix: 统一 Data Coverage Probe 与 samples/schema 的覆盖口径

必须修复：

1. 统一 breadth 口径。
   - Probe 已验证 breadth 可用：上涨家数=1903, 下跌家数=3509, 涨停=68, 跌停=12。
   - 在 command/reference/schema/validation 中把 breadth 标为 verified，并纳入可评分维度。
   - 或者如果你决定 sample 不使用 breadth，必须把 sample source_status 改为 not_used_in_sample，并解释原因。
   - 推荐采用 verified + scored。

2. 修正 confidence 计算。
   - 不允许出现 `final_confidence=45` 但 note 写 `min(60,50)=50` 的矛盾。
   - 如果采用 index + breadth + industry tag：
     base 40 + index 15 + breadth 10 + tag 5 = 70
     若 verified dimensions >=2，不触发 coverage cap
     final_confidence = 70（除非另有明确 cap）
   - 如果不采用 breadth：
     base 40 + index 15 + tag 5 = 60
     coverage cap 50
     final_confidence = 50
   - 推荐采用 index + breadth + tag → final_confidence around 70。

3. 拆分 `index_returns` 与 `index_bars`。
   - `index_returns`: verified via iWencai market query
   - `index_bars`: unavailable via mootdx market bars
   - 把 confidence bonus 从 `index_bars verified` 改为 `index_returns verified`。

4. 拆分 industry tag 与 sector strength。
   - `industry_basicinfo.status = verified`
   - `sector_strength.status = degraded`
   - `sector_strength.usable_for_scoring = false`，除非你能稳定匹配 target industry rank。

5. 修正 risk appetite。
   - Probe 是 partial，不是 missing。
   - 因为缺少 20d avg / northbound / margin，默认 `usable_for_scoring=false`。

6. 统一 coverage_status 映射：
   - verified: 3+ verified scoring dimensions
   - partial: 2 verified scoring dimensions
   - degraded: 1 verified scoring dimension
   - blocked: no verified index returns

7. 更新以下文件：
   - tos-funder/commands/tos-funder-macro-topdown.md
   - tos-funder/references/macro-topdown.md
   - tos-funder/references/output-schema-examples.md
   - docs/tos-funder/validation-pr10a.md

修复后运行并贴结果：

rg -n 'index_bars.*verified|final_confidence\": 45|confidence: ~45|breadth.*missing|market_breadth.*missing|risk_appetite.*missing|fewer than 2 verified dimensions|only 1 dimension|only index trend dimension|coverage_status: partial.*Coverage Gate|coverage_gate.*fewer than 2' tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10a.md

rg -n 'index_returns|index_bars.*unavailable|breadth.*verified|risk_appetite.*partial|usable_for_scoring|coverage_status|market_regime' tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md tos-funder/references/output-schema-examples.md docs/tos-funder/validation-pr10a.md

rg -n 'PMI|CPI|利率|汇率|期货|期权|美债|美元|FOMC|macro forecast|预测宏观|final_action|\"action\"|\"stance\": \"buy\"|\"signal\": \"buy\"|query2data|query -r event|query -r business|query -r management|weak_bullish|strong_bearish' tos-funder/commands/tos-funder-macro-topdown.md tos-funder/references/macro-topdown.md docs/tos-funder/validation-pr10a.md
```

## Verdict

PR10A is not accepted yet.

The shape is good and the probe is valuable, but the command/schema/validation currently contradict the probe. Fix the coverage/status/scoring consistency before moving on.

---

## Re-Audit After PR10A-fix

Review time: 2026-06-03 Asia/Shanghai
Reviewer: Codex
Status: Needs tiny validation table cleanup before acceptance

### What Is Fixed

The substantive issues from the first review are fixed.

1. Breadth is now consistently treated as a verified scoring dimension.
   - Probe: `上涨家数=1903`, `下跌家数=3509`, `涨停家数=68`, `跌停家数=12`.
   - Samples now score breadth as verified.
   - Main stock samples now have 2 scoring dimensions: index + breadth.

2. `index_returns` and `index_bars` are correctly separated.
   - `index_returns = verified` via iWencai market query.
   - `index_bars = unavailable` via mootdx market bars.
   - Confidence bonus now correctly references `index_returns`, not bars.

3. Sector context is clearer.
   - `industry_basicinfo` is verified.
   - `sector_strength` is degraded and `usable_for_scoring=false`.
   - Sector rank is not scored unless target-industry rank can be stably matched.

4. Risk appetite is clearer.
   - `risk_appetite = partial`.
   - `usable_for_scoring=false` because northbound/margin are unavailable and 20d turnover average is not consistently available.

5. Coverage status mapping is now consistent.
   - `verified`: 3+ scoring dimensions.
   - `partial`: 2 scoring dimensions.
   - `degraded`: 1 scoring dimension.
   - `blocked`: no verified index returns.

6. BYD/Moutai/Ningbo samples now show:
   - `coverage_status=partial`
   - `confidence=70`
   - no coverage cap because index + breadth are both verified.

7. Schema example now reflects the same truth:
   - `missing_context=["style_rotation"]`
   - `degraded_context=["sector_strength", "risk_appetite"]`
   - `breadth.status=verified`
   - `risk_appetite.status=partial`
   - `final_confidence=70`

### Remaining Issue

`docs/tos-funder/validation-pr10a.md` has two markdown table separators with one extra column.

#### Probe Summary Table

Current header has 5 columns:

```text
| Category | Status | Source | Usable for Scoring | Notes |
```

Current separator has 6 columns:

```text
|---|---|---|---|---|---|
```

Required:

```text
|---|---|---|---|---|
```

#### Sample Source Status Summary Table

Current header has 8 columns:

```text
| 样本 | Index Returns | Industry Tags | Sector Strength | Breadth | Style | Risk Appetite | Scoring Dims | source_status |
```

Correction: This header actually has 9 columns, so the current 9-column separator is correct. No change needed there.

The `rg` match on the sample source table is acceptable. Only the Probe Summary table separator is actually wrong.

### CC Fix Instructions

```text
PR10A-fix2: 修复 validation-pr10a Probe Summary 表格 separator

只改一个文件：
- docs/tos-funder/validation-pr10a.md

在 Probe Summary 表中，把：
|---|---|---|---|---|---|

改为：
|---|---|---|---|---|

不要改 Sample Source Status Summary 表。那个表有 9 列，当前 separator 是正确的。

运行并贴结果：
rg -n '^\\| Category \\| Status \\| Source \\| Usable for Scoring \\| Notes \\||^\\|---\\|---\\|---\\|---\\|---\\|---\\|' docs/tos-funder/validation-pr10a.md

预期：
- Category header 仍出现。
- 6-column separator 不再出现。
```

### Re-Audit Verdict

PR10A-fix resolves the real logic issues. PR10A is acceptable after the single Probe Summary markdown table cleanup. No further architecture change is needed.

---

## Re-Audit After PR10A-fix2 - 2026-06-03

### Verdict

Not accepted yet.

The architecture and PR10A logic remain acceptable, and no previous substantive issue appears to have regressed. However, the requested PR10A-fix2 markdown cleanup was not actually applied.

### Evidence

`docs/tos-funder/validation-pr10a.md:95-96` still shows:

```text
| Category | Status | Source | Usable for Scoring | Notes |
|---|---|---|---|---|---|
```

The header has 5 columns, but the separator still has 6 columns.

Required:

```text
| Category | Status | Source | Usable for Scoring | Notes |
|---|---|---|---|---|
```

### Scope Check

No other stale PR10A-fix issues were found in this re-audit:

- No stale `final_confidence=45` sample remains.
- No `index_bars` verified wording remains in the active schema/sample logic.
- Breadth is no longer treated as missing in the active validation samples.
- The remaining `breadth_context.status = "missing"` references are generic fallback branches in `macro-topdown.md`, not contradictions in PR10A validation.

### CC Fix Instructions

```text
PR10A-fix3: 只修复 Probe Summary 表格 separator

只改一个文件：
- docs/tos-funder/validation-pr10a.md

只改一行：
- 第 96 行附近，把：
  |---|---|---|---|---|---|

  改为：
  |---|---|---|---|---|

不要修改 Sample Source Status Summary 表；那个表是 9 列，当前 separator 正确。
不要修改 PR10A 的 command、reference、schema 或样例逻辑。

修复后运行：
sed -n '95,96p' docs/tos-funder/validation-pr10a.md
rg -n '^\\|---\\|---\\|---\\|---\\|---\\|---\\|$' docs/tos-funder/validation-pr10a.md

预期：
sed 输出应为：
| Category | Status | Source | Usable for Scoring | Notes |
|---|---|---|---|---|

rg 应无输出。
```

### PM Note

This is a small documentation hygiene issue, but it matters because the audit/fix loop is meant to be mechanically verifiable. CC should avoid replying "fixed" before running the exact acceptance command and checking that the expected output matches.

---

## Re-Audit After PR10A-fix3 - 2026-06-03

### Verdict

Accepted.

PR10A-fix3 correctly fixes the remaining Probe Summary markdown table separator issue.

### Verification

`sed -n '95,96p' docs/tos-funder/validation-pr10a.md` now returns:

```text
| Category | Status | Source | Usable for Scoring | Notes |
|---|---|---|---|---|
```

The exact stale 6-column separator check returns no matches:

```text
rg -n '^\\|---\\|---\\|---\\|---\\|---\\|---\\|$' docs/tos-funder/validation-pr10a.md
```

Additional stale-state scan found no active regression for:

- `final_confidence=45`
- `confidence: ~45`
- `index_bars.*verified`
- `market_breadth.*missing`
- `only 1 dimension`
- `coverage_gate.*fewer than 2`

### Final PR10A Status

PR10A Macro / Top-Down Proxy is accepted.

The implementation is now consistent with the intended architecture:

- It remains a lightweight A-share top-down proxy, not a macro forecasting engine.
- It separates verified index returns from unavailable index bars.
- It scores usable breadth, while keeping sector strength / style / risk appetite degraded or unscored when data quality is insufficient.
- It exposes macro/top-down context without producing final portfolio action.
