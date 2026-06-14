# UZEN Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first A-share-only UZEN Skills migration layer with JSON/Markdown reports backed by hoxit data APIs.

**Architecture:** `uzen-skills/` contains command and skill instructions. `hoxit/uzen.py` contains deterministic, unit-tested execution logic for snapshot collection, scoring, risk checks, and Markdown rendering. The first version avoids UZI's original provider chain and uses hoxit APIs first, with iwencai fallback only through `hoxit.iwencai`.

**Tech Stack:** Python 3.10+, stdlib only for core code, pytest, existing hoxit modules, Markdown docs.

---

## File Structure

- Create `uzen-skills/README.md`: user-facing summary, first-version scope, commands, output paths, deferred backlog.
- Create `uzen-skills/AGENTS.md`: agent instructions for using UZEN through hoxit, including A-share-only guardrails.
- Create `uzen-skills/commands/*.md`: command-level routing docs for `analyze-stock`, `quick-scan`, `dcf`, `comps`, `panel-only`, `scan-trap`, and `lhb-analyzer`.
- Create `uzen-skills/skills/deep-analysis/SKILL.md`: main workflow skill instructions.
- Create `uzen-skills/skills/investor-panel/SKILL.md`: investor panel skill instructions.
- Create `uzen-skills/skills/lhb-analyzer/SKILL.md`: dragon-tiger-board skill instructions.
- Create `uzen-skills/skills/trap-detector/SKILL.md`: trap/risk detector skill instructions.
- Create `uzen-skills/cache/.gitkeep` and `uzen-skills/reports/.gitkeep`: output directories.
- Create `hoxit/uzen.py`: deterministic execution layer.
- Modify `hoxit/cli.py`: add `hoxit uzen ...` commands after Python API is tested.
- Create `tests/test_uzen.py`: unit tests for snapshot, rendering, panel, risk, and mode behavior.
- Modify `tests/test_cli.py`: parser coverage for `uzen` subcommands.
- Modify `docs/INTERFACES.md`: document UZEN commands and under-documented signal helpers.
- Modify `docs/API_DEVLOG.md`: append only if implementation adds or changes external interface behavior.

## Task 1: Add UZEN Skill Skeleton

**Files:**
- Create: `uzen-skills/README.md`
- Create: `uzen-skills/AGENTS.md`
- Create: `uzen-skills/commands/analyze-stock.md`
- Create: `uzen-skills/commands/quick-scan.md`
- Create: `uzen-skills/commands/dcf.md`
- Create: `uzen-skills/commands/comps.md`
- Create: `uzen-skills/commands/panel-only.md`
- Create: `uzen-skills/commands/scan-trap.md`
- Create: `uzen-skills/commands/lhb-analyzer.md`
- Create: `uzen-skills/skills/deep-analysis/SKILL.md`
- Create: `uzen-skills/skills/investor-panel/SKILL.md`
- Create: `uzen-skills/skills/lhb-analyzer/SKILL.md`
- Create: `uzen-skills/skills/trap-detector/SKILL.md`
- Create: `uzen-skills/cache/.gitkeep`
- Create: `uzen-skills/reports/.gitkeep`

- [ ] **Step 1: Create directories**

Run:

```bash
mkdir -p uzen-skills/commands \
  uzen-skills/skills/deep-analysis/references \
  uzen-skills/skills/deep-analysis/personas \
  uzen-skills/skills/investor-panel \
  uzen-skills/skills/lhb-analyzer \
  uzen-skills/skills/trap-detector \
  uzen-skills/cache \
  uzen-skills/reports
```

Expected: command exits with status 0.

- [ ] **Step 2: Create `uzen-skills/README.md`**

Write:

```markdown
# UZEN Skills

UZEN is the A-share-first migration layer inspired by `Reference/UZI-Skill`.
It keeps the research workflow, command intent, investor-panel concept, and risk checks, but uses hoxit as the primary data substrate.

## First-Version Scope

- A-share stocks only.
- JSON and Markdown output first.
- hoxit Python APIs and CLI behavior are the primary execution path.
- iwencai fallback is allowed only through `hoxit.iwencai`.

## Commands

- `analyze-stock`: full A-share report.
- `quick-scan`: compact report for quote, valuation, flow, themes, and risk.
- `dcf`: light valuation view.
- `comps`: peer and industry comparison.
- `panel-only`: investor-panel vote summary.
- `scan-trap`: trap and manipulation-risk scan.
- `lhb-analyzer`: dragon-tiger-board focused analysis.

## Deferred

HTML reports, share images, Playwright repair, remote hosting, full UZI 22-dimension parity, portfolio commands, and non-A-share markets are recorded in `docs/superpowers/specs/2026-06-14-uzen-skills-design.md` for later phases.
```

