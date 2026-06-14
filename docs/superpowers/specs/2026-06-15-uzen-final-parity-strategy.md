# UZEN Final Parity Strategy

Date: 2026-06-15
Status: active planning

## Purpose

This document resets the execution strategy for bringing `uzen-skills` closer to `Reference/UZI-Skill` while keeping hoxit as the A-share data and CLI substrate.

The current UZEN baseline is useful, but it is still far from UZI-Skill in product behavior. The next work must therefore be planned around capability parity, not command-name parity.

## Final Target

UZEN should become an A-share-first research workflow that can:

- accept a normal A-share code or name;
- collect available hoxit data through stable hoxit interfaces;
- identify missing or weak data explicitly;
- run a staged research workflow with hard quality gates;
- produce a readable JSON and Markdown research artifact;
- support focused modes such as quick scan, investor panel, trap scan, LHB, DCF, and comps with mode-specific behavior;
- let an agent add qualitative judgment only inside a declared analysis envelope;
- avoid fabricating unsupported UZI features such as full 65-investor parity, social trap evidence, HTML/share cards, or non-A-share coverage before the data and protocol exist.

## Strategy

### 1. Treat Skill Protocols As Product Surface

UZI-Skill's most important behavior is not only in Python scripts. It is also encoded in `skills/*/SKILL.md`:

- role definition for the analyst agent;
- mandatory execution order;
- hard gates and stop conditions;
- data completeness expectations;
- qualitative-analysis responsibilities;
- report tone and output contract;
- investor panel and trap detector schemas.

Current UZEN skill files are skeletal. They do not yet teach an agent how to work. This is why the previous runtime-focused audit understated the gap.

The next phase must first migrate the A-share-safe parts of those protocols before expanding runtime behavior.

### 2. Keep hoxit As The Only Data Boundary

UZEN must not import UZI's provider chain directly. Missing data should be handled in this order:

1. Use an existing hoxit interface.
2. If a reusable A-share data need is missing, add it to hoxit following current module boundaries and CLI conventions.
3. If hoxit cannot cover it yet, mark the field as `missing`, `unsupported`, or `data_needed`.
4. Do not add one-off scrapers under `uzen-skills`.

### 3. Separate Protocol Parity From Runtime Parity

Protocol parity means the skill documents define the right workflow, gates, schemas, and limits.

Runtime parity means hoxit can actually produce the corresponding data and calculations.

Protocol parity should come first because it gives cc and Codex a reliable contract for later production PRs.

### 4. A-Share First

This phase is limited to A-share research. H-share, US stock, ETF, fund, bond, and crypto behavior remains deferred.

UZI behavior that assumes non-A-share data may be described only as a future extension, not as current UZEN capability.

## Execution Phases

### Phase 1: Skill Protocol Parity

Goal: make `uzen-skills/skills/*/SKILL.md` useful, honest, and enforceable.

Scope:

- rewrite `deep-analysis` as the orchestration protocol;
- rewrite `investor-panel` with a signal schema and current-vs-target boundaries;
- rewrite `trap-detector` with market-risk vs social/manipulation-risk separation;
- rewrite `lhb-analyzer` with seat, institution, hot-money, and peer-comparison requirements.

No production hoxit code should change in this phase.

### Phase 2: Mode Execution Correctness

Goal: make each `hoxit uzen <mode>` execute only the data calls and sections required by that mode.

This corresponds to the earlier roadmap's mode profile work.

### Phase 3: Report Contract

Goal: replace debug-style Markdown dumps with compact human research output while preserving raw JSON.

### Phase 4: Structured Quality And Missing Data

Goal: add per-source quality records and explicit `skipped`, `missing`, `partial`, and `error` states.

### Phase 5: Focused Analytical Models

Goal: implement A-share-safe DCF, comps, panel foundation, LHB reasoning, and trap evidence only where hoxit data supports them.

### Phase 6: Agent Analysis Envelope

Goal: add an explicit optional area where the agent can write qualitative judgment, assumptions, and conflicts without mixing them into raw data.

## Immediate Next Step

Start Phase 1 with PR-SKILL-001 only:

- rewrite `uzen-skills/skills/deep-analysis/SKILL.md`;
- update adjacent docs only where necessary;
- do not modify production hoxit code;
- stop for Codex review after the implementation report and commit.
