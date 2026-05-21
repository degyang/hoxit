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
