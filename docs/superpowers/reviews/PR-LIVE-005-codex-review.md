# PR-LIVE-005 Codex Final Review

## Verdict

APPROVED

## Findings

No blocking findings.

## Review Notes

- Optional live smoke is skipped by default and enabled only with `HOXIT_LIVE_TESTS=1`.
- The Ningbo Bank `002142` UZEN smoke test generates JSON/Markdown in `tmp_path`, checks `change_pct`, bank detection, DCF bank warning, field-level status, Markdown sections, and raw dict leakage.
- Documentation now records the Phase 7 live provider contract, hoxit-first fallback policy, no akshare fallback, and controlled Web/Playwright requirements.
- No production provider behavior, CLI, akshare, Playwright, or visualization changes were introduced.

## Verified

- `.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -v` passed: 258 passed.
- `.venv/bin/python -m pytest tests/test_live_endpoints.py -v` passed in offline mode: 30 skipped.
- `.venv/bin/hoxit uzen --help` passed.
- `git diff --check -- docs hoxit tests uzen-skills` passed.
- `set -a; [ -f .env.local ] && source .env.local; set +a; HOXIT_LIVE_TESTS=1 .venv/bin/python -m pytest tests/test_live_endpoints.py -k uzen -v` passed: 1 passed, 29 deselected.
- `.venv/bin/python -m pytest` passed: 358 passed, 30 skipped.

## Notes

- The branch is correctly based on `origin/agent/cc/pr-live-004-bank-report-quality-ningbo`.
- Live smoke uses pytest `tmp_path`; existing local `tos/` output remains untracked and was not reviewed as part of this PR.
