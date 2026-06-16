# PR-LIVE-002 Codex Final Review

## Verdict

CHANGES_REQUESTED

## Findings

1. `hoxit/uzen.py:467` now computes `avg_price` from quote turnover/volume, but it still uses `amount / vol` unconditionally. This is unsafe for hoxit's primary mootdx quote shape because `hoxit/market.py` preserves the raw mootdx `vol` field without unit normalization; live A-share quote data can expose volume in 手/lots. For example, the previously validated Ningbo Bank live shape had roughly `amount=1000648512` and `vol=310484`, where `amount / vol` is about `3222`, while the meaningful transaction average is about `32.22` if `vol` is lots. This would reintroduce a plausible-looking but wrong report metric.

2. `hoxit/uzen.py:467` does not preserve a direct provider `avg_price` field. The PR ticket requires direct provider fields to be preserved when present. The current helper ignores `quote["avg_price"]` and overwrites it with a derived value or `None`.

## Required Changes

- Preserve direct `quote.avg_price` when present.
- Derive `avg_price` from quote amount and volume/vol only with an explicit, tested A-share unit rule. At minimum, cover both share-volume and lot-volume shapes so mootdx-style `vol` does not produce a 100x inflated均价.
- If the unit cannot be inferred safely, leave `avg_price` as `None` with a warning/data-needed entry rather than producing a misleading number.
- Update tests so `avg_price` covers direct-field preservation, share-volume input, lot-volume input, and missing/ambiguous turnover data.
- Keep the PR scoped to PR-LIVE-002; no CLI, Playwright, akshare, or later-ticket work.

## Verified

- `.venv/bin/python -m pytest tests/test_uzen.py -v` passed: 187 passed.
- After revision, `.venv/bin/python -m pytest tests/test_uzen.py -v` passed: 188 passed.
- `.venv/bin/hoxit uzen --help` passed.
- `git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/API_DEVLOG.md` passed.
- `.venv/bin/python -m pytest` passed: 300 passed, 29 skipped.
- After revision, `.venv/bin/python -m pytest` passed: 301 passed, 29 skipped.

## Notes

- The branch is now correctly based on `origin/agent/cc/pr-live-001-uzen-provider-normalization-boundary`; the earlier base-branch issue is resolved.
- `tos/` remains an untracked local output directory and was not reviewed as part of this PR.
