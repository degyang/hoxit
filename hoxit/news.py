from __future__ import annotations

import json
import re
import time
import uuid
import hashlib
from typing import Callable

from .utils import em_get, normalize_code

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "")


def _cls_param_string(params: dict) -> str:
    def convert(key: str, value) -> str:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return f"{key}={value}"
        if isinstance(value, list):
            if not value:
                return f"{key}[]"
            return "&".join(filter(None, (convert(f"{key}[{index}]", item) for index, item in enumerate(value))))
        if isinstance(value, dict):
            return "&".join(
                filter(None, (convert(f"{key}[{child}]", value[child]) for child in sorted(value, key=lambda item: str(item).upper())))
            )
        return str(value)

    return "&".join(
        filter(None, (convert(key, params[key]) for key in sorted(params, key=lambda item: str(item).upper())))
    )


def _cls_sign(params: dict) -> str:
    param_string = _cls_param_string(params)
    sha1_value = hashlib.sha1(param_string.encode()).hexdigest()
    return hashlib.md5(sha1_value.encode()).hexdigest()


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
    response = (http_get or em_get)(
        "https://search-api-web.eastmoney.com/search/jsonp",
        params={"cb": callback, "param": inner_params},
        headers={"Referer": "https://so.eastmoney.com/"},
        timeout=15,
    )
    text = response.text
    json_text = text[text.index("(") + 1 : text.rindex(")")]
    data = json.loads(json_text)
    rows = []
    raw_list = data.get("result", {}).get("cmsArticleWebOld") or []
    if isinstance(raw_list, dict):
        raw_list = raw_list.get("list") or []
    for item in raw_list:
        rows.append({
            "title": _strip_html(item.get("title", "")),
            "content": _strip_html(item.get("content", ""))[:200],
            "time": item.get("date", ""),
            "source": item.get("mediaName", ""),
            "url": item.get("url", ""),
        })
    return rows


def cls_flash(page_size: int = 50, http_get: Callable | None = None, ak_module=None) -> list[dict]:
    """
    财联社快讯（全市场实时快讯）。

    参考项目中旧版 nodeapi/telegraphList 已下线（#14）。新版网页使用带 sign 的
    /v1/roll/get_roll_list；sign 由前端静态算法生成，无需用户申请 key。
    """

    params = {
        "refresh_type": "1",
        "rn": str(page_size),
        "last_time": str(int(time.time())),
        "os": "web",
        "sv": "8.7.9",
        "app": "CailianpressWeb",
    }
    params["sign"] = _cls_sign(params)
    try:
        response = (http_get or _requests_get)(
            "https://www.cls.cn/v1/roll/get_roll_list",
            params=params,
            headers={"User-Agent": UA, "Referer": "https://www.cls.cn/telegraph"},
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
    except Exception:
        return []


def global_news(page_size: int = 50, http_get: Callable | None = None, ak_module=None) -> list[dict]:
    response = (http_get or em_get)(
        "https://np-weblist.eastmoney.com/comm/web/getFastNewsList",
        params={
            "client": "web",
            "biz": "web_724",
            "fastColumn": "102",
            "sortEnd": "",
            "pageSize": str(page_size),
            "req_trace": str(uuid.uuid4()),
        },
        headers={"Referer": "https://kuaixun.eastmoney.com/"},
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