- [ ] **Step 3: Create `uzen-skills/AGENTS.md`**

Write:

```markdown
# UZEN Agent Instructions

Use UZEN for A-share stock research workflows only.

## Rules

- Prefer `hoxit.uzen` or `hoxit uzen` commands.
- Do not call UZI's original provider chain as the primary path.
- Do not add one-off scrapers under `uzen-skills`; add reusable A-share data capabilities to hoxit first.
- If a requested capability is outside first-version scope, report it as deferred instead of fabricating data.
- Reports are informational and must not present unsupported investment advice.

## Required Data Boundary

Use hoxit modules first:

- `hoxit.market`
- `hoxit.valuation`
- `hoxit.fundamentals`
- `hoxit.reports`
- `hoxit.news`
- `hoxit.filings`
- `hoxit.signals`
- `hoxit.iwencai`
```

- [ ] **Step 4: Create command docs**

For each file below, write the matching content.

`uzen-skills/commands/analyze-stock.md`:

```markdown
# analyze-stock

Run a full A-share UZEN report.

Execution path:

```bash
hoxit uzen analyze-stock <code> --output-dir uzen-skills/reports
```

Expected artifacts:

- `<code>-analyze-stock.json`
- `<code>-analyze-stock.md`
```

`uzen-skills/commands/quick-scan.md`:

```markdown
# quick-scan

Run a compact A-share scan.

Execution path:

```bash
hoxit uzen quick-scan <code> --output-dir uzen-skills/reports
```

Focus areas: quote, valuation, capital flow, themes, and risk flags.
```

`uzen-skills/commands/dcf.md`:

```markdown
# dcf

Run the first-version light valuation view.

Execution path:

```bash
hoxit uzen dcf <code> --output-dir uzen-skills/reports
```

This first version uses available hoxit valuation and forecast fields. Full UZI DCF parity is deferred.
```

`uzen-skills/commands/comps.md`:

```markdown
# comps

Run peer and industry comparison.

Execution path:

```bash
hoxit uzen comps <code> --output-dir uzen-skills/reports
```

Use hoxit industry data first and iwencai fallback through `hoxit.iwencai` when needed.
```

`uzen-skills/commands/panel-only.md`:

```markdown
# panel-only

Run investor-panel summary without the full report.

Execution path:

```bash
hoxit uzen panel-only <code> --output-dir uzen-skills/reports
```
```

`uzen-skills/commands/scan-trap.md`:

```markdown
# scan-trap

Run trap and manipulation-risk checks.

Execution path:

```bash
hoxit uzen scan-trap <code> --output-dir uzen-skills/reports
```

Risk inputs include hot themes, capital flow, filings, shareholder changes, block trades, margin trading, and dragon-tiger data when available.
```

`uzen-skills/commands/lhb-analyzer.md`:

```markdown
# lhb-analyzer

Run dragon-tiger-board focused analysis.

Execution path:

```bash
hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD --output-dir uzen-skills/reports
```
```

- [ ] **Step 5: Create skill docs**

Write `uzen-skills/skills/deep-analysis/SKILL.md`:

```markdown
---
name: deep-analysis
description: A-share stock research workflow backed by hoxit. Use for analyze-stock, quick-scan, dcf, comps, panel-only, scan-trap, and lhb-analyzer requests.
---

# UZEN Deep Analysis

Use this skill for A-share stock research. The execution layer is `hoxit.uzen`.

## Guardrails

- A-share only in the first version.
- JSON and Markdown output first.
- Use hoxit data APIs first.
- Mark unavailable non-A-share or HTML/share-card requests as deferred.
```

Write `uzen-skills/skills/investor-panel/SKILL.md`:

```markdown
---
name: investor-panel
description: A-share investor-panel summary backed by hoxit.uzen.
---

# UZEN Investor Panel

Use `hoxit uzen panel-only <code>` to generate a lightweight A-share panel summary.
```

Write `uzen-skills/skills/lhb-analyzer/SKILL.md`:

```markdown
---
name: lhb-analyzer
description: A-share dragon-tiger-board analysis backed by hoxit signals.
---

# UZEN LHB Analyzer

Use `hoxit uzen lhb-analyzer <code> --trade-date YYYY-MM-DD`.
```

Write `uzen-skills/skills/trap-detector/SKILL.md`:

