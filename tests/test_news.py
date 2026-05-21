from __future__ import annotations

from hoxit import news

from conftest import JsonResponse, TextResponse


def test_stock_news_parses_eastmoney_jsonp():
    text = 'jQuery_news({"result":{"cmsArticleWebOld":{"list":[{"title":"<em>标题</em>","content":"<p>正文</p>","date":"2026-05-12","mediaName":"东财","url":"https://example.test"}]}}})'
    rows = news.stock_news("688017", http_get=lambda *args, **kwargs: TextResponse(text))
    assert rows == [{"title": "标题", "content": "正文", "time": "2026-05-12", "source": "东财", "url": "https://example.test"}]


def test_cls_flash_uses_direct_cls_endpoint():
    payload = {"data": {"roll_data": [{"title": "", "brief": "快讯", "content": "内容", "ctime": "2026-05-12 09:30:00"}]}}
    rows = news.cls_flash(http_get=lambda *args, **kwargs: JsonResponse(payload))
    assert rows == [{"title": "快讯", "content": "内容", "time": "2026-05-12 09:30:00"}]


def test_global_news_adds_req_trace():
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return JsonResponse({"data": {"fastNewsList": [{"title": "全球资讯", "summary": "摘要", "showTime": "2026-05-12"}]}})

    rows = news.global_news(http_get=fake_get)
    assert "req_trace" in calls[0]["params"]
    assert rows[0]["title"] == "全球资讯"
