from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

DEFAULT_BASE_URL = "https://openapi.iwencai.com"
DEFAULT_TIMEOUT = 30
QUERY2DATA_ENDPOINT = "/v1/query2data"
COMPREHENSIVE_SEARCH_ENDPOINT = "/v1/comprehensive/search"
ROUTES_PATH = Path(__file__).resolve().parent / "routes.json"


class IwencaiError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, response: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


@dataclass(frozen=True)
class Route:
    key: str
    kind: str
    skill_id: str
    version: str
    description: str = ""
    channels: tuple[str, ...] = ()
    app_id: str = "AIME_SKILL"


def _requests_post(url: str, **kwargs):
    import requests

    return requests.post(url, **kwargs)


def routes_path() -> Path:
    return ROUTES_PATH


def load_routes(path: Path | None = None) -> dict[str, Route]:
    route_file = path or routes_path()
    raw = json.loads(route_file.read_text(encoding="utf-8"))
    routes: dict[str, Route] = {}
    for key, value in raw.items():
        routes[key] = Route(
            key=key,
            kind=value["kind"],
            skill_id=value["skill_id"],
            version=value["version"],
            description=value.get("description", ""),
            channels=tuple(value.get("channels", [])),
            app_id=value.get("app_id", "AIME_SKILL"),
        )
    return routes


def get_route(route: str | Route) -> Route:
    if isinstance(route, Route):
        return route
    routes = load_routes()
    if route not in routes:
        raise IwencaiError(f"unknown iwencai route: {route}")
    return routes[route]


def get_api_key(cli_api_key: str | None = None) -> str:
    api_key = cli_api_key or os.environ.get("IWENCAI_API_KEY", "")
    if not api_key:
        raise IwencaiError("未设置 API key。请设置 IWENCAI_API_KEY，或在一次性本地运行时传入 --api-key。")
    return api_key


def generate_trace_id() -> str:
    return secrets.token_hex(32)


def build_headers(*, api_key: str, route: Route, call_type: str, trace_id: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Claw-Call-Type": call_type,
        "X-Claw-Skill-Id": route.skill_id,
        "X-Claw-Skill-Version": route.version,
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": trace_id,
    }


def claw_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key, value in headers.items() if key.startswith("X-Claw-")}


def _response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text is not None:
        return str(text)
    content = getattr(response, "content", b"")
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    return str(content or "")


def _parse_response_body(response: Any) -> Any:
    text = _response_text(response)
    if text.strip():
        try:
            return response.json()
        except Exception:
            return text
    try:
        return response.json()
    except Exception:
        return ""


def post_json(
    *,
    url: str,
    payload: Mapping[str, Any],
    headers: Mapping[str, str],
    timeout: int,
    http_post: Callable | None = None,
    raise_for_status: bool = True,
) -> Any:
    post = http_post or _requests_post
    response = post(url, json=payload, headers=dict(headers), timeout=timeout)
    status_code = getattr(response, "status_code", None)
    parsed = _parse_response_body(response)
    if status_code != 200 and raise_for_status:
        raise IwencaiError(
            f"HTTP 错误 {status_code}",
            status_code=status_code,
            response=parsed,
        )
    if status_code != 200 and isinstance(parsed, str):
        return {
            "error": "invalid_json_response",
            "raw_response": parsed,
            "status_code": status_code,
        }
    return parsed


def query2data(
    *,
    route: str | Route,
    query: str,
    page: str = "1",
    limit: str = "10",
    api_key: str | None = None,
    call_type: str = "normal",
    timeout: int = DEFAULT_TIMEOUT,
    base_url: str = DEFAULT_BASE_URL,
    http_post: Callable | None = None,
) -> dict[str, Any]:
    resolved_route = get_route(route)
    if resolved_route.kind != "query2data":
        raise IwencaiError(f"Route '{resolved_route.key}' 不是 query2data route。")
    resolved_key = get_api_key(api_key)
    trace_id = generate_trace_id()
    payload = {
        "query": query,
        "page": page,
        "limit": limit,
        "is_cache": "1",
        "expand_index": "true",
    }
    headers = build_headers(api_key=resolved_key, route=resolved_route, call_type=call_type, trace_id=trace_id)
    response = post_json(
        url=f"{base_url.rstrip('/')}{QUERY2DATA_ENDPOINT}",
        payload=payload,
        headers=headers,
        timeout=timeout,
        http_post=http_post,
    )
    if isinstance(response, dict):
        response["trace_id"] = trace_id
        response["claw_headers"] = claw_headers(headers)
        return response
    if isinstance(response, list):
        return {"data": response, "trace_id": trace_id, "claw_headers": claw_headers(headers)}
    return {"text_response": str(response), "trace_id": trace_id, "claw_headers": claw_headers(headers)}


