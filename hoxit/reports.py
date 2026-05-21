from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

from . import iwencai
from .utils import normalize_code, sanitize_filename

REPORT_API = "https://reportapi.eastmoney.com/report/list"
PDF_TPL = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def _requests_get(url: str, **kwargs):
    import requests

    return requests.get(url, **kwargs)


def _requests_post(url: str, **kwargs):
    import requests

    return requests.post(url, **kwargs)


def eastmoney_reports(
    code: str,
    max_pages: int = 5,
    http_get: Callable | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> list[dict]:
    code = normalize_code(code)
    get = http_get or _requests_get
    records: list[dict] = []
    headers = {"User-Agent": UA, "Referer": "https://data.eastmoney.com/"}
    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*",
            "pageSize": "100",
            "industry": "*",
            "rating": "*",
            "ratingChange": "*",
            "beginTime": "2000-01-01",
            "endTime": "2030-01-01",
            "pageNo": str(page),
            "fields": "",
            "qType": "0",
            "orgCode": "",
            "code": code,
            "rcode": "",
            "p": str(page),
            "pageNum": str(page),
            "pageNumber": str(page),
        }
        response = get(REPORT_API, params=params, headers=headers, timeout=30)
        data = response.json()
        rows = data.get("data") or []
        if not rows:
            break
        records.extend(rows)
        if page >= (data.get("TotalPage", 1) or 1):
            break
        sleep(0.3)
    return records


def download_pdf(record: dict, target_dir: str = "./reports", http_get: Callable | None = None) -> str | None:
    info_code = record.get("infoCode", "")
    if not info_code:
        return None
    date = (record.get("publishDate") or "")[:10]
    org = sanitize_filename(record.get("orgSName") or "未知", 40)
    title = sanitize_filename(record.get("title") or "", 80)
    target = Path(target_dir) / f"{date}_{org}_{title}.pdf"
    if target.exists():
        return str(target)
    get = http_get or _requests_get
    response = get(
        PDF_TPL.format(info_code=info_code),
        headers={"User-Agent": UA, "Referer": "https://data.eastmoney.com/"},
        timeout=60,
    )
    if getattr(response, "status_code", None) == 200 and len(response.content) >= 1024:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        return str(target)
    return None


def iwencai_search(
    query: str,
    channel: str = "report",
    size: int = 50,
    base_url: str | None = None,
    api_key: str | None = None,
    call_type: str = "normal",
    timeout: int = iwencai.DEFAULT_TIMEOUT,
    http_post: Callable | None = None,
) -> list[dict]:
    route = channel if channel in {"announcement", "report"} else "report"
    response = iwencai.comprehensive_search(
        route=route,
        query=query,
        payload_extra={"size": size},
        api_key=api_key,
        call_type=call_type,
        timeout=timeout,
        base_url=base_url or os.environ.get("IWENCAI_BASE_URL", "https://openapi.iwencai.com"),
        http_post=http_post or _requests_post,
    )
    if isinstance(response, dict):
        if response.get("status_code", 0) != 0:
            raise RuntimeError(f"iwencai error: {response.get('status_msg', '')}")
        return response.get("data") or []
    return []


def dedup_articles(articles: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for article in articles:
        uid = article.get("uid", "") or f"{article.get('title', '')}|{article.get('publish_date', '')}"
        score = float(article.get("score", 0) or 0)
        if uid not in best or score > float(best[uid].get("score", 0) or 0):
            best[uid] = article
    return sorted(best.values(), key=lambda item: item.get("publish_date", ""), reverse=True)
