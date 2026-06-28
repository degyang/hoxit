from __future__ import annotations

import random
import time
from datetime import datetime, timedelta
import re
from typing import Callable, Iterable


# ── 东财防封：全局节流 + 会话复用 ────────────────────────────────
# 所有 eastmoney.com 请求统一走 em_get()：串行限流（最小间隔 + 随机抖动）
# + 复用 Keep-Alive 会话，批量调用自动降速防封。

EM_MIN_INTERVAL = 1.0  # 东财请求最小间隔（秒）；批量任务建议调到 1.5~2.0

_em_session = None  # lazy-init
_em_last_call: list[float] = [0.0]


def _get_em_session():
    import requests

    global _em_session
    if _em_session is None:
        _em_session = requests.Session()
        _em_session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
        # 连接级自动重试：瞬态连接错误 / 429 / 5xx 指数退避重试（住宅 IP 偶发风控更稳）。
        # 注意：403 不重试（东财风控信号，重试无益反而加重；按 EM_MIN_INTERVAL 降频应对）。
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            _em_adapter = HTTPAdapter(max_retries=Retry(
                total=3, connect=3, backoff_factor=0.6,
                status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"]))
            _em_session.mount("https://", _em_adapter)
            _em_session.mount("http://", _em_adapter)
        except Exception:
            pass  # 老版本 urllib3 缺 allowed_methods 等参数时降级为无重试，不影响主流程
    return _em_session


def em_get(url: str, params: dict | None = None, headers: dict | None = None, timeout: int = 15, **kwargs) -> "requests.Response":
    """东财统一节流 GET — 串行限流 + 会话复用。

    所有 eastmoney.com 的 HTTP 请求都应使用此函数替代裸 requests.get，
    以避免触发东财的频率风控。
    """
    now = time.time()
    wait = EM_MIN_INTERVAL - (now - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))  # + 随机抖动 0.1~0.5s
    session = _get_em_session()
    merged = dict(session.headers)
    if headers:
        merged.update(headers)
    _em_last_call[0] = time.time()
    return session.get(url, params=params, headers=merged, timeout=timeout, **kwargs)


def em_post(url: str, data: dict | None = None, headers: dict | None = None, timeout: int = 15, **kwargs) -> "requests.Response":
    """东财统一节流 POST — 同 em_get，带限流 + 会话复用。"""
    now = time.time()
    wait = EM_MIN_INTERVAL - (now - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))
    session = _get_em_session()
    merged = dict(session.headers)
    if headers:
        merged.update(headers)
    _em_last_call[0] = time.time()
    return session.post(url, data=data, headers=merged, timeout=timeout, **kwargs)


# ── 工具函数 ──


def normalize_code(code: str) -> str:
    """Normalize SH688017, 688017.SH, bj832000, etc. to a six-digit code."""
    value = str(code).strip()
    value = re.sub(r"^(sh|sz|bj)", "", value, flags=re.IGNORECASE)
    value = re.sub(r"\.(sh|sz|bj)$", "", value, flags=re.IGNORECASE)
    if not re.fullmatch(r"\d{6}", value):
        raise ValueError(f"invalid A-share code: {code!r}")
    return value


def get_prefix(code: str) -> str:
    code = normalize_code(code)
    if code.startswith(("6", "9")):
        return "sh"
    if code.startswith("8"):
        return "bj"
    return "sz"


def get_cninfo_market(code: str) -> str:
    prefix = get_prefix(code)
    return {"sh": "沪市", "sz": "深市", "bj": "北交所"}[prefix]


# 巨潮 股票→orgId 映射（模块级缓存，首次调用时拉取一次，全程复用）
_CNINFO_ORGID_MAP: dict[str, str] = {}
_CNINFO_KNOWN_ORGIDS: dict[str, str] = {
    # cninfo orgId is not mechanically derived from market/code for many stocks.
    # Keep the v3.2.2 examples available when the live mapping endpoint is down.
    "601318": "9900002221",
    "601398": "jjxt0000019",
    "688017": "9900041602",
    "832000": "gfbj0832000",
}

def _cninfo_orgid(code: str) -> str:
    """查股票真实 orgId（V3.2.2 修复 #19）。
    巨潮 orgId 并非统一 `gssx0{code}` 格式（如 601318→9900002221、
    601398→jjxt0000019、688017→9900041602），硬编码会导致大量股票（尤其 601xxx 段）
    返回 totalAnnouncement=0、查不到公告。优先动态查官方映射表，查不到再回退硬编码。
    """
    if not _CNINFO_ORGID_MAP:
        try:
            import requests
            r = requests.get(
                "http://www.cninfo.com.cn/new/data/szse_stock.json",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            _CNINFO_ORGID_MAP.update(
                {s["code"]: s["orgId"] for s in r.json().get("stockList", [])}
            )
        except Exception:
            pass
    org = _CNINFO_ORGID_MAP.get(code) or _CNINFO_KNOWN_ORGIDS.get(code)
    if org:
        return org
    # fallback：老格式（仅部分老股票如 600519/600036 适用）
    if code.startswith("6"):
        return f"gssh0{code}"
    if code.startswith(("8", "4")):
        return f"gsbj0{code}"
    return f"gssz0{code}"


def get_cninfo_org_id(code: str) -> str:
    code = normalize_code(code)
    return _cninfo_orgid(code)


def prefixed_code(code: str) -> str:
    code = normalize_code(code)
    return f"{get_prefix(code)}{code}"


def safe_float(value, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def sanitize_filename(value: str, max_len: int = 80) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]', "_", value or "")
    return cleaned[:max_len] or "untitled"


def iter_dates(start_date: str, end_date: str) -> Iterable[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if end < start:
        raise ValueError("end_date must be >= start_date")
    current = start
    while current <= end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)
