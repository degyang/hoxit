# PR-ANALYTICS-001: UZEN Light DCF Model

## Owner

Claude Code

## Status

TODO

## Branch

`agent/cc/pr-analytics-001-uzen-light-dcf-model`

## Design

`docs/superpowers/plans/2026-06-15-uzen-analytical-models-phase3.md`

## Goal

Make `hoxit uzen dcf` produce a deterministic, hoxit-native simplified DCF analysis with traceable assumptions, explicit missing-data behavior, JSON output, and Chinese-first Markdown.

## Scope

- Add a light DCF analysis helper in `hoxit/uzen.py`.
- Attach the result under `snapshot["analysis"]["dcf"]`.
- Render a compact DCF section in Markdown, especially for `dcf` mode.
- Add focused unit tests in `tests/test_uzen.py`.
- Keep all calculations deterministic and based only on existing snapshot data.

## Out of Scope

- No new external data source.
- No UZI provider-chain import.
- No investment recommendation wording.
- No non-A-share behavior.
- No changes to CLI command names or output file naming.
- No comps, risk split, or investor panel schema changes.

## Files Likely to Change

- `hoxit/uzen.py`
- `tests/test_uzen.py`
- `docs/superpowers/status/board.md`
- `docs/superpowers/status/PR-ANALYTICS-001-implementation.md`

## Must Not Change

- `hoxit/cli.py`
- `pyproject.toml`
- `uzen-skills/`
- `docs/INTERFACES.md`
- later PR tickets

## Required Behavior

The DCF object must use this shape:

```python
{
    "status": "computed" | "data_needed",
    "inputs": dict,
    "assumptions": dict,
    "intrinsic_value_per_share": float | None,
    "market_price": float | None,
    "margin_of_safety": float | None,
    "sensitivity": list[dict],
    "warnings": list[str],
}
```

When data is sufficient:

- calculate explicit-year cash flows;
- discount explicit cash flows;
- calculate a terminal value;
- calculate intrinsic value per share;
- calculate margin of safety against market price when available;
- include a small sensitivity table for discount rate and terminal growth.

When data is insufficient:

- return `status: "data_needed"`;
- list missing fields in `warnings`;
- do not fabricate cash flow, share count, or price values.

Preferred data inputs:

- market price from `sources.quote.price`;
- cash-flow or profit proxy from `sources.finance` numeric fields;
- share count from metrics or finance numeric fields;
- growth assumptions only from numeric hoxit data or conservative defaults recorded in `assumptions`.

## Acceptance Criteria

- [ ] `analyze_snapshot()` always includes `analysis["dcf"]`.
- [ ] `hoxit uzen dcf` JSON contains DCF status, inputs, assumptions, intrinsic value, margin of safety, sensitivity, and warnings.
- [ ] Missing inputs produce `data_needed`, not fake valuation numbers.
- [ ] Markdown includes a Chinese-first DCF section with bilingual labels for important terms such as `折现率（Discount Rate）`.
- [ ] Existing snapshot, quality, mode, and Markdown tests still pass.

## Test Requirements

- [ ] Add a computed DCF unit test with deterministic expected values or bounded comparisons.
- [ ] Add a missing-input DCF test.
- [ ] Add a Markdown DCF section test.
- [ ] Keep tests free of network and optional third-party dependencies.

## Verification Commands

```bash
.venv/bin/python -m pytest tests/test_uzen.py -v
.venv/bin/hoxit uzen --help
git diff --check -- hoxit/uzen.py tests/test_uzen.py docs/superpowers
```

## Dependencies

Depends on:

- Runtime Phase 2 complete and merged.

## Definition of Done

- [ ] Implementation complete
- [ ] Tests pass
- [ ] Verification commands pass
- [ ] Implementation report written
- [ ] Board row moved to REVIEW_READY
- [ ] Current branch committed
- [ ] Executor stopped after current PR and did not begin the next PR
- [ ] Codex review approved

## Stop Condition

After implementation, verification, commit, and implementation report, stop and wait for Codex review. Do not read, implement, commit, or update any later PR unless Codex gives a new explicit handoff.

## Rollback Notes

Revert the PR commit. Since this PR should only add derived analysis and tests, rollback should not affect data collection or CLI command registration.

## Handoff Notes for Claude Code

Follow this ticket exactly. Start from `main` at the current pushed state. Before starting, confirm this ticket is the only Phase 3 ticket marked for execution in `docs/superpowers/status/board.md`.
