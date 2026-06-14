# PR-005 Codex Review

## Verdict

CHANGES_REQUESTED

## Summary

PR-005 adds lightweight UZEN mode profile metadata under `analysis.mode_profile` and tests the requested labels for `quick-scan`, `panel-only`, `lhb-analyzer`, and unknown-mode fallback.

The mode-profile implementation itself is small and aligned with the ticket. However, the branch is not based on the approved PR-004 head. It is missing PR-004's dispatch test fix, PR-004 approval metadata, and the workflow gate updates. Since PR-005 explicitly depends on PR-004 being approved or merged, this branch must be rebased or merged onto the approved PR-004 branch before approval.

## Review Object

Base: `origin/agent/cc/pr-004-uzen-cli-workflow`

Head: `agent/cc/pr-005-uzen-mode-profiles`

Diff command:

```bash
git diff origin/agent/cc/pr-004-uzen-cli-workflow...HEAD
```

Reviewed files:

- `docs/superpowers/prs/PR-005-uzen-mode-profiles.md`
- `docs/superpowers/status/PR-005-implementation.md`
- `hoxit/uzen.py`
- `tests/test_uzen.py`

## Acceptance Criteria

- [x] `quick-scan` profile has `depth == "lite"`.
- [x] `panel-only` profile has `primary_section == "panel"`.
- [x] `lhb-analyzer` profile has `primary_section == "dragon_tiger"`.
- [x] Unknown mode falls back to standard analyze-stock profile.
- [x] Existing UZEN tests still pass.

## Test Evidence

Implementation report records:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
# Output: 9 passed

.venv/bin/python -m pytest -q
# Output: 100 passed, 26 skipped

git diff --check -- hoxit/uzen.py tests/test_uzen.py
# Output: no whitespace errors
```

Codex independently reran:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
.venv/bin/python -m pytest -q
git diff --check -- hoxit/uzen.py tests/test_uzen.py
```

Results:

- `tests/test_uzen.py`: `9 passed`
- full default suite: `100 passed, 26 skipped`
- diff check: no whitespace errors

## Issues

### Critical

None.

### Important

1. PR-005 branch is not based on approved PR-004.

   Command:

   ```bash
   git merge-base --is-ancestor origin/agent/cc/pr-004-uzen-cli-workflow HEAD
   # exit status: 1
   ```

   The current branch history contains the early PR-004 implementation commits but not the approved PR-004 head. Missing commits include the PR-004 dispatch coverage fix, PR-004 approval review, and the workflow gate updates. This violates the ticket dependency: “PR-004 approved or merged.”

### Minor

1. `test_quick_scan_skips_heavy_sections` is a misleading test name.

   PR-005 intentionally does not change provider call graphs or skip heavy sections; it only labels mode profiles. The assertions are valid, but the test name should be renamed to reflect labeling, for example `test_quick_scan_mode_profile_is_lite`.

## Required Fixes for Claude Code

1. Rebase or merge `agent/cc/pr-005-uzen-mode-profiles` onto the approved PR-004 branch:

   ```bash
   git fetch origin
   git checkout agent/cc/pr-005-uzen-mode-profiles
   git rebase origin/agent/cc/pr-004-uzen-cli-workflow
   ```

   If rebase is not appropriate for the collaboration setup, merge the approved PR-004 branch instead.

2. Keep PR-005 scoped to:

   - `hoxit/uzen.py`
   - `tests/test_uzen.py`
   - `docs/superpowers/status/PR-005-implementation.md`

3. Rename the misleading quick-scan test.

4. Rerun:

   ```bash
   .venv/bin/python -m pytest tests/test_uzen.py -q
   .venv/bin/python -m pytest -q
   git diff --check -- hoxit/uzen.py tests/test_uzen.py
   ```

5. Update `docs/superpowers/status/PR-005-implementation.md` with the new commit range and verification output.

## Merge Decision

Do not approve PR-005 until the branch is based on approved PR-004 and the misleading test name is corrected.
