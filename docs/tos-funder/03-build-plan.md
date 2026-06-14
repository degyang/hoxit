# Trading Funder Build Plan

Current master plan: `$HOME/Projects/hoxit/docs/tos-funder/15-complete-migration-plan.md`.

Current status board: `$HOME/Projects/hoxit/docs/tos-funder/16-migration-status-board.md`.

This file records the earlier staged build plan for the compressed A-share adaptation. Use the complete migration plan when the goal is full `Reference/ai-hedge-fund` parity.

## Phase 1: Foundation

Status: started.

- Create `tos-funder/SKILL.md`.
- Create command skeletons.
- Create iWencai adapter reference.
- Create TDX/mootdx price-series reference.
- Preserve POS five-family taxonomy.
- Provide Buffett and portfolio samples.

## Phase 2: Value Family

Implement commands:

- `tos-funder-value-buffett`
- `tos-funder-value-graham`
- `tos-funder-value-munger`
- `tos-funder-value-burry`
- `tos-funder-value-pabrai`

Each command should:

1. Read value investor reference.
2. Run iWencai route queries.
3. Build deterministic score.
4. Apply persona prompt if needed.
5. Emit signal/action/risk/opportunity.

## Phase 3: Quant Foundation

Status: in progress.

Implement deterministic commands:

- fundamentals ✅ (PR 3A)
- price-series command ✅ (TDX/mootdx architecture update after PR 3A)
- valuation
- growth factors
- technicals

This phase should produce reusable factor outputs for persona commands and portfolio synthesis.

References:
- `tos-funder/references/quant-systematic.md`
- `tos-funder/references/price-series.md`
- `docs/tos-funder/validation-pr3a.md`

## Phase 4: Growth and Tactical Families

Implement:

- Fisher, Lynch, Cathie Wood.
- Ackman, Druckenmiller, Jhunjhunwala, Taleb.

Focus on A-share substitutions for news, insider trades, catalysts, and macro regime.

## Phase 5: Portfolio

Implement portfolio commands:

- consume analyst signals
- calculate allowed A-share actions
- cap position size
- summarize conflicting signals
- output final actions

## Definition of Done for Each Command

- Has frontmatter and command usage.
- Names required data routes: iWencai for fundamentals/events, `hoxit market` for price-series technical/risk data.
- Has missing-data behavior.
- Separates deterministic facts from persona reasoning.
- Uses A-share-compatible action verbs.
- Includes risks, opportunities, and next-step prompts.
- Includes one tested A-share sample.