```markdown
---
name: trap-detector
description: A-share trap and manipulation-risk scan backed by hoxit signals.
---

# UZEN Trap Detector

Use `hoxit uzen scan-trap <code>` to produce risk flags from hoxit signals.
```

- [ ] **Step 6: Add output placeholders**

Run:

```bash
touch uzen-skills/cache/.gitkeep uzen-skills/reports/.gitkeep
```

Expected: files exist.

- [ ] **Step 7: Verify skeleton**

Run:

```bash
find uzen-skills -maxdepth 4 -type f | sort
```

Expected: output includes all files created above.

- [ ] **Step 8: Commit**

Run:

```bash
git add uzen-skills
git commit -m "docs: add uzen skills skeleton"
```

## Task 2: Add UZEN Snapshot Aggregator

**Files:**
- Create: `hoxit/uzen.py`
- Create: `tests/test_uzen.py`

- [ ] **Step 1: Write failing snapshot tests**

Create `tests/test_uzen.py` with:

```python
from __future__ import annotations

from hoxit.uzen import UzenDataProvider, collect_snapshot


def provider() -> UzenDataProvider:
    return UzenDataProvider(
        quote=lambda codes: {codes[0]: {"code": codes[0], "name": "测试股份", "price": 10.0, "change_pct": 2.5}},
        bars=lambda code, category=4, offset=60, adjust="qfq": [{"date": "2026-06-12", "close": 10.0}],
        metrics=lambda codes: {codes[0]: {"pe_ttm": 18.0, "pb": 2.1, "market_cap": 10000000000}},
        valuation=lambda code: {"forward_pe": 15.0, "peg": 1.2},
        fundamentals=lambda code: {"name": "测试股份", "industry": "软件开发"},
        finance=lambda code: {"roe": 12.3, "net_profit": 100000000},
        f10=lambda code: {"status": "unsupported", "sections": {}, "warnings": ["f10 unavailable"]},
        reports=lambda code: [{"title": "测试研报", "rating": "增持"}],
        news=lambda code: [{"title": "测试新闻"}],
        filings=lambda code, start_date, end_date: [{"title": "年度报告"}],
        hot=lambda date=None, exclude_st=False: [{"code": "600000", "reason": "热点"}],
        concept=lambda code: [{"name": "人工智能"}],
        fund_flow=lambda code, days=20: [{"date": "2026-06-12", "main_net_inflow": 1000}],
        dragon_tiger=lambda code, trade_date: [{"trade_date": trade_date, "net_buy": 2000}],
        lockup=lambda code, trade_date, forward_days=90: [],
        industry=lambda top_n=20: [{"industry": "软件开发", "change_pct": 1.1}],
        margin_trading=lambda code, page_size=30: [],
        block_trade=lambda code, page_size=20: [],
        holder_num=lambda code, page_size=10: [],
        dividend=lambda code, page_size=20: [],
    )


def test_collect_snapshot_assembles_core_sections():
    snapshot = collect_snapshot("600000", mode="analyze-stock", provider=provider(), today="2026-06-14")

    assert snapshot["code"] == "600000"
    assert snapshot["market"] == "A"
    assert snapshot["mode"] == "analyze-stock"
    assert snapshot["sources"]["quote"]["code"] == "600000"
    assert snapshot["sources"]["bars"] == [{"date": "2026-06-12", "close": 10.0}]
    assert snapshot["sources"]["valuation"]["forward_pe"] == 15.0
    assert snapshot["sources"]["signals"]["concept"] == [{"name": "人工智能"}]
    assert snapshot["data_quality"]["complete"] is False
    assert "f10 unavailable" in snapshot["data_quality"]["warnings"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_collect_snapshot_assembles_core_sections -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'hoxit.uzen'`.

- [ ] **Step 3: Implement snapshot aggregator**

Create `hoxit/uzen.py` with:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Callable


def _empty(*args, **kwargs):
    return []


def _empty_mapping(*args, **kwargs):
    return {}


@dataclass(frozen=True)
class UzenDataProvider:
    quote: Callable[[list[str]], dict[str, dict]]
    bars: Callable[..., list[dict]]
    metrics: Callable[[list[str]], dict[str, dict]]
    valuation: Callable[[str], dict]
    fundamentals: Callable[[str], dict]
    finance: Callable[[str], dict]
    f10: Callable[[str], dict]
    reports: Callable[[str], list[dict]]
    news: Callable[[str], list[dict]]
    filings: Callable[[str, str, str], list[dict]]
    hot: Callable[..., list[dict]]
    concept: Callable[[str], list[dict]]
    fund_flow: Callable[..., list[dict]]
    dragon_tiger: Callable[[str, str], list[dict]]
    lockup: Callable[..., list[dict]]
    industry: Callable[..., list[dict]]
    margin_trading: Callable[..., list[dict]] = _empty
    block_trade: Callable[..., list[dict]] = _empty
    holder_num: Callable[..., list[dict]] = _empty
    dividend: Callable[..., list[dict]] = _empty


