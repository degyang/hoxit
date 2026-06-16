from __future__ import annotations

from hoxit import fundamentals

from conftest import JsonResponse


def test_individual_info_uses_eastmoney_push2():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({
            "data": {
                "f57": "688017",
                "f58": "绿的谐波",
                "f84": 100,
                "f85": 80,
                "f127": "机器人",
                "f116": 1000,
                "f117": 800,
                "f189": 20200828,
                "f43": 123.45,
            }
        })

    result = fundamentals.individual_info("688017", http_get=fake_get)
    assert calls[0]["params"]["secid"] == "1.688017"
    assert result["industry"] == "机器人"
    assert result["list_date"] == "20200828"


def test_f10_degrades_when_client_has_no_f10_method():
    class NoF10Client:
        pass

    result = fundamentals.f10("002142", client=NoF10Client())

    assert result["code"] == "002142"
    assert result["status"] == "unsupported"
    assert result["sections"] == {}
    assert "filings cninfo" in result["warnings"][0]


def test_f10_uses_client_method_when_available():
    class F10Client:
        def f10(self, symbol):
            return {"symbol": symbol, "sections": {"股东研究": "..."}, "status": "ok"}

    assert fundamentals.f10("002142", client=F10Client()) == {
        "symbol": "002142",
        "sections": {"股东研究": "..."},
        "status": "ok",
    }


# ── governance_summary ──────────────────────────────────────────


def test_governance_summary_returns_computed_on_valid_data():
    """治理摘要应正确解析 iwencai management route 返回的数据。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [{
                "股票代码": "600519.SH",
                "实际控制人": "贵州省国资委",
                "股权质押比例": 15.5,
                "股东名称": "贵州茅台集团",
                "变动方向": "增持",
                "变动股数": 100000,
                "高管持股比例": 0.05,
            }]
        })

    result = fundamentals.governance_summary("600519", http_post=fake_post)
    assert result["status"] == "computed"
    assert result["code"] == "600519.SH"
    assert result["actual_controller"] == "贵州省国资委"
    assert result["pledge_ratio"] == 15.5
    assert result["executive_holding"] == 0.05
    assert len(result["shareholder_changes"]) == 1
    assert result["shareholder_changes"][0]["name"] == "贵州茅台集团"
    assert result["shareholder_changes"][0]["type"] == "增持"
    assert result["warnings"] == []


def test_governance_summary_returns_data_needed_on_empty_rows():
    """治理摘要在 iwencai 返回空数据时应返回 data_needed 状态。"""
    def fake_post(url, **kwargs):
        return JsonResponse({"datas": []})

    result = fundamentals.governance_summary("600519", http_post=fake_post)
    assert result["status"] == "data_needed"
    assert result["actual_controller"] == ""
    assert result["pledge_ratio"] is None
    assert result["shareholder_changes"] == []
    assert result["executive_holding"] is None
    assert len(result["warnings"]) > 0


def test_governance_summary_handles_network_error():
    """治理摘要在网络异常时应返回 data_needed 而非抛出异常。"""
    def failing_post(url, **kwargs):
        raise RuntimeError("network error")

    result = fundamentals.governance_summary("600519", http_post=failing_post)
    assert result["status"] == "data_needed"
    assert result["code"] == "600519"


def test_governance_summary_normalizes_code():
    """治理摘要应正确处理带后缀的股票代码。"""
    calls = []

    def fake_post(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({"datas": []})

    fundamentals.governance_summary("600519.SH", http_post=fake_post)
    assert "600519" in calls[0]["json"]["query"]


# ── business_summary ────────────────────────────────────────────


def test_business_summary_returns_computed_on_valid_data():
    """经营摘要应正确解析 iwencai business route 返回的数据。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [{
                "股票代码": "600519.SH",
                "主营业务收入构成": [
                    {"name": "茅台酒", "revenue": 1000000, "ratio": 0.85},
                    {"name": "系列酒", "revenue": 200000, "ratio": 0.15},
                ],
                "前五大客户销售占比": 12.5,
                "前五大供应商采购占比": 8.3,
                "客户名称": ["经销商A", "经销商B", "经销商C"],
            }]
        })

    result = fundamentals.business_summary("600519", http_post=fake_post)
    assert result["status"] == "computed"
    assert result["code"] == "600519.SH"
    assert len(result["revenue_segments"]) == 2
    assert result["revenue_segments"][0]["name"] == "茅台酒"
    assert result["customer_concentration"] == 12.5
    assert result["supplier_concentration"] == 8.3
    assert len(result["top_customers"]) > 0
    assert result["warnings"] == []


def test_business_summary_returns_data_needed_on_empty_rows():
    """经营摘要在 iwencai 返回空数据时应返回 data_needed 状态。"""
    def fake_post(url, **kwargs):
        return JsonResponse({"datas": []})

    result = fundamentals.business_summary("600519", http_post=fake_post)
    assert result["status"] == "data_needed"
    assert result["revenue_segments"] == []
    assert result["customer_concentration"] is None
    assert result["supplier_concentration"] is None
    assert result["top_customers"] == []
    assert len(result["warnings"]) > 0


def test_business_summary_handles_network_error():
    """经营摘要在网络异常时应返回 data_needed 而非抛出异常。"""
    def failing_post(url, **kwargs):
        raise RuntimeError("network error")

    result = fundamentals.business_summary("600519", http_post=failing_post)
    assert result["status"] == "data_needed"
    assert result["code"] == "600519"


def test_business_summary_handles_string_revenue_segment():
    """经营摘要应能处理字符串形式的收入构成。"""
    def fake_post(url, **kwargs):
        return JsonResponse({
            "datas": [{
                "股票代码": "600519.SH",
                "主营业务收入构成": "白酒酿造",
                "前五大客户销售占比": 10.0,
            }]
        })

    result = fundamentals.business_summary("600519", http_post=fake_post)
    assert result["status"] == "computed"
    assert len(result["revenue_segments"]) == 1
    assert result["revenue_segments"][0]["name"] == "白酒酿造"
