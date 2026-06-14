from __future__ import annotations

import json

import pytest

from hoxit.tos_funder import (
    CORE_SPINE_LAYERS,
    EXPANDED_MIGRATED_LAYERS,
    assess_non_iwc_substitutes,
    annualized_volatility,
    complete_full_run_layers,
    expected_full_run_reports,
    full_run_status,
    sample_stdev,
    validate_full_run_manifest,
    write_stock_index,
)


def test_sample_stdev_uses_plain_float_math():
    assert sample_stdev([0.01, -0.02, 0.03]) == pytest.approx(0.025166, rel=1e-4)
    assert sample_stdev([0.01]) is None
    assert annualized_volatility([0.01, -0.02, 0.03]) == pytest.approx(0.3995, rel=1e-3)


def test_full_run_layers_include_expanded_migration_dimensions():
    layers = complete_full_run_layers()

    assert layers[: len(CORE_SPINE_LAYERS)] == CORE_SPINE_LAYERS
    assert layers[-len(EXPANDED_MIGRATED_LAYERS) :] == EXPANDED_MIGRATED_LAYERS
    assert len(layers) == 22
    assert "quant-price-series" in layers
    assert "value-munger" in layers
    assert "quant-valuation-damodaran" in layers
    assert "news-sentiment" in layers


def test_full_run_status_distinguishes_core_spine_from_complete():
    assert full_run_status(CORE_SPINE_LAYERS) == "core_spine_only"
    assert full_run_status(["price-series", "value-buffett"]) == "partial_full"
    assert full_run_status(["price-series", *CORE_SPINE_LAYERS[1:]]) == "core_spine_only"
    assert full_run_status(complete_full_run_layers()) == "complete"


def test_validate_full_run_manifest_requires_layers_and_reports():
    complete_manifest = {
        "commands_completed": complete_full_run_layers(),
        "reports_written": expected_full_run_reports(),
        "expanded_signal_count": 22,
    }
    assert validate_full_run_manifest(complete_manifest) == {
        "status": "complete",
        "complete": True,
        "missing_layers": [],
        "missing_reports": [],
        "expanded_signal_count": 22,
    }

    core_manifest = {
        "commands_completed": CORE_SPINE_LAYERS,
        "reports_written": expected_full_run_reports()[:12],
        "expanded_signal_count": 11,
    }
    result = validate_full_run_manifest(core_manifest)
    assert result["status"] == "core_spine_only"
    assert result["complete"] is False
    assert "value-munger" in result["missing_layers"]
    assert "12-value-munger.md" in result["missing_reports"]


def test_write_stock_index_uses_requested_stock_entry_filename(tmp_path):
    path = write_stock_index(
        tmp_path / "_index",
        stock_name="宁波银行",
        stock_code="002142",
        run_id="2026-06-10-full",
        decision={"action": "hold", "confidence": 73},
        signal_rows=[
            {"layer": "Buffett", "signal": "bullish", "confidence": 80, "report": "01-value-buffett.md"},
            {"layer": "Munger", "signal": "bullish", "confidence": 72, "report": "12-value-munger.md"},
        ],
        watch_triggers=["净息差企稳"],
    )

    assert path.name == "宁波银行.md"
    text = path.read_text(encoding="utf-8")
    assert "Expanded dimensions: **2**" in text
    assert "[12-value-munger.md](2026-06-10-full/12-value-munger.md)" in text
    assert "仅 11 层 core spine 不是完整迁移运行" in text


def test_assess_non_iwc_substitutes_identifies_better_routes():
    result = assess_non_iwc_substitutes({
        "reports-eastmoney": [{"predictNextYearEps": "5.65", "predictNextYearPe": "5.93"}],
        "news-stock": [{"title": "资金流入银行股"}],
        "filings-cninfo": [{"title": "行长任职资格获核准"}],
        "signals-concept": {"boards": [{"name": "银行"}]},
        "signals-industry": {"top": [{"name": "城商行"}]},
        "signals-dragon-tiger": {"records": []},
        "signal-fund-flow": [],
        "fundamentals-f10": {"status": "unsupported"},
    })

    assert result["summary"]["non_iwc_routes_helpful"] is True
    assert result["replacements"]["forward_valuation"]["status"] == "improved"
    assert result["replacements"]["news_sentiment"]["source"] == "hoxit news stock"
    assert result["replacements"]["f10_profile"]["status"] == "unsupported"
    assert "tactical_flow" in result["summary"]["still_weak_dimensions"]
