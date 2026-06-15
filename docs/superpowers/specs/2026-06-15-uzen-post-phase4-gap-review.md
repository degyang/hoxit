# UZEN Post-Phase-4 Gap Review

Date: 2026-06-15
Status: draft for planning

## Purpose

This review reassesses UZEN after Report Envelope Phase 4 was merged to `main`.

The comparison target is the available UZI-Skill project record at:

`/Users/mac/Projects/POS/10-Projects/Tracking/11.28 UZI-Skill`

The goal is to decide the next development phase for an A-share-first, hoxit-native UZEN. This is not a recommendation to copy UZI-Skill wholesale. UZEN should preserve hoxit's architecture, dependency discipline, and data boundary.

## Current UZEN Baseline

Merged phases now provide:

- `hoxit uzen` CLI with seven A-share modes.
- hoxit-native provider boundary through `UzenDataProvider`.
- Mode execution profiles that avoid unnecessary data calls.
- Per-source quality records.
- Compact Markdown report sections with mode-specific visibility.
- Lightweight DCF and Comps analysis.
- Market-risk / unsupported social-trap split.
- Five deterministic investor signals.
- Deterministic LHB summary.
- Optional analysis封套（Agent Analysis Envelope）.
- Chinese-first docs and skill protocols.

Current implementation remains intentionally compact:

```text
hoxit uzen <mode>
  -> collect_snapshot()
  -> analyze_snapshot()
  -> render_markdown()
  -> JSON + Markdown artifacts
```

## UZI-Skill Reference Shape

The reference project is much larger than UZEN:

- 337 files under `skills/deep-analysis`.
- One dominant `deep-analysis` skill with hard gates and long operational protocol.
- 22 data dimensions and 22 renderer dimensions.
- Pipeline engine: collect, score, synthesize, validate, render.
- 66 investor personas across 9 groups and 242 quantitative rules.
- `agent_analysis.json` as a required deep-mode judgment bridge.
- HTML report, share card, war report, inline assets, visual cards.
- Self-review and agent-analysis validators.
- Data-provider chain with akshare, baostock, efinance, tushare, direct HTTP, browser/web fallback.
- Market routing across A/H/US and non-stock guardrails.
- 60+ test files and hundreds of tests.

Key UZI data flow:

```text
user input
  -> ticker / market / intent
  -> raw_data.json
  -> dimensions.json
  -> stock_features
  -> panel.json
  -> agent_analysis.json
  -> synthesis.json
  -> report artifacts
```

## Executive Findings

UZEN is no longer just command-name parity. It now has a working hoxit-native A-share report runtime. However, it is still far from UZI-Skill in the areas that matter most for product behavior:

1. UZEN lacks a dimension pipeline.
2. UZEN lacks a synthesis layer.
3. UZEN has no report quality gate or self-review gate.
4. UZEN's investor panel is a 5-signal baseline, not a persona system.
5. UZEN's `agent_analysis` is optional and shallow, not a deep-mode workflow bridge.
6. UZEN has no HTML/visual report layer.
7. UZEN's LHB and trap analysis are honest but still shallow.
8. UZEN has fewer A-share data interfaces than UZI expects for industry, fund holders, chain, governance, events, policy, materials, and sentiment.

This is the right state for a disciplined hoxit-native migration: current UZEN is usable and testable, but the next phase must add a pipeline/synthesis spine before adding more modes.

## Gap Matrix

| Area | UZI-Skill | UZEN after Phase 4 | Gap Severity | Recommendation |
| --- | --- | --- | --- | --- |
| Runtime architecture | Stage/pipeline engine with raw_data, dimensions, features, panel, synthesis | Single snapshot/analyze/render module | High | Add UZEN dimension/synthesis layer without importing UZI runtime |
| Data quality | Dimension quality, validators, self-review gates | Source quality + warnings + input_quality | Medium-high | Add report self-review and artifact quality checks |
| Report output | HTML, cards, share PNG, war report | Markdown + JSON | High | First improve Markdown synthesis; HTML later |
| Agent role | Deep-mode agent must review data gaps, panel, assumptions, synthesis | Optional `agent_analysis` envelope | High | Add deep-review workflow contract and validation |
| Investor panel | 66 personas, 9 groups, 242 rules, persona assets | 5 deterministic signals | High | Expand A-share baseline groups incrementally; avoid 66 parity claim |
| Trap detector | Social/manipulation evidence categories and keyword/evidence rules | Market risk + unsupported trap_risk | Medium | Keep split; add evidence schema only before adding providers |
| LHB | Seat database, institution/hot-money classification, peer comparison | row count, net_buy, simple signals | Medium-high | Add hoxit LHB data depth before claiming seat logic |
| Valuation | DCF/DDM/LBO/SOTP/Monte Carlo/deep methods | light DCF + Comps | Medium-high | Strengthen DCF assumptions and Comps peer audit first |
| Command surface | 22 commands | 7 commands | Medium | Do not add more commands until pipeline spine exists |
| Market coverage | A/H/US, ETF/fund/non-stock guardrails | A-share only | Low by design | Preserve A-share-first scope |
| Data providers | provider chain + browser/web fallback | hoxit interfaces only | Medium | Add reusable hoxit APIs only when accepted mode requires them |
| Testing | 60+ files, broad regression | focused hoxit unit tests | Medium | Add tests with each runtime expansion; no live dependency in unit tests |

