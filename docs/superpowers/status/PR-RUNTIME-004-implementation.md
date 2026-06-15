---
title: "PR-RUNTIME-004 Implementation Report"
pr: "PR-RUNTIME-004"
scope: "uzen runtime docs sync"
status: "IMPLEMENTED"
date: "2026-06-15"
updated: "2026-06-15"
---

# PR-RUNTIME-004: UZEN Runtime Docs Sync

## Summary

Updated user-facing docs to reflect runtime mode execution profiles, structured source quality records, and Markdown report contract.

## Deliverables

### 1. `docs/INTERFACES.md`

Updated UZEN section with:
- Mode execution profiles table (7 modes with their providers)
- Data quality records structure and quality values
- Markdown report contract (compact formatting)
- Current limitations
- Deferred UZI parity items

### 2. `uzen-skills/README.md`

Updated with:
- Runtime behavior section
- Mode execution profiles table
- Source quality records explanation
- Markdown report contract
- Current limitations
- Deferred items (separated from limitations)

### 3. Command Docs (`uzen-skills/commands/*.md`)

Updated all 7 command docs with:
- Data providers section (which providers each mode calls)
- Mode profile section (depth and primary_section)
- Consistent formatting

| Command | Providers | Mode Profile |
|---------|-----------|--------------|
| analyze-stock | All 20 | standard / full_report |
| quick-scan | 6 | lite / summary |
| panel-only | 5 | focused / panel |
| scan-trap | 8 | focused / trap_risk |
| lhb-analyzer | 7 | focused / dragon_tiger |
| dcf | 5 | focused / valuation |
| comps | 4 | focused / industry |

### 4. `docs/superpowers/status/PR-RUNTIME-004-implementation.md`

This report.

## Verification

```
$ git diff --check -- docs/INTERFACES.md uzen-skills docs/superpowers/status/PR-RUNTIME-004-implementation.md
(no output)

$ .venv/bin/hoxit uzen --help
usage: hoxit uzen [-h]
                  {analyze-stock,quick-scan,dcf,comps,panel-only,scan-trap,lhb-analyzer}
                  ...
```

## Acceptance Criteria Checklist

- [x] `docs/INTERFACES.md` reflects current UZEN JSON and Markdown behavior.
- [x] Command docs do not claim unavailable runtime capabilities.
- [x] Docs clearly distinguish current runtime support from deferred UZI parity.
- [x] No production code changes are included.

## Changes Summary

| File | Changes |
|------|---------|
| `docs/INTERFACES.md` | Added mode profiles, quality records, Markdown contract, limitations, deferred items |
| `uzen-skills/README.md` | Added runtime behavior section, limitations, deferred items |
| `uzen-skills/commands/analyze-stock.md` | Added providers, mode profile, JSON structure |
| `uzen-skills/commands/quick-scan.md` | Added providers, mode profile, output |
| `uzen-skills/commands/dcf.md` | Added providers, mode profile, limitations |
| `uzen-skills/commands/comps.md` | Added providers, mode profile, notes (iwencai deferred) |
| `uzen-skills/commands/panel-only.md` | Added providers, mode profile |
| `uzen-skills/commands/scan-trap.md` | Added providers, mode profile, corrected data inputs |
| `uzen-skills/commands/lhb-analyzer.md` | Added providers, mode profile |

## Review Fixes

### Fix 1: scan-trap lockup overclaim

**Issue**: Data Inputs section listed `lockup_expiry` but `scan-trap` mode does not call it.

**Fix**: Removed lockup from Data Inputs. Updated list to match `_MODE_SOURCES["scan-trap"]`:
- quote, bars, concept, fund_flow, margin_trading, block_trade, holder_num, dragon_tiger

### Fix 2: comps iwencai fallback overclaim

**Issue**: Notes section claimed iwencai fallback but UZEN comps runtime does not call `hoxit.iwencai`.

**Fix**: Rewrote Notes to clarify:
- Current behavior uses `hoxit.signals.industry_comparison`
- iwencai peer fallback is deferred — not wired into UZEN comps runtime

### Fix 3: 中文优先（Chinese-first style）

**Issue**: 文档使用英文，与项目中文优先风格不一致。

**修正**：
- `uzen-skills/README.md`：全部改为中文，保留命令名、字段名、provider 名、JSON key 为英文
- `uzen-skills/commands/*.md`：7 个命令文档全部改为中文
- 关键术语中英文对照：运行时行为（Runtime Behavior）、模式执行配置（Mode Execution Profile）、数据质量（Data Quality）、延迟能力（Deferred Capability）
- `docs/INTERFACES.md` 已在之前 PR 中改为中文，本次未修改

### Fix 4: 标题清理（Heading cleanup）

**Issue**: 部分标题仍为英文（如 `Data Providers`、`Mode Profile`）。

**修正**：将 7 个命令文档中的英文标题改为中文优先或中英文对照：
- `## Data Providers` → `## 数据提供方（Data Providers）`
- `## Mode Profile` → `## 模式配置（Mode Profile）`

命令名、provider 名、JSON key、CLI 参数保持英文原文。
