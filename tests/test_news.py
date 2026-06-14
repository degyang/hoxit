from __future__ import annotations

from hoxit import news

from conftest import JsonResponse, TextResponse


def test_stock_news_parses_eastmoney_jsonp():
    text = 'jQuery_news({"result":{"cmsArticleWebOld":{"list":[{"title":"<em>标题</em>","content":"<p>正文</p>","date":"2026-05-12","mediaName":"东财","url":"https://example.test"}]}}})'
    rows = news.stock_news("688017", http_get=lambda *args, **kwargs: TextResponse(text))
    assert rows == [{"title": "标题", "content": "正文", "time": "2026-05-12", "source": "东财", "url": "https://example.test"}]


def test_cls_flash_uses_signed_cls_endpoint():
    calls = []
    payload = {"data": {"roll_data": [{"title": "", "brief": "快讯", "content": "内容", "ctime": "2026-05-12 09:30:00"}]}}

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return JsonResponse(payload)

    rows = news.cls_flash(http_get=fake_get)
    assert calls[0][0] == "https://www.cls.cn/v1/roll/get_roll_list"
    assert calls[0][1]["params"]["app"] == "CailianpressWeb"
    assert calls[0][1]["params"]["sign"]
    assert rows == [{"title": "快讯", "content": "内容", "time": "2026-05-12 09:30:00"}]


def test_global_news_adds_req_trace():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({"data": {"fastNewsList": [{"title": "全球资讯", "summary": "摘要", "showTime": "2026-05-12"}]}})

    rows = news.global_news(http_get=fake_get)
    assert "req_trace" in calls[0]["params"]
    assert rows[0]["title"] == "全球资讯"