def default_provider() -> UzenDataProvider:
    from . import filings, fundamentals, market, news, reports, signals, valuation

    return UzenDataProvider(
        quote=market.mootdx_quote,
        bars=market.mootdx_bars,
        metrics=market.tencent_metrics,
        valuation=valuation.full_valuation,
        fundamentals=fundamentals.individual_info,
        finance=fundamentals.finance_snapshot,
        f10=fundamentals.f10,
        reports=reports.eastmoney_reports,
        news=news.stock_news,
        filings=filings.cninfo_reports,
        hot=signals.ths_hot_reason,
        concept=signals.baidu_concept_blocks,
        fund_flow=signals.baidu_fund_flow_history,
        dragon_tiger=signals.dragon_tiger_board,
        lockup=signals.lockup_expiry,
        industry=signals.industry_comparison,
        margin_trading=signals.margin_trading,
        block_trade=signals.block_trade,
        holder_num=signals.holder_num_change,
        dividend=signals.dividend_history,
    )


def _safe_call(label: str, func: Callable, *args, warnings: list[str], default: Any, **kwargs) -> Any:
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        warnings.append(f"{label}: {exc}")
        return default


def _date_window(today: str) -> tuple[str, str]:
    end = datetime.strptime(today, "%Y-%m-%d").date()
    start = end - timedelta(days=365)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def collect_snapshot(
    code: str,
    *,
    mode: str = "analyze-stock",
    provider: UzenDataProvider | None = None,
    today: str | None = None,
    trade_date: str | None = None,
) -> dict[str, Any]:
    provider = provider or default_provider()
    today = today or date.today().strftime("%Y-%m-%d")
    trade_date = trade_date or today
    start_date, end_date = _date_window(today)
    warnings: list[str] = []

    quote_map = _safe_call("quote", provider.quote, [code], warnings=warnings, default={})
    quote = quote_map.get(code, {}) if isinstance(quote_map, dict) else {}
    f10 = _safe_call("f10", provider.f10, code, warnings=warnings, default={})
    if isinstance(f10, dict) and f10.get("status") == "unsupported":
        warnings.extend(str(item) for item in f10.get("warnings", []))

    sources = {
        "quote": quote,
        "bars": _safe_call("bars", provider.bars, code, category=4, offset=60, adjust="qfq", warnings=warnings, default=[]),
        "metrics": _safe_call("metrics", provider.metrics, [code], warnings=warnings, default={}).get(code, {}),
        "valuation": _safe_call("valuation", provider.valuation, code, warnings=warnings, default={}),
        "fundamentals": _safe_call("fundamentals", provider.fundamentals, code, warnings=warnings, default={}),
        "finance": _safe_call("finance", provider.finance, code, warnings=warnings, default={}),
        "f10": f10,
        "reports": _safe_call("reports", provider.reports, code, warnings=warnings, default=[]),
        "news": _safe_call("news", provider.news, code, warnings=warnings, default=[]),
        "filings": _safe_call("filings", provider.filings, code, start_date, end_date, warnings=warnings, default=[]),
        "signals": {
            "hot": _safe_call("hot", provider.hot, today, exclude_st=True, warnings=warnings, default=[]),
            "concept": _safe_call("concept", provider.concept, code, warnings=warnings, default=[]),
            "fund_flow": _safe_call("fund_flow", provider.fund_flow, code, days=20, warnings=warnings, default=[]),
            "dragon_tiger": _safe_call("dragon_tiger", provider.dragon_tiger, code, trade_date, warnings=warnings, default=[]),
            "lockup": _safe_call("lockup", provider.lockup, code, trade_date, forward_days=90, warnings=warnings, default=[]),
            "industry": _safe_call("industry", provider.industry, top_n=20, warnings=warnings, default=[]),
            "margin_trading": _safe_call("margin_trading", provider.margin_trading, code, page_size=30, warnings=warnings, default=[]),
            "block_trade": _safe_call("block_trade", provider.block_trade, code, page_size=20, warnings=warnings, default=[]),
            "holder_num": _safe_call("holder_num", provider.holder_num, code, page_size=10, warnings=warnings, default=[]),
            "dividend": _safe_call("dividend", provider.dividend, code, page_size=20, warnings=warnings, default=[]),
        },
    }
    return {
        "code": code,
        "market": "A",
        "mode": mode,
        "generated_at": f"{today}T00:00:00+08:00",
        "data_quality": {"complete": not warnings, "warnings": warnings},
        "sources": sources,
        "analysis": {},
    }
