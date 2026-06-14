# PR11 Validation: Final Hardening

Created: 2026-06-03

## 1. Command Inventory

| Command file | Frontmatter OK | SKILL route | Analyze route | Schema anchor | Notes |
|---|---|---|---|---|---|
| `tos-funder-analyze.md` | ✅ | ✅ | — (root router) | `#analyze_output` | Routing hub; all families routed |
| `tos-funder-value-buffett.md` | ✅ | ✅ | value family | None needed | Consumed by analyze; no standalone anchor |
| `tos-funder-value-graham.md` | ✅ | ✅ | value family | None needed | Consumed by analyze; no standalone anchor |
| `tos-funder-growth.md` | ✅ | ✅ | growth family | `#growth_aggregate_signal` | Aggregator |
| `tos-funder-growth-fisher.md` | ✅ | ✅ | drill-down | `#growth_analyst_signal` | |
| `tos-funder-growth-lynch.md` | ✅ | ✅ | drill-down | `#growth_analyst_signal` | |
| `tos-funder-quant-fundamentals.md` | ✅ | ✅ | quant family | None needed | Consumed by analyze |
| `tos-funder-quant-technicals.md` | ✅ | ✅ | quant family | None needed | Consumed by analyze |
| `tos-funder-quant-sentiment.md` | ✅ | ✅ | quant/sentiment family | `#sentiment_output` | |
| `tos-funder-quant-price-series.md` | ✅ | ✅ | prerequisite | `#price_series_output` | |
| `tos-funder-tactical-catalyst.md` | ✅ | ✅ | tactical family | `#tactical_catalyst_signal` | |
| `tos-funder-tactical-tail-risk.md` | ✅ | ✅ | tactical family | `#tail_risk_signal` | |
| `tos-funder-tactical.md` | ✅ | ✅ | tactical family | `#tactical_synthesis_signal` | |
| `tos-funder-macro-topdown.md` | ✅ | ✅ | macro family | `#macro_topdown_signal` | |
| `tos-funder-risk-manager.md` | ✅ | ✅ | risk family | `#risk_manager_output` | |
| `tos-funder-portfolio.md` | ✅ | ✅ | portfolio family | `#portfolio_output` | Only command producing `final_actions` |

All 16 commands have valid frontmatter (name, description, command: true, argument-hint, type: command) and are listed in `SKILL.md` with routing.

**Fix applied**: `tos-funder-analyze.md` quant family route now explicitly mentions `/tos-funder-quant-fundamentals` and `/tos-funder-quant-technicals`.

## 2. Schema Anchor Consistency

Reference: `tos-funder/references/output-schema-examples.md` (single source of truth).

| Schema Anchor | Defined in output-schema-examples.md | Mapped in skill-workflow.md | Produced by |
|---|---|---|---|
| `#price_series_output` | ✅ | ✅ | `/tos-funder-quant-price-series` |
| `#risk_manager_output` | ✅ | ✅ | `/tos-funder-risk-manager` |
| `#analyze_output` | ✅ | ✅ | `/tos-funder-analyze` |
| `#portfolio_output` | ✅ | ✅ | `/tos-funder-portfolio` |
| `#sentiment_output` | ✅ | ✅ | `/tos-funder-quant-sentiment` |
| `#growth_analyst_signal` | ✅ | ✅ | `/tos-funder-growth-fisher`, `/tos-funder-growth-lynch` |
| `#growth_aggregate_signal` | ✅ | ✅ | `/tos-funder-growth` |
| `#tactical_catalyst_signal` | ✅ | ✅ | `/tos-funder-tactical-catalyst` |
| `#tail_risk_signal` | ✅ | ✅ | `/tos-funder-tactical-tail-risk` |
| `#tactical_synthesis_signal` | ✅ | ✅ | `/tos-funder-tactical` |
| `#macro_topdown_signal` | ✅ | ✅ | `/tos-funder-macro-topdown` |

Commands without standalone anchors (`value-buffett`, `value-graham`, `quant-fundamentals`, `quant-technicals`) are consumed directly by `/tos-funder-analyze` — no anchor needed per `skill-workflow.md` line 24.

## 3. Enum Drift Check

### Check: disallowed signal/action enum patterns

```bash
rg -n "weak_bullish|strong_bearish|weak_sell|strong_buy|trim|manual_review\"" tos-funder docs/tos-funder
```

**Result**: 26 matches — all classified as:
- **Constraint/instruction text** (e.g., "Do NOT use weak_bullish" in portfolio.md, templates, references)
- **Historical audit/instruction files** referencing old patterns
- **Working constitution** (policy doc)
- **Quick-guide review checklist**

**No active schema or command issue found.**

### Check: disallowed action values in JSON

```bash
rg -n '"action"\s*:\s*"(avoid|manual_review|trim|short|cover|strong_buy|weak_sell)"' tos-funder docs/tos-funder
```

**Result**: No matches.

### Check: disallowed signal values in JSON

```bash
rg -n '"signal"\s*:\s*"(weak_bullish|strong_bearish|buy|sell|hold|reduce|watch|reject)"' tos-funder docs/tos-funder
```

