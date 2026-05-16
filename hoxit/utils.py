from __future__ import annotations

from datetime import datetime, timedelta
import re
from typing import Iterable


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
