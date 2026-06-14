# PR12 Review: Stock Research Workspace

Created: 2026-06-03 14:48:14 Asia/Shanghai

## Verdict

Not accepted yet.

PR12 now has the required implementation files and the overall architecture is on track:

- `tos-funder/commands/tos-funder-stock-research.md` exists with valid frontmatter.
- `tos-funder/references/stock-research-workspace.md` exists.
- `docs/tos-funder/validation-pr12.md` exists.
- `SKILL.md`, `tos-funder-analyze.md`, `skill-workflow.md`, `output-schema-examples.md`, and `quick-guide.md` contain routing references.
- The command correctly presents itself as a workspace orchestrator, not a new analyst model.
- Full / incremental / refresh modes and `detail=redundant|normal|compact` are documented.

Two cleanup issues remain before accepting the PR.

## Findings

### 1. Final-action boundary check is internally inconsistent

Severity: Medium-High

Files:

- `tos-funder/commands/tos-funder-stock-research.md:324`
- `tos-funder/references/stock-research-workspace.md:80`
- `tos-funder/references/stock-research-workspace.md:159`
- `docs/tos-funder/validation-pr12.md:129-132`

The validation says:

```text
Expected: No `final_action` or `final_actions` at the orchestrator level.
```

But the actual check returns:

```text
tos-funder/commands/tos-funder-stock-research.md:324: "final_action": "<portfolio action>"
tos-funder/references/stock-research-workspace.md:80: "action": "hold"
tos-funder/references/stock-research-workspace.md:159: "final_action": "hold"
```

This is not necessarily a design failure, because the workspace is allowed to store the latest portfolio decision. The problem is that the schema does not make the source explicit enough, and the validation does not classify the actual matches.

Expected fix:

- Do not remove the ability to record the portfolio decision.
- Rename or structure these fields to show they are a **portfolio output snapshot**, not stock-research's own final decision.

Recommended schema:

```json
"latest_portfolio_decision": {
  "action": "hold",
  "confidence": 69,
  "source_command": "/tos-funder-portfolio",
  "source_report": "11-portfolio-decision.md",
  "source_run": "2026-06-03-full"
}
```

For `_manifest.json`:

```json
"summary": {
  "portfolio_decision": {
    "action": "hold",
    "confidence": 69,
    "source_command": "/tos-funder-portfolio",
    "source_report": "11-portfolio-decision.md"
  }
}
```

Avoid `summary.final_action` in stock-research schemas, because that looks like the orchestrator produced the final action. Use `portfolio_decision.action` instead.

Then update:

- `tos-funder/commands/tos-funder-stock-research.md`
- `tos-funder/references/stock-research-workspace.md`
- `tos-funder/references/output-schema-examples.md` if it references the old field
- `docs/tos-funder/validation-pr12.md`

### 2. `validation-pr12.md` records expected check results, not actual check output/classification

Severity: Medium

File:

- `docs/tos-funder/validation-pr12.md:103-149`

The validation currently says "Expected results" but does not show the actual matches. For PR12 this matters because the actual `final_action|final_actions|"action"` check is not empty.

Expected fix:

In `validation-pr12.md`, replace expected-only check notes with an actual summarized result table:

```text
| Check | Actual result | Classification | Status |
```

For the final-action boundary check, classify matches:

- allowed: constraint text saying stock-research does not produce final actions
- allowed: `portfolio_decision.action` snapshot sourced from `/tos-funder-portfolio`
- issue: any `summary.final_action` or top-level `final_action` produced by stock-research

After the schema rename above, the check should no longer show `summary.final_action`.

### 3. `quick-guide.md` still marks PR12 as `in progress`

Severity: Low

File:

- `docs/tos-funder/quick-guide.md`

Current PR12 status says:

```text
Status:
- in progress
```

This is acceptable while PR12 is under review, but after PR12-fix it should become:

```text
Status:
- accepted
```

and Current Progress / Current delivery should reflect PR12 completion.

## Checks Run

Required files:

```text
ls -l tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md
```

Result:

```text
all three required files exist
```

Routing:

```text
rg -n "tos-funder-stock-research" tos-funder docs/tos-funder
```

Result:

- command file exists
- `SKILL.md` route exists
- `tos-funder-analyze.md` workspace route exists
- `skill-workflow.md` maps to `#stock_research_workspace`
- `output-schema-examples.md` has section 12
- `quick-guide.md` mentions PR12

Output protocol:

```text
rg -n "outputs/stocks|_state.json|_manifest.json|_index.md" tos-funder docs/tos-funder
```

Result:

- output protocol appears in command, reference, validation, quick-guide, and schema examples.

Boundary check:

```text
rg -n 'final_action|final_actions|"action"\\s*:|weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review"|query2data|query -r event|query -r business|hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR' \
  tos-funder/commands/tos-funder-stock-research.md \
  tos-funder/references/stock-research-workspace.md \
  docs/tos-funder/validation-pr12.md
```

Result:

- no enum drift found
- no iWencai technical indicator dependency found
- dead route references appear only as boundary text
- final-action boundary has the schema ambiguity described above