**Result**: No matches.

**Verdict**: ✅ No enum drift in active commands or schemas.

## 4. Confidence Shape Check

```bash
rg -n '"confidence"\s*:\s*\{' tos-funder/commands tos-funder/references docs/tos-funder/validation-*.md
```

**Result**: No matches — all top-level `confidence` fields are integers (0–100).

**Verdict**: ✅ Confidence shape is correct across all active commands and schemas.

## 5. Final Action Boundary

**Rule**: Only `/tos-funder-analyze` may produce `final_action`; only `/tos-funder-portfolio` may produce `final_actions`.

```bash
rg -n "final_action|final_actions|\"action\"\s*:" tos-funder/commands tos-funder/references/output-schema-examples.md
```

**Classifications**:

| Source | Match | Classification |
|---|---|---|
| `tos-funder-analyze.md` | `final_action` in output example | ✅ Allowed — analyze output |
| `tos-funder-portfolio.md` | `final_actions[]` in output example | ✅ Allowed — portfolio output |
| `tos-funder-portfolio.md` | constraint "Do NOT use ... as action enums" | ✅ Allowed — constraint text |
| `output-schema-examples.md` | `final_action` in analyze section | ✅ Allowed — canonical schema |
| `output-schema-examples.md` | `final_actions[]` in portfolio section | ✅ Allowed — canonical schema |
| `tos-funder-tactical-catalyst.md` | "Does NOT produce final_action" | ✅ Allowed — constraint text |
| `tos-funder-tactical-tail-risk.md` | "Does NOT produce final_action" | ✅ Allowed — constraint text |
| `tos-funder-tactical.md` | "Does NOT produce final_action" | ✅ Allowed — constraint text |
| `tos-funder-growth.md` | "No final_action in output" | ✅ Allowed — constraint text |
| `tos-funder-macro-topdown.md` | "Does NOT produce final_action" | ✅ Allowed — constraint text |
| `tos-funder-risk-manager.md` | `"action": "watch"` in command output example | ⚠️ **Fixed** — removed from JSON example; constraint text updated |
| `tos-funder-quant-technicals.md` | `"action": "buy_if_fundamentals_confirm_else_watch"` inside signal object | ✅ Acceptable — not a portfolio action value; hybrid instruction for consumer |

**Fix applied**: Removed `"action": "watch"` from risk-manager output example. Updated constraint text to clarify risk ceilings are communicated via `action_constraints.action_ceiling`, not a separate `action` field.

## 6. Dead iWencai Route Check

**Dead routes**: `event query2data`, `business`, `management` insider fields.

```bash
rg -n "query2data|query -r event|query -r business|query -r management|hoxit iwc query -r management" tos-funder/commands tos-funder/references
```

**Classifications**:

| Source | Match | Classification |
|---|---|---|
| `tos-funder-quant-sentiment.md` | Dead routes marked as BLOCKED/DEAD | ✅ Correctly documenting dead routes |
| `tos-funder-quant-sentiment.md` | "event query2data is BLOCKED" (in examples) | ✅ Correct — DEAD notation in output |
| `tos-funder-value-buffett.md` | `hoxit iwc query -r management` for 分红/股本 | ✅ Allowed — validated fields only |
| `tos-funder-value-graham.md` | `hoxit iwc query -r management` for 分红/股本 | ✅ Allowed — validated fields only |
| `tos-funder-quant-fundamentals.md` | `hoxit iwc query -r management` for 分红/股本 | ✅ Allowed — validated fields only |
| `tos-funder-tactical-catalyst.md` | "No dead routes" constraint | ✅ Correct |
| `tos-funder-tactical-tail-risk.md` | "No dead routes" constraint | ✅ Correct |
| `tos-funder-tactical.md` | (no dead route use) | ✅ Clean |
| `references/*.md` | Documentation marking routes dead/blocked | ✅ Correct — reference documentation |
| `output-schema-examples.md` | "event query2data is BLOCKED" | ✅ Correct — schema example notation |

**Verdict**: ✅ No dead routes used as executable execution paths. `management` usage limited to validated fields (分红, 股本, 股东人数).

## 7. Data Source Boundary Check

**Expected boundaries**:
- Fundamentals/valuation/announcements/reports → iWencai
- OHLCV/quote/intraday/technicals/risk → mootdx/TDX
- iWencai OHLCV → fallback only
- Technical indicators → computed locally from qfq OHLCV

```bash
rg -n "hoxit iwc.*RSI|hoxit iwc.*MACD|hoxit iwc.*ATR|iWencai.*technical|iWencai.*技术指标" tos-funder/commands tos-funder/references
```

**Result**: 8 matches — all in reference documentation stating the boundary correctly:
- `iwencai-adapter.md`: iWencai is NOT the source for technicals
- `price-series.md`: iWencai OHLCV is fallback only
- `quant-systematic.md`: RSI/MACD/ATR computed locally from OHLCV
- `sentiment-event-proxy.md`: "No price-series from iWencai"
- `command-template.md`: "Use market bars for OHLCV"

