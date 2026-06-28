from __future__ import annotations

from hoxit import market
from hoxit.market import mootdx_bars, mootdx_quote, mootdx_transactions, parse_tencent_response, tdx_client


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
    def __init__(self):
        self.last_bars_kwargs = None

    def quotes(self, symbol):
        return FakeFrame([
            {"code": symbol[0], "name": "绿的谐波", "price": 1.23, "open": 1.0, "high": 1.4, "low": 0.9}
        ])

    def bars(self, **kwargs):
        self.last_bars_kwargs = kwargs
        symbol = kwargs["symbol"]
        frequency = kwargs["frequency"]
        offset = kwargs["offset"]
        return FakeFrame([{"code": symbol, "frequency": frequency, "offset": offset, "close": 1.2}])

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
    assert mootdx_bars("688017", frequency=9, offset=2, client=client) == [{"code": "688017", "frequency": 9, "offset": 2, "close": 1.2}]
    assert mootdx_transactions("688017", date="20260512", client=client) == [{"code": "688017", "date": "20260512", "price": 1.2}]


def test_tdx_client_uses_first_reachable_explicit_server(monkeypatch):
    calls = []

    class FakeQuotes:
        @staticmethod
        def factory(**kwargs):
            calls.append(kwargs)
            return {"client": kwargs}

    monkeypatch.setattr(market, "_TDX_SERVERS", [("1.1.1.1", 7709), ("2.2.2.2", 7709)])
    monkeypatch.setattr(market, "_probe_tdx_server", lambda ip, port: ip == "2.2.2.2")

    result = tdx_client(quotes_factory=FakeQuotes.factory)

    assert result == {"client": {"market": "std", "server": ("2.2.2.2", 7709)}}
    assert calls == [{"market": "std", "server": ("2.2.2.2", 7709)}]


def test_tdx_client_falls_back_to_bestip_then_plain_factory(monkeypatch):
    calls = []

    def fake_factory(**kwargs):
        calls.append(kwargs)
        if kwargs.get("bestip"):
            raise ValueError("bestip empty")
        return {"client": kwargs}

    monkeypatch.setattr(market, "_TDX_SERVERS", [("1.1.1.1", 7709)])
    monkeypatch.setattr(market, "_probe_tdx_server", lambda ip, port: False)

    result = tdx_client(quotes_factory=fake_factory)

    assert result == {"client": {"market": "std"}}
    assert calls == [{"market": "std", "bestip": True}, {"market": "std"}]


def test_mootdx_market_helpers_use_shared_tdx_client(monkeypatch):
    client = FakeMootdxClient()
    calls = []

    def fake_tdx_client():
        calls.append("tdx_client")
        return client

    monkeypatch.setattr(market, "tdx_client", fake_tdx_client)

    assert mootdx_quote(["688017"], fallback=None)["688017"]["source"] == "mootdx"
    assert mootdx_bars("688017", frequency=9, offset=2) == [{"code": "688017", "frequency": 9, "offset": 2, "close": 1.2}]
    assert mootdx_transactions("688017", date="20260512") == [{"code": "688017", "date": "20260512", "price": 1.2}]
    assert calls == ["tdx_client", "tdx_client", "tdx_client"]
