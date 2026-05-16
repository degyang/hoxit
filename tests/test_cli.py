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
    bars = parser.parse_args(["market", "bars", "688017", "--category", "7", "--offset", "20"])
    assert bars.action == "bars"
    assert bars.category == 7
    assert bars.offset == 20
    transactions = parser.parse_args(["market", "transactions", "688017", "--date", "20260512"])
    assert transactions.action == "transactions"
    assert transactions.date == "20260512"


def test_cli_signals_hot_supports_exclude_st():
    parser = build_parser()
    args = parser.parse_args(["signals", "hot", "--date", "2026-05-12", "--exclude-st"])
    assert args.layer == "signals"
    assert args.action == "hot"
    assert args.exclude_st is True


def test_print_csv_flattens_quote_mapping(capsys):
    _print_csv({
        "688017": {"source": "mootdx", "code": "688017", "price": 1.23, "raw": {"ignored": True}},
        "300476": {"source": "mootdx", "code": "300476", "price": 4.56},
    })
    output = capsys.readouterr().out
    assert output.splitlines()[0] == "source,code,price"
    assert "mootdx,688017,1.23" in output
    assert "ignored" not in output