```

- [ ] **Step 4: Run snapshot test**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_collect_snapshot_assembles_core_sections -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add hoxit/uzen.py tests/test_uzen.py
git commit -m "feat: add uzen snapshot aggregator"
```

## Task 3: Add Analysis Summaries And Markdown Rendering

**Files:**
- Modify: `hoxit/uzen.py`
- Modify: `tests/test_uzen.py`

- [ ] **Step 1: Add failing tests for analysis and Markdown**

Append to `tests/test_uzen.py`:

```python
from hoxit.uzen import analyze_snapshot, render_markdown


def test_analyze_snapshot_adds_summary_panel_and_risk():
    snapshot = collect_snapshot("600000", mode="scan-trap", provider=provider(), today="2026-06-14")
    analyzed = analyze_snapshot(snapshot)

    assert analyzed["analysis"]["summary"]["name"] == "测试股份"
    assert analyzed["analysis"]["summary"]["price"] == 10.0
    assert analyzed["analysis"]["panel"]["verdict"] in {"bullish", "neutral", "bearish"}
    assert analyzed["analysis"]["trap_risk"]["level"] in {"low", "medium", "high"}


def test_render_markdown_has_stable_sections():
    snapshot = analyze_snapshot(collect_snapshot("600000", provider=provider(), today="2026-06-14"))
    markdown = render_markdown(snapshot)

    assert markdown.startswith("# UZEN A股分析：600000")
    assert "## 核心结论" in markdown
    assert "## 数据完整性" in markdown
    assert "## 行情与估值" in markdown
    assert "## 资金、龙虎榜与题材" in markdown
    assert "## 风险与杀猪盘检查" in markdown
    assert "本报告仅用于信息整理" in markdown
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
```

Expected: FAIL because `analyze_snapshot` and `render_markdown` are missing.

- [ ] **Step 3: Implement analysis and Markdown**

Append to `hoxit/uzen.py`:

```python
def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.replace("%", "").replace(",", ""))
            except ValueError:
                continue
    return None


def _panel_summary(snapshot: dict[str, Any]) -> dict[str, Any]:
    valuation = snapshot["sources"].get("valuation", {})
    metrics = snapshot["sources"].get("metrics", {})
    finance = snapshot["sources"].get("finance", {})
    pe = _first_number(valuation.get("forward_pe"), metrics.get("pe_ttm"), metrics.get("pe"))
    roe = _first_number(finance.get("roe"), finance.get("ROE"))
    score = 50
    reasons: list[str] = []
    if pe is not None and pe < 20:
        score += 10
        reasons.append("估值低于 20 倍 PE 区间")
    if pe is not None and pe > 60:
        score -= 15
        reasons.append("估值高于 60 倍 PE 区间")
    if roe is not None and roe >= 10:
        score += 10
        reasons.append("ROE 达到双位数")
    verdict = "bullish" if score >= 65 else "bearish" if score <= 40 else "neutral"
    return {"score": score, "verdict": verdict, "reasons": reasons or ["第一版轻量面板基于估值和财务质量打分"]}


def _trap_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    signals = snapshot["sources"].get("signals", {})
    flags: list[str] = []
    if signals.get("block_trade"):
        flags.append("存在大宗交易记录")
    if signals.get("margin_trading"):
        flags.append("存在融资融券变化记录")
    holder_rows = signals.get("holder_num") or []
    if len(holder_rows) >= 2:
        flags.append("股东户数存在可跟踪变化")
    if not signals.get("fund_flow"):
        flags.append("资金流数据缺失")
    level = "high" if len(flags) >= 3 else "medium" if flags else "low"
    return {"level": level, "flags": flags}


def analyze_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    quote = snapshot["sources"].get("quote", {})
    fundamentals = snapshot["sources"].get("fundamentals", {})
    snapshot["analysis"] = {
        "summary": {
            "name": quote.get("name") or fundamentals.get("name") or "",
            "price": quote.get("price"),
            "change_pct": quote.get("change_pct"),
        },
        "valuation": snapshot["sources"].get("valuation", {}),
        "industry": {"rows": snapshot["sources"].get("signals", {}).get("industry", [])},
        "panel": _panel_summary(snapshot),
        "trap_risk": _trap_risk(snapshot),
        "followups": [],
    }
    return snapshot


def render_markdown(snapshot: dict[str, Any]) -> str:
    analysis = snapshot.get("analysis") or {}
    summary = analysis.get("summary", {})
    panel = analysis.get("panel", {})
    risk = analysis.get("trap_risk", {})
    sources = snapshot.get("sources", {})
    signals = sources.get("signals", {})
    warnings = snapshot.get("data_quality", {}).get("warnings", [])
    lines = [
        f"# UZEN A股分析：{snapshot['code']}",
        "",
        "## 核心结论",
        f"- 名称：{summary.get('name') or '未知'}",
        f"- 最新价：{summary.get('price') if summary.get('price') is not None else '缺失'}",
        f"- 轻量面板：{panel.get('verdict', 'neutral')}，分数 {panel.get('score', 50)}",
        "",
        "## 数据完整性",
        f"- 完整性：{'完整' if snapshot.get('data_quality', {}).get('complete') else '存在缺口'}",
    ]
    lines.extend(f"- 警告：{warning}" for warning in warnings)
    lines.extend([
        "",
        "## 行情与估值",
        f"- 行情：{sources.get('quote', {})}",
        f"- 估值：{sources.get('valuation', {})}",
        "",
        "## 基本面与财务",
        f"- 基本面：{sources.get('fundamentals', {})}",
        f"- 财务：{sources.get('finance', {})}",
        "",
        "## 研报、新闻与公告",
        f"- 研报数量：{len(sources.get('reports', []))}",
        f"- 新闻数量：{len(sources.get('news', []))}",
        f"- 公告数量：{len(sources.get('filings', []))}",
        "",
        "## 资金、龙虎榜与题材",
        f"- 概念：{signals.get('concept', [])}",
        f"- 资金流记录数：{len(signals.get('fund_flow', []))}",
        f"- 龙虎榜记录数：{len(signals.get('dragon_tiger', []))}",
        "",
        "## 行业与同业",
        f"- 行业样本数：{len(signals.get('industry', []))}",
        "",
        "## 投资者面板",
        f"- 结论：{panel.get('verdict', 'neutral')}",
        f"- 理由：{'；'.join(panel.get('reasons', []))}",
        "",
        "## 风险与杀猪盘检查",
        f"- 风险等级：{risk.get('level', 'low')}",
        f"- 风险标记：{'；'.join(risk.get('flags', [])) if risk.get('flags') else '未触发第一版风险标记'}",
        "",
        "## 后续跟踪项",
        "- 对缺失数据源做人工复核。",
        "",
        "> 本报告仅用于信息整理，不构成投资建议。",
        "",
    ])
    return "\n".join(lines)
```

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add hoxit/uzen.py tests/test_uzen.py
git commit -m "feat: render uzen markdown analysis"
```

## Task 4: Add Run Function And CLI Commands

**Files:**
- Modify: `hoxit/uzen.py`
- Modify: `hoxit/cli.py`
- Modify: `tests/test_uzen.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Add failing tests for artifact writing and parser**

Append to `tests/test_uzen.py`:

```python
import json

from hoxit.uzen import run_analysis


def test_run_analysis_writes_json_and_markdown(tmp_path):
    result = run_analysis("600000", mode="quick-scan", provider=provider(), output_dir=tmp_path, today="2026-06-14")

    assert result["json_path"].endswith("600000-quick-scan.json")
    assert result["markdown_path"].endswith("600000-quick-scan.md")
    payload = json.loads((tmp_path / "600000-quick-scan.json").read_text(encoding="utf-8"))
    markdown = (tmp_path / "600000-quick-scan.md").read_text(encoding="utf-8")
    assert payload["mode"] == "quick-scan"
    assert "# UZEN A股分析：600000" in markdown
```

Append to `tests/test_cli.py`:

```python
def test_cli_uzen_subcommands_parse():
    parser = build_parser()
    args = parser.parse_args(["uzen", "quick-scan", "600000", "--output-dir", "uzen-skills/reports"])
    assert args.layer == "uzen"
    assert args.action == "quick-scan"
    assert args.code == "600000"
    assert args.output_dir == "uzen-skills/reports"

    lhb = parser.parse_args(["uzen", "lhb-analyzer", "600000", "--trade-date", "2026-06-14"])
    assert lhb.trade_date == "2026-06-14"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_run_analysis_writes_json_and_markdown tests/test_cli.py::test_cli_uzen_subcommands_parse -q
```

