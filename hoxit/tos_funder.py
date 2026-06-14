from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping


CORE_SPINE_LAYERS = [
    "quant-price-series",
    "value-buffett",
    "value-graham",
    "growth",
    "quant-fundamentals",
    "quant-technicals",
    "quant-sentiment",
    "risk-manager",
    "tactical",
    "macro-topdown",
    "portfolio",
]

EXPANDED_MIGRATED_LAYERS = [
    "value-munger",
    "value-burry",
    "value-pabrai",
    "growth-cathie-wood",
    "quant-valuation",
    "quant-valuation-damodaran",
    "tactical-ackman",
    "tactical-taleb",
    "macro-druckenmiller",
    "macro-jhunjhunwala",
    "news-sentiment",
]

FULL_RUN_LAYERS = CORE_SPINE_LAYERS + EXPANDED_MIGRATED_LAYERS


REPORT_FILES = {
    "value-buffett": "01-value-buffett.md",
    "value-graham": "02-value-graham.md",
    "growth": "03-growth.md",
    "quant-fundamentals": "04-quant-fundamentals.md",
    "quant-price-series": "05-price-series.md",
    "quant-technicals": "06-quant-technicals.md",
    "quant-sentiment": "07-sentiment.md",
    "risk-manager": "08-risk-manager.md",
    "tactical": "09-tactical.md",
    "macro-topdown": "10-macro-topdown.md",
    "portfolio": "11-portfolio-decision.md",
    "value-munger": "12-value-munger.md",
    "value-burry": "13-value-burry.md",
    "value-pabrai": "14-value-pabrai.md",
    "growth-cathie-wood": "15-growth-cathie-wood.md",
    "quant-valuation": "16-quant-valuation.md",
    "quant-valuation-damodaran": "17-quant-valuation-damodaran.md",
    "tactical-ackman": "18-tactical-ackman.md",
    "tactical-taleb": "19-tactical-taleb.md",
    "macro-druckenmiller": "20-macro-druckenmiller.md",
    "macro-jhunjhunwala": "21-macro-jhunjhunwala.md",
    "news-sentiment": "22-news-sentiment.md",
}

LAYER_ALIASES = {
    "price-series": "quant-price-series",
}


def sample_stdev(values: Iterable[float]) -> float | None:
    """Return sample standard deviation without relying on statistics.stdev internals."""
    vals = [float(value) for value in values]
    if len(vals) < 2:
        return None
    mean = sum(vals) / len(vals)
    variance = sum((value - mean) ** 2 for value in vals) / (len(vals) - 1)
    return math.sqrt(variance)


def annualized_volatility(returns: Iterable[float], trading_days: int = 252) -> float | None:
    stdev = sample_stdev(returns)
    if stdev is None:
        return None
    return stdev * math.sqrt(trading_days)


def complete_full_run_layers() -> list[str]:
    return list(FULL_RUN_LAYERS)


def expected_full_run_reports() -> list[str]:
    return ["00-summary.md"] + [REPORT_FILES[layer] for layer in FULL_RUN_LAYERS]


def missing_full_run_layers(completed: Iterable[str]) -> list[str]:
    completed_set = {_canonical_layer(layer) for layer in completed}
    return [layer for layer in FULL_RUN_LAYERS if layer not in completed_set]


def full_run_status(completed: Iterable[str]) -> str:
    completed_set = {_canonical_layer(layer) for layer in completed}
    missing = missing_full_run_layers(completed_set)
    if not missing:
        return "complete"
    if all(layer in completed_set for layer in CORE_SPINE_LAYERS):
        return "core_spine_only"
    return "partial_full"


def _canonical_layer(layer: str) -> str:
    return LAYER_ALIASES.get(layer, layer)


def validate_full_run_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    completed = list(manifest.get("commands_completed", []))
    reports = set(manifest.get("reports_written", []))
    missing_layers = missing_full_run_layers(completed)
    missing_reports = [
        report for report in expected_full_run_reports() if report not in reports
    ]
    expanded_count = manifest.get("expanded_signal_count")
    status = full_run_status(completed)
    return {
        "status": status,
        "complete": status == "complete" and not missing_reports,
        "missing_layers": missing_layers,
        "missing_reports": missing_reports,
        "expanded_signal_count": expanded_count,
    }


def signal_value(layer: Mapping[str, Any]) -> str:
    portfolio_decision = layer.get("portfolio_decision")
    if isinstance(portfolio_decision, Mapping):
        return str(portfolio_decision.get("action") or "n/a")
    return str(layer.get("signal") or layer.get("risk_level") or "n/a")


def confidence_value(layer: Mapping[str, Any]) -> int | str:
    portfolio_decision = layer.get("portfolio_decision")
    if isinstance(portfolio_decision, Mapping) and portfolio_decision.get("confidence") is not None:
        return int(portfolio_decision["confidence"])
    if layer.get("confidence") is None:
        return "-"
    return int(layer["confidence"])


