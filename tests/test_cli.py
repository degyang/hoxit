from __future__ import annotations

from hoxit.cli import _print_csv, build_parser


def test_cli_uses_hoxit_program_name_and_layer_subcommands():
    parser = build_parser()
    args = parser.parse_args(["market", "quote", "688017"])
    assert parser.prog == "hoxit"
    assert args.layer == "market"
    assert args.action == "quote"
    assert args.codes == ["688017"]
    assert args.format == "csv"


def test_cli_market_quote_can_request_json_format():
    parser = build_parser()
    args = parser.parse_args(["market", "quote", "688017", "--format", "json"])
    assert args.format == "json"


def test_cli_market_metrics_and_mootdx_subcommands():
    parser = build_parser()
    assert parser.parse_args(["market", "metrics", "688017"]).action == "metrics"
    bars = parser.parse_args(["market", "bars", "688017", "--frequency", "8", "--offset", "20"])
    assert bars.action == "bars"
    assert bars.frequency == 8
    assert bars.offset == 20
    assert parser.parse_args(["market", "bars", "688017"]).frequency == 9
    transactions = parser.parse_args(["market", "transactions", "688017", "--date", "20260512"])
    assert transactions.action == "transactions"
    assert transactions.date == "20260512"


def test_cli_reports_industry_subcommand_parse():
    parser = build_parser()
    args = parser.parse_args(["reports", "industry", "--industry-code", "1238", "--max-pages", "2"])
    assert args.layer == "reports"
    assert args.action == "industry"
    assert args.industry_code == "1238"
    assert args.max_pages == 2


def test_cli_signals_hot_supports_exclude_st():
    parser = build_parser()
    args = parser.parse_args(["signals", "hot", "--date", "2026-05-12", "--exclude-st"])
    assert args.layer == "signals"
    assert args.action == "hot"
    assert args.exclude_st is True


def test_cli_uzen_subcommands_parse():
    parser = build_parser()
    args = parser.parse_args(["uzen", "quick-scan", "600000", "--output-dir", "uzen-skills/reports"])
    assert args.layer == "uzen"
    assert args.action == "quick-scan"
    assert args.code == "600000"
    assert args.output_dir == "uzen-skills/reports"

    lhb = parser.parse_args(["uzen", "lhb-analyzer", "600000", "--trade-date", "2026-06-14"])
    assert lhb.trade_date == "2026-06-14"

    for action in ["analyze-stock", "dcf", "comps", "panel-only", "scan-trap"]:
        parsed = parser.parse_args(["uzen", action, "600000"])
        assert parsed.action == action


def test_cli_uzen_dispatch_calls_run_analysis(monkeypatch):
    from hoxit import cli, uzen

    calls = []

    def fake_run_analysis(code, **kwargs):
        calls.append((code, kwargs))
        return {"ok": True}

    monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)
    parser = cli.build_parser()
    args = parser.parse_args([
        "uzen",
        "lhb-analyzer",
        "600000",
        "--trade-date",
        "2026-06-14",
        "--output-dir",
        "tmp/reports",
    ])

    assert cli.run(args) == {"ok": True}
    assert calls == [
        (
            "600000",
            {
                "mode": "lhb-analyzer",
                "output_dir": "tmp/reports",
                "trade_date": "2026-06-14",
                "agent_analysis": None,
            },
        )
    ]


def test_print_csv_flattens_quote_mapping(capsys):
    _print_csv({
        "688017": {"source": "mootdx", "code": "688017", "price": 1.23, "raw": {"ignored": True}},
        "300476": {"source": "mootdx", "code": "300476", "price": 4.56},
    })
    output = capsys.readouterr().out
    assert output.splitlines()[0] == "source,code,price"
    assert "mootdx,688017,1.23" in output
    assert "ignored" not in output


def test_cli_uzen_agent_analysis_argument():
    """--agent-analysis should be parsed for all UZEN subcommands."""
    parser = build_parser()

    for action in ["analyze-stock", "quick-scan", "dcf", "comps", "panel-only", "scan-trap"]:
        args = parser.parse_args(["uzen", action, "600000", "--agent-analysis", "test.json"])
        assert args.agent_analysis == "test.json"

    lhb = parser.parse_args(["uzen", "lhb-analyzer", "600000", "--agent-analysis", "test.json"])
    assert lhb.agent_analysis == "test.json"


def test_cli_uzen_agent_analysis_default_none():
    """--agent-analysis should default to None."""
    parser = build_parser()
    args = parser.parse_args(["uzen", "quick-scan", "600000"])
    assert args.agent_analysis is None


def test_cli_uzen_dispatch_with_agent_analysis(monkeypatch, tmp_path):
    """CLI should pass agent_analysis to run_analysis when provided."""
    from hoxit import cli, uzen
    import json

    calls = []

    def fake_run_analysis(code, **kwargs):
        calls.append((code, kwargs))
        return {"ok": True}

    monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)

    # Create a temporary agent analysis file
    agent_file = tmp_path / "agent.json"
    agent_file.write_text(json.dumps({"thesis": "测试"}), encoding="utf-8")

    parser = cli.build_parser()
    args = parser.parse_args([
        "uzen",
        "quick-scan",
        "600000",
        "--agent-analysis",
        str(agent_file),
    ])

    assert cli.run(args) == {"ok": True}
    assert len(calls) == 1
    code, kwargs = calls[0]
    assert code == "600000"
    assert kwargs["agent_analysis"] is not None
    assert kwargs["agent_analysis"]["status"] == "provided"
    assert kwargs["agent_analysis"]["thesis"] == "测试"


def test_cli_uzen_dispatch_without_agent_analysis(monkeypatch):
    """CLI should pass agent_analysis=None when not provided."""
    from hoxit import cli, uzen

    calls = []

    def fake_run_analysis(code, **kwargs):
        calls.append((code, kwargs))
        return {"ok": True}

    monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)

    parser = cli.build_parser()
    args = parser.parse_args(["uzen", "quick-scan", "600000"])

    assert cli.run(args) == {"ok": True}
    assert len(calls) == 1
    code, kwargs = calls[0]
    assert code == "600000"
    assert kwargs["agent_analysis"] is None


def test_cli_uzen_agent_analysis_file_not_found(monkeypatch, tmp_path):
    """CLI should raise FileNotFoundError for missing agent analysis file."""
    from hoxit import cli, uzen

    def fake_run_analysis(code, **kwargs):
        return {"ok": True}

    monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)

    parser = cli.build_parser()
    args = parser.parse_args([
        "uzen",
        "quick-scan",
        "600000",
        "--agent-analysis",
        str(tmp_path / "nonexistent.json"),
    ])

    import pytest
    with pytest.raises(FileNotFoundError, match="Agent analysis file not found"):
        cli.run(args)


def test_cli_uzen_agent_analysis_invalid_json(monkeypatch, tmp_path):
    """CLI should raise ValueError for invalid JSON in agent analysis file."""
    from hoxit import cli, uzen

    def fake_run_analysis(code, **kwargs):
        return {"ok": True}

    monkeypatch.setattr(uzen, "run_analysis", fake_run_analysis)

    # Create a file with invalid JSON
    agent_file = tmp_path / "invalid.json"
    agent_file.write_text("not valid json", encoding="utf-8")

    parser = cli.build_parser()
    args = parser.parse_args([
        "uzen",
        "quick-scan",
        "600000",
        "--agent-analysis",
        str(agent_file),
    ])

    import pytest
    with pytest.raises(ValueError, match="Invalid JSON"):
        cli.run(args)
