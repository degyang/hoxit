from __future__ import annotations

from .utils import get_cninfo_market, normalize_code


def cninfo_reports(code: str, start_date: str, end_date: str, ak_module=None):
    ak = ak_module
    if ak is None:
        import akshare as ak
    code = normalize_code(code)
    return ak.stock_zh_a_disclosure_report_cninfo(
        symbol=code,
        market=get_cninfo_market(code),
        start_date=start_date,
        end_date=end_date,
    ).to_dict("records")
