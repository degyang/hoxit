from __future__ import annotations

from hoxit.market import mootdx_bars, mootdx_quote, mootdx_transactions, parse_tencent_response


def test_parse_tencent_response_uses_correct_pb_index(sample_quote_line):
    result = parse_tencent_response(sample_quote_line)
    quote = result["688017"]
    assert quote["name"] == "绿的谐波"
    assert quote["price"] == 305.50
    assert quote["pe_ttm"] == 409.55
    assert quote["amplitude_pct"] == 20.00
    assert quote["pb"] == 15.69


class FakeFrame:
    def __init__(self, rows):
        self.rows = rows

    def to_dict(self, orient):
        assert orient == "records"
        return self.rows


class FakeMootdxClient:
    def quotes(self, symbol):
        return FakeFrame([
            {"code": symbol[0], "name": "绿的谐波", "price": 1.23, "open": 1.0, "high": 1.4, "low": 0.9}
        ])

    def bars(self, symbol, category, offset):
        return FakeFrame([{"code": symbol, "category": category, "offset": offset, "close": 1.2}])

    def transaction(self, symbol, date):
        return FakeFrame([{"code": symbol, "date": date, "price": 1.2}])


def test_mootdx_quote_is_primary_source():
    result = mootdx_quote(["688017"], client=FakeMootdxClient(), fallback=lambda codes: {"should": "not call"})
    assert result["688017"]["source"] == "mootdx"
    assert result["688017"]["price"] == 1.23


def test_mootdx_quote_falls_back_to_tencent_when_mootdx_fails():
    class BrokenClient:
        def quotes(self, symbol):
            raise RuntimeError("mootdx unavailable")

    result = mootdx_quote(["688017"], client=BrokenClient(), fallback=lambda codes: {"688017": {"source": "tencent"}})
    assert result == {"688017": {"source": "tencent"}}


def test_mootdx_market_data_helpers():
    client = FakeMootdxClient()
    assert mootdx_bars("688017", category=4, offset=2, client=client) == [{"code": "688017", "category": 4, "offset": 2, "close": 1.2}]
    assert mootdx_transactions("688017", date="20260512", client=client) == [{"code": "688017", "date": "20260512", "price": 1.2}]