## What Changed Since Earlier Audits

Earlier audits correctly identified many gaps, but Phase 1-4 closed several foundational issues:

- `quick-scan`, `dcf`, `comps`, `panel-only`, `scan-trap`, and `lhb-analyzer` now have distinct data-call profiles.
- Markdown is mode-specific.
- Source quality is structured.
- DCF/Comps/LHB are no longer empty labels.
- Agent qualitative judgment has a declared envelope.
- Skill files are no longer placeholders.

The main unresolved gap is therefore no longer "docs are skeletal" or "commands are labels only"; it is "UZEN still lacks UZI's staged research spine."

## Recommended Next Phase

### Phase 5: UZEN Research Spine

Goal: introduce a hoxit-native research spine that separates raw data, dimensions, synthesis, and report self-review while preserving current CLI behavior.

Non-goals:

- Do not import UZI provider chain.
- Do not add HTML reports yet.
- Do not add non-A-share coverage.
- Do not claim 66-investor parity.
- Do not make agent qualitative analysis overwrite deterministic hoxit data.

Proposed shape:

```text
collect_snapshot()
  -> build_dimensions(snapshot)
  -> synthesize_analysis(snapshot, dimensions, agent_analysis)
  -> review_report_contract(snapshot)
  -> render_markdown(snapshot)
```

The initial implementation can stay inside `hoxit/uzen.py` or a small `hoxit/uzen_*` helper module. The decision should favor hoxit's existing simplicity unless the file becomes hard to maintain.

## Phase 5 PR Candidates

### PR-SPINE-001: Dimension Layer

Add `analysis["dimensions"]` as a deterministic, A-share-safe layer.

Initial dimensions:

- `basic`
- `market`
- `valuation`
- `fundamentals`
- `capital_flow`
- `panel`
- `risk`
- `lhb`
- `dcf`
- `comps`

Each dimension should include:

```json
{
  "status": "computed|partial|data_needed|unsupported",
  "quality": "full|partial|missing|skipped|error",
  "inputs": ["quote", "metrics"],
  "outputs": ["summary", "warnings"],
  "warnings": []
}
```

### PR-SPINE-002: Synthesis Layer

Add `analysis["synthesis"]` with concise, non-fabricated conclusions:

- `stance`: bullish / neutral / bearish / data_needed
- `confidence`: high / medium / low
- `drivers`: positive drivers from deterministic analysis
- `risks`: negative drivers from deterministic analysis
- `conflicts`: valuation vs momentum, panel vs risk, etc.
- `followups`: concrete data gaps and next checks

Synthesis must cite existing analysis objects only.

### PR-SPINE-003: Report Self-Review Gate

Add `analysis["report_review"]`:

- required JSON sections present
- Markdown sections align with mode
- no raw dict repr in Markdown
- disclaimer present
- unsupported features are labeled
- agent analysis only appears inside envelope
- no full UZI/66-persona parity claims

This can be a deterministic checklist, not a natural-language evaluator.

### PR-SPINE-004: Deep-Review Agent Envelope

Extend the optional agent envelope from a shallow note into a validated deep-review object:

- `status`
- `basis`
- `thesis`
- `assumptions`
- `conflicts`
- `data_gap_acknowledged`
- `dimension_commentary`
- `panel_insights`
- `warnings`

This should remain optional for CLI users, but when provided it must be validated and rendered clearly.

### PR-SPINE-005: Docs Sync

Update `docs/INTERFACES.md` and `uzen-skills/` to document dimensions, synthesis, report review, and deep-review envelope boundaries.

## Priority Decision

Do Phase 5 before expanding investor count, LHB seat logic, trap evidence, or HTML.

Reason:

Without a dimension/synthesis/review spine, later additions will pile more logic into `analysis` without a durable contract. UZI's advantage is not just breadth; it is the staged research data flow. UZEN needs a smaller version of that spine first.

## Risks

- Over-abstracting too early: avoid building a full framework before concrete dimensions exist.
- Breaking current JSON users: keep current keys stable and add new objects.
- Accidentally implying UZI parity: docs and review gates must keep deferred features explicit.
- Agent overreach: qualitative analysis must stay in envelope and not mutate deterministic outputs.

## Recommended Immediate Next Step

Create a Phase 5 implementation plan and PR tickets:

1. `PR-SPINE-001-uzen-dimension-layer`
2. `PR-SPINE-002-uzen-synthesis-layer`
3. `PR-SPINE-003-uzen-report-self-review`
4. `PR-SPINE-004-uzen-deep-review-envelope`
5. `PR-SPINE-005-uzen-spine-docs-sync`

The first ticket should be small and additive: implement only `analysis["dimensions"]`, add tests, and keep all existing report behavior unchanged.
