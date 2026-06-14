# UZEN Skill File Gap Audit

Date: 2026-06-15
Status: active planning

## Scope

This audit compares the instruction layer in:

- `Reference/UZI-Skill/skills/deep-analysis/SKILL.md`
- `Reference/UZI-Skill/skills/investor-panel/SKILL.md`
- `Reference/UZI-Skill/skills/trap-detector/SKILL.md`
- `Reference/UZI-Skill/skills/lhb-analyzer/SKILL.md`

against:

- `uzen-skills/skills/deep-analysis/SKILL.md`
- `uzen-skills/skills/investor-panel/SKILL.md`
- `uzen-skills/skills/trap-detector/SKILL.md`
- `uzen-skills/skills/lhb-analyzer/SKILL.md`

## Executive Finding

The current UZEN skill files are placeholders. They identify command names and hoxit as the backend, but they do not yet encode UZI's workflow discipline.

This is a first-order product gap. Without these protocols, cc or any agent can run the wrong mode, overclaim unsupported data, skip quality gates, or continue to later work without Codex review.

## Deep Analysis

### UZI Behavior

UZI `deep-analysis` is the master workflow. It defines:

- the agent role as a securities analyst;
- strict task ordering;
- no-fabrication rules;
- stock-name/code correction;
- ETF and non-stock guardrails;
- stage-based data collection;
- progress update requirements;
- institutional model hooks;
- investor panel integration;
- qualitative multi-agent analysis duties;
- Playwright fallback for missing public data;
- self-review and report quality gates.

### Current UZEN Behavior

Current UZEN `deep-analysis` says only:

- A-share only;
- JSON and Markdown first;
- use hoxit APIs first;
- mark non-A-share and HTML/share-card work as deferred.

### Gap

UZEN lacks:

- explicit orchestration responsibility;
- required mode selection rules;
- data completeness gates;
- current-vs-target capability language;
- agent analysis boundaries;
- report structure;
- stop conditions for missing data;
- single-ticket workflow reminders for cc.

### Phase 1 Decision

Rewrite UZEN `deep-analysis` as the master A-share protocol. It should adapt UZI's discipline without claiming unsupported UZI runtime features.

## Investor Panel

### UZI Behavior

UZI `investor-panel` defines a strict `Signal` schema, investor groups, role-play behavior, Great Divide logic, vote distribution, and a large persona set.

### Current UZEN Behavior

Current UZEN says to run:

```bash
hoxit uzen panel-only <code>
```

The current runtime panel is a lightweight PE/ROE summary, not a real investor panel.

### Gap

UZEN lacks:

- investor signal schema;
- investor identities and groups;
- pass/fail/neutral vote semantics;
- confidence and evidence fields;
- rules for unavailable data;
- clear statement that 65-investor parity is not implemented.

### Phase 1 Decision

Define the target panel schema and an A-share-first lightweight panel protocol. Full 65-person UZI parity remains deferred until runtime schema and persona rules are implemented.

## Trap Detector

### UZI Behavior

UZI `trap-detector` checks manipulation and social-sentiment traps using eight signal categories, keyword boosts, evidence URLs, and risk levels.

### Current UZEN Behavior

Current UZEN says to run:

```bash
hoxit uzen scan-trap <code>
```

The runtime checks hoxit market-risk inputs such as block trades, margin data, holder changes, fund flow, and LHB data.

### Gap

UZEN currently mixes two different concepts:

- market-data risk from hoxit;
- social/manipulation trap evidence from UZI.

UZEN lacks:

- evidence schema;
- `data_needed` handling for unavailable social signals;
- keyword and URL evidence rules;
- clear separation between deterministic market flags and social trap judgment.

### Phase 1 Decision

Rewrite the skill so `scan-trap` first reports supported hoxit market-risk checks, then reports unsupported UZI-style social trap checks as missing or deferred unless evidence exists.

## LHB Analyzer

### UZI Behavior

UZI `lhb-analyzer` expects:

- dragon-tiger-board data;
- seat recognition;
- institution vs hot-money classification;
- buy/sell seat behavior;
- board and peer comparison;
- post-LHB risk interpretation.

### Current UZEN Behavior

Current UZEN says to run:

```bash
hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD
```

The current runtime can collect broad LHB-related data, but there is no documented seat-analysis protocol.

### Gap

UZEN lacks:

- seat identity schema;
- institution/hot-money categories;
- peer and board leadership checks;
- evidence requirements;
- fallback behavior when only partial LHB data exists.

### Phase 1 Decision

Define an A-share LHB protocol that matches hoxit's current boundaries and identifies the missing reusable APIs needed for later runtime parity.

## Priority

Phase 1 order:

1. `deep-analysis`: master protocol and workflow gates.
2. `investor-panel`: schema and current-vs-target boundary.
3. `trap-detector`: split supported market risk from deferred social trap evidence.
4. `lhb-analyzer`: LHB reasoning contract and missing data list.

This order gives cc a stable master instruction before rewriting specialized skills.
