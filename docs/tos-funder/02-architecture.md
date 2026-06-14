# Trading Funder Architecture

Trading Funder is a skill-command architecture.

## Non-goals

- Do not port LangGraph.
- Do not port the React/FastAPI app.
- Do not reproduce the original CLI runtime.
- Do not build a new orchestration platform before commands prove useful.

## Components

```text
Claude Code command
  -> Trading Funder reference
  -> hoxit data collection
  -> facts bundle
  -> deterministic score/model
  -> optional persona reasoning
  -> report/action/next-step prompts
```

## Skill Layer

`tos-funder/SKILL.md` is the entrypoint. It keeps only routing and core workflow instructions.

## Command Layer

Commands are executable Markdown instructions for Claude Code:

- `tos-funder-analyze.md`: router.
- `tos-funder-value-buffett.md`: key sample analyst implementation.
- `tos-funder-value-graham.md`: Graham deep-value implementation.
- `tos-funder-quant-price-series.md`: TDX/mootdx price-series adapter command.
- `tos-funder-portfolio.md`: risk/portfolio sample.

## Reference Layer

References contain the durable strategy logic:

- taxonomy
- iWencai adapter
- price-series adapter
- workflow schema
- value investor methods
- command template

## Data Layer

Primary:

```text
hoxit iwc query
hoxit iwc search
hoxit market bars
hoxit market quote
hoxit market transactions
```

Routing rule:

```text
fundamentals / valuation snapshots / announcements / reports -> iWencai
OHLCV / quote / intraday / technical / risk series -> mootdx/TDX market layer
```

Fallback:

```text
iWencai OHLCV only when mootdx is unavailable; original ai-hedge-fund API only when hoxit-native A-share sources cannot cover the field and compatibility is documented.
```

## State Model

Instead of LangGraph `AgentState`, each command should produce a portable facts bundle:

```text
target
data_quality
scores
valuation
risks
signal
next_steps
```

Portfolio commands can consume multiple saved analyst outputs, but they should not require a persistent platform.
