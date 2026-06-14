from __future__ import annotations

import pytest

from hoxit.utils import get_cninfo_market, get_cninfo_org_id, get_prefix, iter_dates, normalize_code, sanitize_filename


def test_normalize_code_variants():
    assert normalize_code("SH688017") == "688017"
    assert normalize_code("688017.SH") == "688017"
    assert normalize_code("bj832000") == "832000"


def test_market_prefix_and_cninfo_market():
    assert get_prefix("688017") == "sh"
    assert get_prefix("832000") == "bj"
    assert get_prefix("000001") == "sz"
    assert get_cninfo_market("000001") == "深市"


def test_cninfo_org_id_uses_dynamic_lookup():
    """巨潮 orgId 优先动态查 szse_stock.json 映射表，查不到 fallback 硬编码。"""
    # 600519 不在映射表中 → 硬编码 fallback
    assert get_cninfo_org_id("600519") == "gssh0600519"
    # 688017/832000 在映射表中 → 返回真实 orgId（v3.2.2 修复 #19）
    assert get_cninfo_org_id("688017") == "9900041602"
    assert get_cninfo_org_id("832000") == "gfbj0832000"
    # 000001 不在映射表中 → 硬编码 fallback
    assert get_cninfo_org_id("000001") == "gssz0000001"


def test_iter_dates_inclusive():
    assert list(iter_dates("2026-05-12", "2026-05-14")) == ["2026-05-12", "2026-05-13", "2026-05-14"]


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        normalize_code("ABC")


def test_sanitize_filename():
    assert sanitize_filename('a/b:c*?"<>|') == "a_b_c______"