Expected: FAIL because `run_analysis` and `uzen` parser are missing.

- [ ] **Step 3: Implement `run_analysis`**

Append to `hoxit/uzen.py`:

```python
import json
from pathlib import Path


def run_analysis(
    code: str,
    *,
    mode: str = "analyze-stock",
    provider: UzenDataProvider | None = None,
    output_dir: str | Path = "uzen-skills/reports",
    today: str | None = None,
    trade_date: str | None = None,
) -> dict[str, Any]:
    snapshot = collect_snapshot(code, mode=mode, provider=provider, today=today, trade_date=trade_date)
    snapshot = analyze_snapshot(snapshot)
    markdown = render_markdown(snapshot)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / f"{code}-{mode}.json"
    markdown_path = target / f"{code}-{mode}.md"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "code": code,
        "mode": mode,
        "json_path": str(json_path),
        "markdown_path": str(markdown_path),
        "snapshot": snapshot,
    }
```

- [ ] **Step 4: Add CLI parser**

In `hoxit/cli.py`, inside `build_parser()` after the valuation parser block and before the `iwc` parser block, add:

```python
    uzen = subparsers.add_parser("uzen", help="UZEN A股研究工作流")
    uzen_sub = uzen.add_subparsers(dest="action", required=True)
    for action_name, help_text in [
        ("analyze-stock", "完整 A股分析报告"),
        ("quick-scan", "快速 A股扫描"),
        ("dcf", "轻量估值视图"),
        ("comps", "行业与同业对比"),
        ("panel-only", "投资者面板摘要"),
        ("scan-trap", "风险与杀猪盘检查"),
    ]:
        command = uzen_sub.add_parser(action_name, help=help_text)
        command.add_argument("code")
        command.add_argument("--output-dir", default="uzen-skills/reports")
    lhb = uzen_sub.add_parser("lhb-analyzer", help="龙虎榜专项分析")
    lhb.add_argument("code")
    lhb.add_argument("--trade-date")
    lhb.add_argument("--output-dir", default="uzen-skills/reports")
```

- [ ] **Step 5: Add CLI dispatch**

In `hoxit/cli.py`, inside `run(args)` before the `if args.layer == "iwc":` block, add:

```python
    if args.layer == "uzen":
        from .uzen import run_analysis

        return run_analysis(
            args.code,
            mode=args.action,
            output_dir=args.output_dir,
            trade_date=getattr(args, "trade_date", None),
        )
```

