from __future__ import annotations

from typing import Callable

from . import iwencai
from .utils import get_cninfo_org_id, normalize_code

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _requests_post(url: str, **kwargs):
    import requests

    return requests.post(url, **kwargs)


def _cninfo_date(value: str) -> str:
    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:]}"
    return value


def cninfo_reports(
    code: str,
    start_date: str,
    end_date: str,
    page_size: int = 30,
    http_post: Callable | None = None,
    ak_module=None,
) -> list[dict]:
    code = normalize_code(code)
    payload = {
        "stock": f"{code},{get_cninfo_org_id(code)}",
        "tabName": "fulltext",
        "pageSize": str(page_size),
        "pageNum": "1",
        "column": "",
        "category": "",
        "plate": "",
        "seDate": f"{_cninfo_date(start_date)}~{_cninfo_date(end_date)}",
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    response = (http_post or _requests_post)(
        "https://www.cninfo.com.cn/new/hisAnnouncement/query",
        data=payload,
        headers={
            "User-Agent": UA,
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://www.cninfo.com.cn/new/disclosure",
            "Origin": "https://www.cninfo.com.cn",
        },
        timeout=15,
    )
    data = response.json()
    rows = []
    for item in data.get("announcements", []) or []:
        rows.append({
            "title": item.get("announcementTitle", ""),
            "type": item.get("announcementTypeName", ""),
            "date": item.get("announcementTime", ""),
            "url": f"https://www.cninfo.com.cn/new/disclosure/detail?annoId={item.get('announcementId', '')}",
        })
    if rows:
        return rows

    try:
        fallback_rows = iwencai.search_rows("announcement", f"{code} 公告 分红", api_key=None)
    except Exception:
        fallback_rows = []
    mapped = []
    for item in fallback_rows:
        mapped.append({
            "title": item.get("title", ""),
            "type": item.get("type", "") or "公告",
            "date": item.get("publish_date", ""),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
        })
    return mapped
