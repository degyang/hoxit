from __future__ import annotations

import os

import pytest

from hoxit import filings, fundamentals, news, signals

pytestmark = pytest.mark.integration


def live_enabled() -> bool:
    return os.getenv("HOXIT_LIVE_TESTS") == "1"


@pytest.mark.skipif(not live_enabled(), reason="set HOXIT_LIVE_TESTS=1 to hit external services")
def test_live_eastmoney_push2_fundamentals_and_industry():
    info = fundamentals.individual_info("600519")
    assert info["code"] == "600519"
    assert info["name"]

    industries = signals.industry_comparison(5)
    assert industries["total"] > 0
    assert industries["top"][0]["name"]


@pytest.mark.skipif(not live_enabled(), reason="set HOXIT_LIVE_TESTS=1 to hit external services")
def test_live_eastmoney_fund_flow_and_datacenter():
    fund_flow = signals.stock_fund_flow_120d("600519", days=5)
    assert fund_flow
    assert {"date", "main_net", "super_net"} <= set(fund_flow[-1])

    lockup = signals.lockup_expiry("600519", "2026-05-21", forward_days=90)
    assert {"history", "upcoming"} <= set(lockup)


@pytest.mark.skipif(not live_enabled(), reason="set HOXIT_LIVE_TESTS=1 to hit external services")
def test_live_news_and_cninfo_endpoints():
    cls_rows = news.cls_flash(page_size=3)
    assert cls_rows
    assert cls_rows[0]["title"] or cls_rows[0]["content"]

    global_rows = news.global_news(page_size=3)
    assert global_rows
    assert global_rows[0]["title"]

    announcements = filings.cninfo_reports("600519", "20260101", "20260521", page_size=3)
    assert announcements
    assert announcements[0]["title"]
