from __future__ import annotations

from .utils import normalize_code


def stock_news(code: str, ak_module=None):
    ak = ak_module
    if ak is None:
        import akshare as ak
    return ak.stock_news_em(symbol=normalize_code(code)).to_dict("records")


def cls_flash(ak_module=None):
    ak = ak_module
    if ak is None:
        import akshare as ak
    return ak.stock_info_global_cls().to_dict("records")


def global_news(ak_module=None):
    ak = ak_module
    if ak is None:
        import akshare as ak
    return ak.stock_info_global_em().to_dict("records")
