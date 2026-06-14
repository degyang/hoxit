# PR11 Review: Final Hardening

Created: 2026-06-03 13:37:18 Asia/Shanghai

## Verdict

Not accepted yet.

PR11 is close. The hardening pass did the important work:

- Created `docs/tos-funder/validation-pr11.md`.
- Built command inventory and schema anchor checks.
- Classified enum drift / confidence shape / final action boundary / dead route / data source boundary checks.
- Fixed `tos-funder-analyze.md` quant routing.
- Removed the risk-manager example's output-level `action` field and kept final action responsibility with analyze/portfolio.
- Updated `quick-guide.md` to say PR11 completed and next action is practical usage.

One restart-document contradiction remains. Because `quick-guide.md` is the primary re-entry file after context loss, this should be fixed before accepting PR11.

## Findings

### 1. `quick-guide.md` still marks all `management` route usage as dead/unusable

Severity: Medium

Files:

- `docs/tos-funder/quick-guide.md:216-222`
- `docs/tos-funder/validation-pr11.md:123-144`
- `tos-funder/commands/tos-funder-value-buffett.md:88-92`
- `tos-funder/commands/tos-funder-value-graham.md:54-60`
- `tos-funder/commands/tos-funder-quant-fundamentals.md:84`

`validation-pr11.md` correctly says:

```text
Dead routes: event query2data, business, management insider fields.
management usage limited to validated fields (分红, 股本, 股东人数).
```

Current `quick-guide.md` says:

```text
Dead or unreliable routes:

- `business`
- `event query2data`
- `management`

Do not use them unless a later validation explicitly revives them.
```

This is too broad and contradicts both the accepted commands and PR11 validation. Current active commands legitimately use `management` for validated fields:

- 分红
- 股本
- 股东人数
- 回购 / 总股本 / 流通A股 where already documented in accepted commands

The unreliable part is **management insider fields**, especially:

- 高管持股
- 质押
- 减持
- 股权激励

Expected fix:

Update `docs/tos-funder/quick-guide.md` to distinguish:

```text
Dead or blocked routes:
- `business`
- `event query2data`
- `management` insider fields: 高管持股 / 质押 / 减持 / 股权激励

Allowed validated `management` fields:
- 分红
- 股本
- 股东人数
- 回购 / 总股本 / 流通A股 where already used by accepted commands

Rule:
- Do not use management for insider/pledge/reduction/incentive fields.
- Narrow validated management queries are allowed when already documented in accepted value/fundamental commands.
```

### 2. `quick-guide.md` timestamp is stale

Severity: Low

File:

- `docs/tos-funder/quick-guide.md:3`

Current:

```text
Updated: 2026-06-03 11:40:06 Asia/Shanghai
```

But PR11 changed the guide after that. This is minor, but since quick-guide is explicitly a restart document, update it to the PR11 completion time.

Expected:

```text
Updated: 2026-06-03 13:37:18 Asia/Shanghai
```

or the actual fix timestamp.

## Checks Run

### PR11 Validation / Quick Guide

```text
sed -n '1,260p' docs/tos-funder/validation-pr11.md
sed -n '1,260p' docs/tos-funder/quick-guide.md
```

Result:

- `validation-pr11.md` is structurally complete.
- `quick-guide.md` is updated for PR11 progress, but its management route boundary is stale/overbroad.

### Targeted Boundary Check

```text
rg -n 'management|Updated:|PR11 Final Hardening|Next action|Dead or unreliable routes' \
  docs/tos-funder/quick-guide.md \
  docs/tos-funder/validation-pr11.md \
  tos-funder/commands/tos-funder-value-buffett.md \
  tos-funder/commands/tos-funder-value-graham.md \
  tos-funder/commands/tos-funder-quant-fundamentals.md
```

Evidence:

- `quick-guide.md:220` marks whole `management` route as dead/unreliable.
- `validation-pr11.md:135-144` marks validated management fields as allowed.
- active commands still use `hoxit iwc query -r management` for validated fields.

### Spot Checks Passed

- `tos-funder-analyze.md` quant route now explicitly includes:
  - `/tos-funder-quant-fundamentals`
  - `/tos-funder-quant-technicals`
  - `/tos-funder-quant-sentiment`
- `tos-funder-risk-manager.md` no longer emits a separate output-level `action` field; it uses `action_constraints.action_ceiling`.

## CC Fix Instructions

```text
PR11-fix: 修复 quick-guide 的 management route 边界表述

只改一个文件：
- docs/tos-funder/quick-guide.md

修复 2 件事：

1. 更新时间戳
   - 将顶部 Updated 时间改为本次修复时间。

2. 修正 Data Source Boundaries 中的 dead/unreliable routes
   当前 quick-guide 把整个 `management` route 标为不可用，这是错的。

   改成：

   Dead or blocked routes:
   - `business`
   - `event query2data`
   - `management` insider fields: 高管持股 / 质押 / 减持 / 股权激励

   Allowed validated `management` fields:
   - 分红
   - 股本
   - 股东人数
   - 回购 / 总股本 / 流通A股 where already documented in accepted value/fundamental commands

   Rule:
   - Do not use management for insider/pledge/reduction/incentive fields.
   - Narrow validated management queries are allowed when already documented in accepted commands.

不要修改命令逻辑。
不要重写 validation-pr11。

修复后运行并贴结果：

sed -n '1,12p' docs/tos-funder/quick-guide.md
sed -n '206,230p' docs/tos-funder/quick-guide.md
rg -n 'Dead or blocked routes|Allowed validated `management` fields|management` insider fields|高管持股|分红|股本|股东人数' docs/tos-funder/quick-guide.md

预期：
- 顶部 Updated 时间已更新。
- quick-guide 不再把整个 `management` route 标为禁止。
- quick-guide 明确区分 validated management fields 与 insider-field dead zone。
```

## PM Guidance For CC

The hardening report itself is good. The remaining issue is about restart safety: the next agent will read `quick-guide.md` first. If it says "`management` is dead", it will incorrectly avoid accepted Buffett/Graham/fundamental command paths. The guide must encode the nuanced boundary, not the old blanket rule.

---

## Re-Audit After PR11-fix - 2026-06-03

### Verdict

Accepted.

PR11-fix resolves the remaining quick-guide restart-safety issue.

### Verification

`docs/tos-funder/quick-guide.md` timestamp is updated:

```text
Updated: 2026-06-03 13:45:00 Asia/Shanghai
```

The data source boundary now correctly distinguishes blocked routes from validated management fields:

```text
Dead or blocked routes:
- `business`
- `event query2data`
- `management` insider fields: 高管持股 / 质押 / 减持 / 股权激励

Allowed validated `management` fields:
- 分红
- 股本
- 股东人数
- 回购 / 总股本 / 流通A股 where already documented in accepted value/fundamental commands

Rule:
- Do not use management for insider/pledge/reduction/incentive fields.
- Narrow validated management queries are allowed when already documented in accepted commands.
```

Targeted `rg` confirms:

- `Dead or blocked routes` is present.
- `Allowed validated management fields` is present.
- The guide no longer marks the entire `management` route as forbidden.

### Final PR11 Status

PR11 Final Hardening is accepted.

The restart document, validation report, command routing, final action boundary, data source boundary, and audit trail are now aligned.
