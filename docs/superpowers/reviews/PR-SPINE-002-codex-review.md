# PR-SPINE-002 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

The PR adds the requested deterministic `analysis["synthesis"]` object and renders a compact `## 综合研判` Markdown section. Tests pass and the changed file scope is otherwise appropriate. However, the implementation directly reads `analysis["trap_risk"]`, while the PR ticket explicitly limits synthesis inputs to `panel`, `market_risk`, `dcf`, `comps`, `lhb`, `dimensions`, and `data_quality`. Since PR-SPINE-001 already carries unsupported trap-risk state through `dimensions["risk"]`, synthesis should consume that dimension contract instead of bypassing it.

## Review Object

Base:

`origin/agent/cc/pr-spine-001-uzen-dimension-layer`

Head:

`HEAD` (`e5c8145 feat: add deterministic synthesis layer to UZEN analysis`)

Diff command:

```bash
git diff origin/agent/cc/pr-spine-001-uzen-dimension-layer...HEAD
```

Files reviewed:

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/PR-SPINE-002-implementation.md`
- `docs/superpowers/status/board.md`

## Spec Compliance

Partial.

- Pass: `analysis["synthesis"]` is added.
- Pass: synthesis has `basis`, `stance`, `confidence`, `drivers`, `risks`, `conflicts`, and `followups`.
- Pass: Markdown includes `## 综合研判`.
- Pass: no LLM or agent-authored content was introduced.
- Fail: synthesis directly reads `analysis["trap_risk"]`, which is outside the allowed input list in the ticket.

## Scope Compliance

Partial.

The file scope is correct and no providers/CLI/docs/skills were changed. The behavioral scope is slightly expanded because synthesis consumes an analysis object not listed in the ticket's allowed sources.

## Acceptance Criteria Check

- [x] JSON artifact includes `analysis["synthesis"]`.
- [ ] Synthesis does not use facts outside the ticket's allowed analysis objects.
- [x] Markdown includes `## 综合研判`.
- [x] Markdown does not include raw dict repr.
- [x] Existing tests pass.

## Test Evidence

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
```

Result: `103 passed`.

```bash
.venv/bin/hoxit uzen --help
```

Result: passed.

```bash
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

Result: passed.

Additional regression check:

```bash
.venv/bin/python -m pytest
```

Result: `201 passed, 26 skipped`.

## Issues

### Critical

None.

### Important

1. Synthesis bypasses the allowed input contract by reading `analysis["trap_risk"]` directly.

   Ticket `PR-SPINE-002` says synthesis must use only:

   - `analysis["panel"]`
   - `analysis["market_risk"]`
   - `analysis["dcf"]`
   - `analysis["comps"]`
   - `analysis["lhb"]`
   - `analysis["dimensions"]`
   - `snapshot["data_quality"]`

   Current implementation reads:

   ```python
   trap_risk = analysis.get("trap_risk", {})
   if trap_risk.get("status") == "unsupported":
       risks.append("社交/操纵风险检查尚未实现")
   ```

   This same information is already available through `dimensions["risk"]["warnings"]` after PR-SPINE-001. Synthesis should consume `dimensions["risk"]` rather than directly reading `trap_risk`.

### Minor

- `test_synthesis_includes_risk_flags` only asserts `len(synth["risks"]) > 0` when market risk flags exist. A stronger assertion should check that each flag appears in synthesis risks.

## Required Fixes for Claude Code

1. Remove direct `analysis["trap_risk"]` reads from `_synthesis_summary()`.

2. Add risk warnings from the allowed `dimensions` input instead, for example:

   ```python
   risk_dimension = dimensions.get("risk", {})
   for warning in risk_dimension.get("warnings", []):
       if warning not in risks:
           risks.append(warning)
   ```

3. Update the implementation report so it no longer states that synthesis reads `analysis["trap_risk"]`.

4. Strengthen the risk flag test so actual market risk flags are included in `synthesis["risks"]`, not just that the list is non-empty.

5. Re-run:

   ```bash
   .venv/bin/python -m pytest tests/test_uzen.py -v
   .venv/bin/hoxit uzen --help
   git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
   ```

6. Commit, push, and stop for Codex review. Do not implement PR-SPINE-003.

## Merge Decision

Do not merge until the allowed-input contract is fixed.