## CC Fix Instructions

```text
PR12-fix: 修复 stock-research final-action 边界和 validation 记录方式

修改这些文件：
- tos-funder/commands/tos-funder-stock-research.md
- tos-funder/references/stock-research-workspace.md
- docs/tos-funder/validation-pr12.md
- docs/tos-funder/quick-guide.md

如 output-schema-examples.md 中有相关旧字段，也同步修改：
- tos-funder/references/output-schema-examples.md

修复 3 件事：

1. 避免 stock-research schema 出现 summary.final_action
   - stock-research 可以记录 portfolio 决策，但必须明确是 portfolio output snapshot。
   - 将 manifest/state 中的：
     summary.final_action
     latest_decision.action

     改成类似：
     summary.portfolio_decision.action
     latest_portfolio_decision.action

   - 必须包含：
     source_command: "/tos-funder-portfolio"
     source_report: "11-portfolio-decision.md"
     source_run: "<run id>"

2. 更新 validation-pr12
   - 不要只写 Expected。
   - 加入实际 rg 检查结果摘要表。
   - 对 final_action/final_actions/"action" 命中进行分类。
   - 明确：stock-research 不产生 final_action/final_actions；它只保存 `/tos-funder-portfolio` 的 `portfolio_decision` snapshot。

3. 更新 quick-guide
   - PR12 状态从 in progress 改为 accepted。
   - Current delivery / Current Progress 中体现 PR12 已完成。

修复后运行并贴结果：

rg -n 'summary.*final_action|latest_decision|final_action|final_actions|"action"\\s*:' tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md tos-funder/references/output-schema-examples.md

rg -n 'portfolio_decision|latest_portfolio_decision|source_command|source_report|source_run' tos-funder/commands/tos-funder-stock-research.md tos-funder/references/stock-research-workspace.md docs/tos-funder/validation-pr12.md tos-funder/references/output-schema-examples.md

rg -n 'PR12|stock research workspace|Status:|accepted|Current delivery' docs/tos-funder/quick-guide.md

预期：
- 不再有 `summary.final_action`。
- 若仍出现 `final_action/final_actions`，必须是约束文本或 portfolio schema 引用，不是 stock-research 自己的输出字段。
- `portfolio_decision` / `latest_portfolio_decision` 明确带 source_command/source_report/source_run。
- quick-guide 中 PR12 为 accepted。
```

## PM Guidance For CC

The PR12 design is correct: stock-research is a workspace orchestrator. The cleanup is about naming discipline. A persisted snapshot of portfolio output is fine; a field named `final_action` inside the stock-research schema blurs the boundary that PR10B/PR11 established. Use `portfolio_decision` and source metadata so future agents cannot misread the orchestrator as a decision engine.

---

## Re-Audit After PR12-fix - 2026-06-03

### Verdict

Accepted.

PR12-fix resolves the final-action boundary naming issue, improves validation classification, and updates quick-guide status.

### Verification

#### 1. `summary.final_action` removed

No stock-research manifest/state schema now uses `summary.final_action`.

`tos-funder/commands/tos-funder-stock-research.md` now records portfolio output as:

```json
"summary": {
  "portfolio_decision": {
    "action": "<portfolio action>",
    "confidence": <confidence int>,
    "source_command": "/tos-funder-portfolio",
    "source_report": "11-portfolio-decision.md"
  }
}
```

#### 2. State uses sourced portfolio snapshot

`tos-funder/references/stock-research-workspace.md` now uses:

```json
"latest_portfolio_decision": {
  "action": "hold",
  "confidence": 69,
  "source_command": "/tos-funder-portfolio",
  "source_report": "11-portfolio-decision.md",
  "source_run": "2026-06-03-full"
}
```

This preserves the portfolio decision snapshot without making stock-research a decision engine.

#### 3. Validation now classifies actual matches

`docs/tos-funder/validation-pr12.md` now includes actual check classifications for final-action boundary matches:

- constraint text is allowed
- `latest_portfolio_decision` is allowed as sourced portfolio output snapshot
- `summary.portfolio_decision` is allowed as manifest snapshot

It explicitly states:

```text
No final_action/final_actions at stock-research orchestrator level.
All portfolio decision fields are clearly sourced from /tos-funder-portfolio.
```

#### 4. Quick-guide updated

`docs/tos-funder/quick-guide.md` now shows:

- `PR12 Stock Research Workspace — completed`
- PR12 status: `accepted`

### Final PR12 Status

PR12 Stock Research Workspace is accepted.

The accepted shape is:

- `/tos-funder-stock-research` is a workspace orchestrator, not an analyst.
- It supports `mode=auto|full|incremental|refresh`.
- It supports `detail=redundant|normal|compact`.
- It writes durable stock workspaces under `outputs/stocks/<股票名>-<代码>/`.
- It maintains `_state.json`, `_index.md`, and per-run `_manifest.json`.
- It saves the portfolio decision as a sourced `/tos-funder-portfolio` snapshot, not as its own final action.