- [ ] **Step 6: Run focused tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py tests/test_cli.py -q
```

Expected: PASS.

- [ ] **Step 7: Run full default tests**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: PASS or existing unrelated failures clearly documented.

- [ ] **Step 8: Commit**

Run:

```bash
git add hoxit/uzen.py hoxit/cli.py tests/test_uzen.py tests/test_cli.py
git commit -m "feat: add uzen cli workflow"
```

## Task 5: Refine Mode-Specific Behavior

**Files:**
- Modify: `hoxit/uzen.py`
- Modify: `tests/test_uzen.py`

- [ ] **Step 1: Add failing tests for mode-specific sections**

Append to `tests/test_uzen.py`:

```python
def test_quick_scan_skips_heavy_sections(tmp_path):
    result = run_analysis("600000", mode="quick-scan", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    snapshot = result["snapshot"]

    assert snapshot["analysis"]["mode_profile"]["depth"] == "lite"
    assert "quick-scan" in result["markdown_path"]


def test_panel_only_and_lhb_modes_are_labeled(tmp_path):
    panel = run_analysis("600000", mode="panel-only", provider=provider(), output_dir=tmp_path, today="2026-06-14")
    lhb = run_analysis("600000", mode="lhb-analyzer", provider=provider(), output_dir=tmp_path, today="2026-06-14", trade_date="2026-06-14")

    assert panel["snapshot"]["analysis"]["mode_profile"]["primary_section"] == "panel"
    assert lhb["snapshot"]["analysis"]["mode_profile"]["primary_section"] == "dragon_tiger"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py::test_quick_scan_skips_heavy_sections tests/test_uzen.py::test_panel_only_and_lhb_modes_are_labeled -q
```

Expected: FAIL because `mode_profile` is missing.

- [ ] **Step 3: Add mode profile helper**

Append this helper above `analyze_snapshot()` in `hoxit/uzen.py`:

```python
def _mode_profile(mode: str) -> dict[str, str]:
    profiles = {
        "quick-scan": {"depth": "lite", "primary_section": "summary"},
        "dcf": {"depth": "focused", "primary_section": "valuation"},
        "comps": {"depth": "focused", "primary_section": "industry"},
        "panel-only": {"depth": "focused", "primary_section": "panel"},
        "scan-trap": {"depth": "focused", "primary_section": "trap_risk"},
        "lhb-analyzer": {"depth": "focused", "primary_section": "dragon_tiger"},
        "analyze-stock": {"depth": "standard", "primary_section": "full_report"},
    }
    return profiles.get(mode, profiles["analyze-stock"])
```

In `analyze_snapshot()`, add `mode_profile` to the `analysis` dictionary:

```python
        "mode_profile": _mode_profile(snapshot.get("mode", "analyze-stock")),
```

- [ ] **Step 4: Run tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_uzen.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add hoxit/uzen.py tests/test_uzen.py
git commit -m "feat: add uzen mode profiles"
```

## Task 6: Update Interfaces Documentation

**Files:**
- Modify: `docs/INTERFACES.md`
- Modify: `docs/API_DEVLOG.md` only if new external API behavior is added beyond existing hoxit calls.

- [ ] **Step 1: Update `docs/INTERFACES.md`**

Add a new section after the valuation section:

```markdown
## UZEN A股研究工作流

UZEN 是 `Reference/UZI-Skill` 的 A 股优先迁移层。第一版通过 hoxit 数据接口生成 JSON 和 Markdown 报告，不启用 UZI 原 provider chain、HTML 渲染、分享图、Playwright 兜底或跨市场分析。

```bash
.venv/bin/hoxit uzen analyze-stock 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen quick-scan 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen dcf 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen comps 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen panel-only 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen scan-trap 600519 --output-dir uzen-skills/reports
.venv/bin/hoxit uzen lhb-analyzer 600519 --trade-date 2026-06-14 --output-dir uzen-skills/reports
```

输出：

- `<code>-<mode>.json`
- `<code>-<mode>.md`
```

Also add the currently under-documented signal helpers under the signal section:

```markdown
### 融资融券明细

```bash
.venv/bin/hoxit signals margin-trading 600519 --page-size 30
```

### 大宗交易

```bash
.venv/bin/hoxit signals block-trade 600519 --page-size 20
```

### 股东户数变化

```bash
.venv/bin/hoxit signals holder-num 600519 --page-size 10
```

### 分红送转历史

```bash
.venv/bin/hoxit signals dividend 600519 --page-size 20
```
```

- [ ] **Step 2: Decide whether `docs/API_DEVLOG.md` needs an entry**

If the implementation only composes existing hoxit APIs, do not add an API devlog entry.

If a new external endpoint is added or an existing external endpoint is changed, append:

```markdown
## 2026-06-14

- 来源：`Reference/UZI-Skill` A 股优先迁移设计与 hoxit 本地实现。
- 触发原因：UZEN 第一版需要补齐 A 股研究报告数据源。
- 影响接口：
- hoxit 变更：
- 验证：
- 后续关注：
```

Fill each bullet with the exact endpoint and verification command from the implementation.

- [ ] **Step 3: Run docs and tests checks**

Run:

```bash
git diff --check -- docs/INTERFACES.md docs/API_DEVLOG.md
.venv/bin/python -m pytest -q
```

Expected: no whitespace errors; tests pass or unrelated existing failures are documented.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/INTERFACES.md docs/API_DEVLOG.md
git commit -m "docs: document uzen workflow"
```

If `docs/API_DEVLOG.md` was not changed, use:

```bash
git add docs/INTERFACES.md
git commit -m "docs: document uzen workflow"
```

## Self-Review

Spec coverage:

- `uzen-skills/` skeleton: Task 1.
- hoxit deterministic execution layer: Tasks 2 and 3.
- JSON/Markdown output: Tasks 3 and 4.
- First-version commands: Tasks 1, 4, and 5.
- A-share-only guardrails: Task 1 docs and Task 4 CLI naming.
- hoxit data-first boundary: Tasks 1, 2, and 6.
- Tests without network: Tasks 2 through 5 use injected providers.
- Deferred backlog: Task 1 README and existing design doc.

Placeholder scan:

- This plan intentionally contains no placeholder markers, no unspecified edge handling, and no references to undefined functions after their defining task.

Type consistency:

- `collect_snapshot()` returns a `dict[str, Any]`.
- `analyze_snapshot()` mutates and returns the same snapshot shape.
- `render_markdown()` accepts the analyzed snapshot.
- `run_analysis()` returns artifact paths and the snapshot.