def comprehensive_search(
    *,
    route: str | Route,
    query: str,
    payload_extra: Mapping[str, Any] | None = None,
    api_key: str | None = None,
    call_type: str = "normal",
    timeout: int = DEFAULT_TIMEOUT,
    base_url: str = DEFAULT_BASE_URL,
    http_post: Callable | None = None,
) -> Any:
    resolved_route = get_route(route)
    if resolved_route.kind != "comprehensive_search":
        raise IwencaiError(f"Route '{resolved_route.key}' 不是 comprehensive_search route。")
    if not resolved_route.channels:
        raise IwencaiError(f"Route '{resolved_route.key}' 没有配置 search channels。")
    resolved_key = get_api_key(api_key)
    trace_id = generate_trace_id()
    payload = {
        "channels": list(resolved_route.channels),
        "app_id": resolved_route.app_id,
        "query": query,
    }
    if payload_extra:
        payload.update(payload_extra)
    headers = build_headers(api_key=resolved_key, route=resolved_route, call_type=call_type, trace_id=trace_id)
    return post_json(
        url=f"{base_url.rstrip('/')}{COMPREHENSIVE_SEARCH_ENDPOINT}",
        payload=payload,
        headers=headers,
        timeout=timeout,
        http_post=http_post,
        raise_for_status=False,
    )


def summarize_query2data_response(
    response: Any, *, query: str, page: str, limit: str
) -> dict[str, Any]:
    """添加本地 query2data 摘要元数据，使输出更易读。"""
    if not isinstance(response, dict) or "datas" not in response:
        return response

    datas = response.get("datas") or []
    try:
        code_count = int(response.get("code_count", 0) or 0)
    except (TypeError, ValueError):
        code_count = 0

    try:
        current_page = int(page)
        current_limit = int(limit)
    except ValueError:
        current_page = 1
        current_limit = len(datas) or 10

    output: dict[str, Any] = {
        "success": True,
        "query": query,
        "code_count": code_count,
        "returned_count": len(datas) if isinstance(datas, list) else 0,
        "page": page,
        "limit": limit,
        "has_more": current_page * current_limit < code_count,
        "chunks_info": response.get("chunks_info", {}),
        "trace_id": response.get("trace_id", ""),
        "datas": datas,
    }

    if output["has_more"]:
        output["pagination_tip"] = (
            f"共找到 {code_count} 条记录；当前页返回 {output['returned_count']} 条。"
        )
    if not datas:
        output["empty_data_tip"] = (
            "未查询到匹配数据。建议简化查询条件，并使用 --call-type retry 重试。"
        )
    return output


def query_rows(
    route: str | Route,
    query: str,
    *,
    page: str = "1",
    limit: str = "10",
    api_key: str | None = None,
    call_type: str = "normal",
    timeout: int = DEFAULT_TIMEOUT,
    base_url: str = DEFAULT_BASE_URL,
    http_post: Callable | None = None,
) -> list[dict]:
    response = query2data(
        route=route,
        query=query,
        page=page,
        limit=limit,
        api_key=api_key,
        call_type=call_type,
        timeout=timeout,
        base_url=base_url,
        http_post=http_post,
    )
    if isinstance(response, dict):
        return response.get("datas") or []
    return []


def search_rows(
    route: str | Route,
    query: str,
    *,
    payload_extra: Mapping[str, Any] | None = None,
    api_key: str | None = None,
    call_type: str = "normal",
    timeout: int = DEFAULT_TIMEOUT,
    base_url: str = DEFAULT_BASE_URL,
    http_post: Callable | None = None,
) -> list[dict]:
    response = comprehensive_search(
        route=route,
        query=query,
        payload_extra=payload_extra,
        api_key=api_key,
        call_type=call_type,
        timeout=timeout,
        base_url=base_url,
        http_post=http_post,
    )
    if isinstance(response, dict):
        return response.get("data") or []
    return []
