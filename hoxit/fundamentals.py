from __future__ import annotations

from .utils import normalize_code


def individual_info(code: str, ak_module=None):
    ak = ak_module
    if ak is None:
        import akshare as ak
    return ak.stock_individual_info_em(symbol=normalize_code(code)).to_dict("records")


def finance_snapshot(code: str, client=None):
    code = normalize_code(code)
    if client is None:
        from mootdx.quotes import Quotes

        client = Quotes.factory(market="std")
    return client.finance(symbol=code)


def f10(code: str, client=None):
    code = normalize_code(code)
    if client is None:
        from mootdx.quotes import Quotes

        client = Quotes.factory(market="std")
    return client.f10(symbol=code)