Additional verification: `tos-funder-quant-technicals.md` computes RSI/MACD/ATR/MA/Bollinger locally from mootdx qfq OHLCV with no iWencai dependency.

**Verdict**: ✅ Data source boundaries are consistent across all commands and references.

## 8. Validation Document Index

| Validation doc | PR | Status | What it proves | Still active? |
|---|---|---|---|---|
| `validation-pr1.md` | PR1 | Accepted | Interface coverage correction | Yes — historical reference |
| `validation-pr2a.md` | PR2A | Accepted | Buffett/Graham validation | Yes — historical reference |
| `validation-pr5b.md` | PR5B | Accepted | Growth aggregate fixes | Yes — historical reference |
| `validation-pr6a.md` | PR6A | Accepted | Price-series/technicals using mootdx/TDX | Yes — historical reference |
| `validation-pr8a.md` | PR8A | Accepted | Tactical catalyst proxy | Yes — historical reference |
| `validation-pr9a.md` | PR9A | Accepted | Tactical tail-risk proxy | Yes — historical reference |
| `validation-pr9b.md` | PR9B | Accepted | Tactical synthesizer | Yes — historical reference |
| `validation-pr10a.md` | PR10A | Accepted | Macro/top-down proxy | Yes — historical reference |
| `validation-pr10b.md` | PR10B | Accepted | Portfolio/decision synthesizer | Yes — active reference |
| `validation-pr11.md` | PR11 | Current | Final hardening / cleanup | Yes — this document |

## 9. Audit Trail Index

| Audit file | PR | Type | Final status | Notes |
|---|---|---|---|---|
| `pr5b-20260603-001015.md` | PR5B | Review | ✅ Accepted | Growth aggregate fixes |
| `pr8a-tactical-catalyst-review-20260603-002834.md` | PR8A | Review | ✅ Accepted | Tactical catalyst proxy |
| `pr9a-tactical-tail-risk-review-20260603-084817.md` | PR9A | Review | ✅ Accepted | Tactical tail-risk proxy |
| `pr9b-tactical-synthesizer-review-20260603-102419.md` | PR9B | Review | ✅ Accepted | Tactical synthesizer |
| `pr10a-macro-topdown-proxy-review-20260603-110349.md` | PR10A | Review | ✅ Accepted | Macro/top-down proxy |
| `pr10b-portfolio-decision-synthesizer-review-20260603-114954.md` | PR10B | Review | ✅ Accepted | Portfolio/decision synthesizer |
| `pr11-final-hardening-instruction-20260603-124127.md` | PR11 | Instruction | ✅ Executed | This PR's instruction |
| (this file) | PR11 | Validation | Current | Final hardening report |

## 10. Summary of Changes

### Files Modified

| File | Change |
|---|---|
| `tos-funder/commands/tos-funder-analyze.md` | Quant routing: added explicit `/tos-funder-quant-fundamentals` and `/tos-funder-quant-technicals` references |
| `tos-funder/commands/tos-funder-risk-manager.md` | Removed `"action": "watch"` from output example; updated constraint to clarify final action boundary |
| `docs/tos-funder/quick-guide.md` | Updated progress to PR11 completed; next action → "Use in practice" |
| `docs/tos-funder/validation-pr11.md` | Created — this file |

### Files Created

| File | Purpose |
|---|---|
| `docs/tos-funder/validation-pr11.md` | Final hardening validation report |

### Fixed Issues

1. **analyze.md quant routing gap**: Missing explicit `/tos-funder-quant-fundamentals` and `/tos-funder-quant-technicals` command references in the quant family routing table.
2. **risk-manager final action boundary**: Upstream risk-manager command produced `"action": "watch"` in its output example, blurring the final action boundary. Removed; risk ceilings communicated via `action_constraints.action_ceiling`.

### Accepted Exceptions

1. **quant-technicals `"action"` field inside signal object**: `"action": "buy_if_fundamentals_confirm_else_watch"` is a hybrid instruction, not a portfolio action value. Inside signal object, not at output top level. No fix needed.
2. **Value/growth/quant-fundamentals commands without standalone schema anchors**: These are consumed directly by `/tos-funder-analyze` and don't need canonical anchors per `skill-workflow.md` line 24.
3. **Historical audit files containing old enum values**: PR5B/PR8A/PR9A validation docs contain rg check commands referencing old patterns. These are historical and not edited per PR11 scope rules.

### Checks Summary

| Check | Result |
|---|---|
| Command inventory (16) | ✅ All valid frontmatter, all routed in SKILL.md |
| Schema anchors (11) | ✅ All defined and mapped |
| Enum drift | ✅ No drift in active commands/schemas |
| Confidence shape | ✅ All integer (0–100) |
| Final action boundary | ✅ 1 fix applied (risk-manager); all clean |
| Dead iWencai routes | ✅ Not used as executable paths |
| Data source boundaries | ✅ Consistent across all commands |
| Validation index (10 docs) | ✅ Documented |
| Audit trail (7 entries) | ✅ Documented |