def write_stock_index(
    base_dir: str | Path,
    *,
    stock_name: str,
    stock_code: str,
    run_id: str,
    decision: Mapping[str, Any],
    signal_rows: Iterable[Mapping[str, Any]],
    watch_triggers: Iterable[str] = (),
) -> Path:
    """Write the durable stock entry file requested by the POS tos-funder workflow."""
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)
    filename = f"{stock_name}.md"
    path = base / filename

    rows = list(signal_rows)
    lines = [
        f"# {stock_name} {stock_code}",
        "",
        f"**入口文件**: `{path}`",
        "",
        "## Latest Decision",
        "",
        f"- Action: **{decision.get('action', 'n/a')}**",
        f"- Confidence: **{decision.get('confidence', 'n/a')}**",
        "- Source: `/tos-funder-portfolio`",
        f"- Latest run: `{run_id}`",
        f"- Expanded dimensions: **{len(rows)}**",
        "",
        "## Expanded Signal Matrix",
        "",
        "| # | Layer | Signal | Confidence | Report |",
        "|---:|---|---:|---:|---|",
    ]
    for index, row in enumerate(rows, 1):
        report = str(row.get("report", ""))
        report_link = f"[{report}]({run_id}/{report})" if report else "-"
        lines.append(
            f"| {index} | {row.get('layer', 'n/a')} | {row.get('signal', 'n/a')} | "
            f"{row.get('confidence', '-')} | {report_link} |"
        )

    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| Date | Run | Mode | Dimensions | Decision | Confidence | Summary |",
            "|---|---|---|---:|---:|---:|---|",
            f"| {run_id.split('-full')[0]} | `{run_id}` | full | {len(rows)} | "
            f"{decision.get('action', 'n/a')} | {decision.get('confidence', 'n/a')} | "
            f"[00-summary.md]({run_id}/00-summary.md) |",
            "",
            "## File Map",
            f"- [Full Summary]({run_id}/00-summary.md)",
            f"- [Portfolio Decision]({run_id}/11-portfolio-decision.md)",
            f"- [Raw Data]({run_id}/raw/)",
            "- [_state.json](_state.json)",
            "",
            "## Watch Triggers",
        ]
    )
    lines.extend(f"- {trigger}" for trigger in watch_triggers)
    lines.extend(
        [
            "",
            "## Notes",
            f"- 以后本目录作为{stock_name}研究入口，入口文件固定为 `{filename}`。",
            "- Full run 必须包含 expanded migrated layers；仅 11 层 core spine 不是完整迁移运行。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def assess_non_iwc_substitutes(outputs: Mapping[str, Any]) -> dict[str, Any]:
    """Assess whether non-iWencai hoxit routes can improve tos-funder evidence."""
    reports = outputs.get("reports-eastmoney") or []
    news = outputs.get("news-stock") or []
    filings = outputs.get("filings-cninfo") or []
    concept = outputs.get("signals-concept") or {}
    industry = outputs.get("signals-industry") or {}
    dragon_tiger = outputs.get("signals-dragon-tiger") or {}
    fund_flow = outputs.get("signal-fund-flow") or outputs.get("signals-fund-flow") or []
    f10 = outputs.get("fundamentals-f10") or {}

    forward_reports = [
        row for row in reports
        if isinstance(row, Mapping)
        and any(row.get(key) not in (None, "") for key in (
            "predictThisYearEps",
            "predictNextYearEps",
            "predictThisYearPe",
            "predictNextYearPe",
        ))
    ]
    boards = concept.get("boards", []) if isinstance(concept, Mapping) else []
    industry_top = industry.get("top", []) if isinstance(industry, Mapping) else []
    dragon_records = dragon_tiger.get("records", []) if isinstance(dragon_tiger, Mapping) else []

    replacements = {
        "forward_valuation": {
            "status": "improved" if forward_reports else "missing",
            "source": "hoxit reports eastmoney",
            "evidence_count": len(forward_reports),
            "reason": "Eastmoney reports expose forward EPS/PE fields" if forward_reports else "No forward EPS/PE found",
        },
        "news_sentiment": {
            "status": "improved" if news else "missing",
            "source": "hoxit news stock",
            "evidence_count": len(news),
            "reason": "Eastmoney stock news provides external news headlines" if news else "No stock news returned",
        },
        "official_events": {
            "status": "improved" if filings else "missing",
            "source": "hoxit filings cninfo",
            "evidence_count": len(filings),
            "reason": "CNINFO filings provide official event facts" if filings else "No CNINFO filings returned",
        },
        "macro_sector_context": {
            "status": "improved" if boards or industry_top else "missing",
            "source": "hoxit signals concept + signals industry",
            "evidence_count": len(boards) + len(industry_top),
            "reason": "Concept and industry routes provide sector-relative context" if boards or industry_top else "No sector context returned",
        },
        "tactical_flow": {
            "status": "partial" if dragon_records else "missing",
            "source": "hoxit signals dragon-tiger / fund-flow",
            "evidence_count": len(dragon_records) + len(fund_flow),
            "reason": "Dragon-tiger/fund-flow evidence is stock-specific when non-empty",
        },
        "f10_profile": {
            "status": "unsupported" if isinstance(f10, Mapping) and f10.get("status") == "unsupported" else "improved" if f10 else "missing",
            "source": "hoxit fundamentals f10",
            "evidence_count": 0 if isinstance(f10, Mapping) and f10.get("status") == "unsupported" else int(bool(f10)),
            "reason": "Current mootdx client may not expose f10; use info/finance/filings/reports substitutes",
        },
    }

    improved = [name for name, item in replacements.items() if item["status"] == "improved"]
    partial_or_missing = [
        name for name, item in replacements.items()
        if item["status"] in {"partial", "missing", "unsupported"}
    ]
    return {
        "summary": {
            "improved_dimensions": improved,
            "still_weak_dimensions": partial_or_missing,
            "non_iwc_routes_helpful": bool(improved),
        },
        "replacements": replacements,
    }
