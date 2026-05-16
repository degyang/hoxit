from __future__ import annotations

import math

from hoxit.valuation import calc_peg, forward_pe, full_valuation, pe_digestion
from conftest import FakeDataFrame


def test_valuation_pure_functions():
    assert forward_pe(100, 5) == 20
    assert math.isinf(forward_pe(100, 0))
    assert calc_peg(30, 0.3) == 1
    assert pe_digestion(30, 0.3) == 0


def test_full_valuation_with_forecast(forecast_df):
    result = full_valuation(
        "688017",
        quote_provider=lambda codes: {"688017": {"code": "688017", "name": "x", "price": 30.0}},
        forecast_provider=lambda code: forecast_df,
    )
    assert result["pe_fwd"] == 10.0
    assert result["cagr_pct"] == 50.0
    assert result["peg"] == 0.2
    assert result["analyst_count"] == 5


def test_full_valuation_handles_empty_forecast():
    result = full_valuation(
        "688017",
        quote_provider=lambda codes: {"688017": {"code": "688017", "name": "x", "price": 30.0}},
        forecast_provider=lambda code: FakeDataFrame(),
    )
    assert result["eps_cur"] is None
    assert result["pe_fwd"] is None
    assert result["analyst_count"] == 0
