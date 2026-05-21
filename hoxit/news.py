from __future__ import annotations

import json
import re
import uuid
from typing import Callable

from .utils import normalize_code

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "")


def stock_news(code: str, page_size: int = 20, http_get: Callable | None = None, ak_module=None) -> list[dict]:
    code = normalize_code(code)
    callback = "jQuery_news"
    inner_params = json.dumps(
        {
            "uid": "",
            "keyword": code,
            "type": ["cmsArticleWebOld"],
            "client": "web",
            "clientType": "web",
            "clientVersion": "curr",
            "param": {
                "cmsArticleWebOld": {
                    "searchScope": "default",
                    "sort": "default",
                    "pageIndex": 1,
                    "pageSize": page_size,
                    "preTag": "",
                    "postTag": "",
                }
            },
        },
        separators=(",", ":"),
    )
    response = (http_get or _requests_get)(
        "https://search-api-web.eastmoney.com/search/jsonp",
        params={"cb": callback, "param": inner_params},
        headers={"User-Agent": UA, "Referer": "https://so.eastmoney.com/"},
        timeout=15,
    )
    text = response.text
    json_text = text[text.index("(") + 1 : text.rindex(")")]
    data = json.loads(json_text)
    rows = []
    for item in data.get("result", {}).get("cmsArticleWebOld", {}).get("list", []) or []:
        rows.append({
            "title": _strip_html(item.get("title", "")),
            "content": _strip_html(item.get("content", ""))[:200],
            "time": item.get("date", ""),
            "source": item.get("mediaName", ""),
            "url": item.get("url", ""),
        })
    return rows


def cls_flash(page_size: int = 50, http_get: Callable | None = None, ak_module=None) -> list[dict]:
    response = (http_get or _requests_get)(
        "https://www.cls.cn/nodeapi/telegraphList",
        params={"rn": str(page_size), "page": "1"},
        headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"},
        timeout=10,
    )
    data = response.json()
    rows = []
    for item in data.get("data", {}).get("roll_data", []) or []:
        rows.append({
            "title": item.get("title", "") or item.get("brief", ""),
            "content": item.get("content", "") or item.get("brief", ""),
            "time": item.get("ctime", ""),
        })
    return rows


def global_news(page_size: int = 50, http_get: Callable | None = None, ak_module=None) -> list[dict]:
    response = (http_get or _requests_get)(
        "https://np-weblist.eastmoney.com/comm/web/getFastNewsList",
        params={
            "client": "web",
            "biz": "web_724",
            "fastColumn": "102",
            "sortEnd": "",
            "pageSize": str(page_size),
            "req_trace": str(uuid.uuid4()),
        },
        headers={"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"},
        timeout=10,
    )
    data = response.json()
    rows = []
    for item in data.get("data", {}).get("fastNewsList", []) or []:
        rows.append({
            "title": item.get("title", ""),
            "summary": (item.get("summary", "") or "")[:200],
            "time": item.get("showTime", ""),
        })
    return rows
