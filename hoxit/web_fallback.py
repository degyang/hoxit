"""hoxit web fallback provider infrastructure.

Provides a controlled, injectable interface for browser-based data extraction
as a fallback when HTTP/API providers cannot deliver required fields.

Design principles:
- Default off: requires HOXIT_WEB_FALLBACK=1 to activate.
- No login/Cookie/profile assumptions: auth/captcha triggers user assistance.
- Injectable: browser/page/driver can be swapped for testing.
- Field-level quality: each extracted field carries its own status.
- Reusable: all logic lives in hoxit, not in UZEN or one-off scrapers.

Usage::

    from hoxit.web_fallback import create_provider, WebFetchResult

    provider = create_provider()  # returns None if HOXIT_WEB_FALLBACK != "1"
    if provider:
        result = provider.fetch("https://example.com/f10", fields=["roe", "revenue"])
        for field_name, entry in result.fields.items():
            print(field_name, entry["value"], entry["status"])
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


# ── Error classification ─────────────────────────────────────────


class WebFallbackError(Exception):
    """Base error for web fallback operations."""

    def __init__(self, message: str, *, url: str = "", detail: str = ""):
        super().__init__(message)
        self.url = url
        self.detail = detail


class WebTimeoutError(WebFallbackError):
    """Page load or element wait timed out."""


class WebNavigationError(WebFallbackError):
    """Failed to navigate to the target URL (DNS, connection, HTTP error)."""


class WebExtractionError(WebFallbackError):
    """Page loaded but field extraction failed (selector not found, parse error)."""


class WebAuthRequiredError(WebFallbackError):
    """Page requires login or authenticated session."""


class WebCaptchaError(WebFallbackError):
    """Page blocked by CAPTCHA or anti-bot challenge."""


# ── User assistance request ──────────────────────────────────────


@dataclass(frozen=True)
class UserAssistanceRequest:
    """Structured request for user help when automation cannot proceed.

    Attributes:
        kind: Type of assistance needed ("login", "captcha", "confirm_structure", "manual_extract").
        url: The URL that needs attention.
        message: Human-readable explanation of what's needed.
        fields: Which fields were being requested when the block occurred.
        detail: Additional context (e.g. selector that failed, error message).
    """

    kind: str
    url: str
    message: str
    fields: tuple[str, ...] = ()
    detail: str = ""


# ── Fetch result ─────────────────────────────────────────────────


@dataclass
class WebFetchResult:
    """Result from a web fallback fetch operation.

    Attributes:
        fields: Dict mapping field name to {"value": ..., "status": ..., "source": ...}.
                status is one of "available", "missing", "error".
        errors: List of error messages encountered during fetch.
        source_url: The URL that was fetched.
        quality: Overall quality assessment ("complete", "partial", "failed").
        fetched_at: Unix timestamp of the fetch.
        user_assistance: List of UserAssistanceRequest if user help is needed.
    """

    fields: dict[str, dict[str, Any]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    source_url: str = ""
    quality: str = "partial"
    fetched_at: float = field(default_factory=time.time)
    user_assistance: list[UserAssistanceRequest] = field(default_factory=list)

    @property
    def available_fields(self) -> dict[str, Any]:
        """Return only fields with status=='available'."""
        return {
            name: entry["value"]
            for name, entry in self.fields.items()
            if entry.get("status") == "available"
        }

    @property
    def has_user_assistance(self) -> bool:
        return bool(self.user_assistance)


# ── Provider protocol ────────────────────────────────────────────


@runtime_checkable
class WebFallbackProvider(Protocol):
    """Protocol for web fallback data providers.

    Implementations must:
    - Be injectable (accept driver/browser/page in constructor).
    - Return field-level results with status annotations.
    - Never silently swallow auth/captcha — must produce UserAssistanceRequest.
    - Be safe to close multiple times.
    """

    def is_available(self) -> bool:
        """Return True if the provider can operate (browser installed, env ok)."""
        ...

    def fetch(
        self,
        url: str,
        fields: list[str],
        *,
        wait_for: str | None = None,
        timeout: float = 30.0,
    ) -> WebFetchResult:
        """Fetch a URL and extract requested fields.

        Args:
            url: Target URL to fetch.
            fields: List of field names to extract.
            wait_for: Optional CSS selector to wait for before extraction.
            timeout: Page load timeout in seconds.

        Returns:
            WebFetchResult with field-level extraction results.
        """
        ...

    def close(self) -> None:
        """Release browser/driver resources. Safe to call multiple times."""
        ...


# ── Fake driver for testing ──────────────────────────────────────


class FakeWebDriver:
    """Test-only fake driver that returns pre-configured page content.

    Usage::

        driver = FakeWebDriver()
        driver.set_page("https://example.com", {
            "content": "<html>...</html>",
            "fields": {"roe": 15.2, "revenue": 1000},
            "error": None,
        })
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://example.com", fields=["roe"])
    """

    def __init__(self) -> None:
        self._pages: dict[str, dict[str, Any]] = {}
        self._closed = False

    def set_page(
        self,
        url: str,
        config: dict[str, Any],
    ) -> None:
        """Register a fake page response for a URL.

        config keys:
            content: HTML string (optional).
            fields: dict of field_name -> value for extraction.
            error: WebFallbackError subclass instance to raise (optional).
            error_class: error class name string (alternative to error instance).
            auth_required: bool, simulates login wall.
            captcha: bool, simulates CAPTCHA.
            load_time: float, simulated load time in seconds.
        """
        self._pages[url] = config

    def get_page(self, url: str) -> dict[str, Any]:
        """Get the fake page config for a URL. Raises WebNavigationError if not found."""
        if url not in self._pages:
            raise WebNavigationError(f"No fake page configured for {url}", url=url)
        return self._pages[url]

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._closed = True


# ── Simple provider implementation ───────────────────────────────


class SimpleWebProvider:
    """Minimal web fallback provider using an injectable driver.

    This is a reference implementation for testing and documentation.
    Production use should substitute a real Playwright-based driver.
    """

    def __init__(self, driver: Any | None = None) -> None:
        self._driver = driver
        self._closed = False

    def is_available(self) -> bool:
        if self._closed:
            return False
        if self._driver is None:
            return False
        return True

    def fetch(
        self,
        url: str,
        fields: list[str],
        *,
        wait_for: str | None = None,
        timeout: float = 30.0,
    ) -> WebFetchResult:
        if not self.is_available():
            return WebFetchResult(
                source_url=url,
                errors=["Provider is not available (closed or no driver)."],
                quality="failed",
            )

        try:
            page = self._driver.get_page(url)
        except WebFallbackError as exc:
            return WebFetchResult(
                source_url=url,
                errors=[str(exc)],
                quality="failed",
            )

        # Check for auth/captcha blocks
        if page.get("auth_required"):
            req = UserAssistanceRequest(
                kind="login",
                url=url,
                message="This page requires authentication. Please log in manually and retry.",
                fields=tuple(fields),
            )
            return WebFetchResult(
                source_url=url,
                errors=["Authentication required."],
                quality="failed",
                user_assistance=[req],
            )

        if page.get("captcha"):
            req = UserAssistanceRequest(
                kind="captcha",
                url=url,
                message="CAPTCHA detected. Please solve it manually and retry.",
                fields=tuple(fields),
            )
            return WebFetchResult(
                source_url=url,
                errors=["CAPTCHA blocked."],
                quality="failed",
                user_assistance=[req],
            )

        # Check for injected error
        error = page.get("error")
        if error and isinstance(error, WebFallbackError):
            return WebFetchResult(
                source_url=url,
                errors=[str(error)],
                quality="failed",
            )

        # Extract fields
        page_fields = page.get("fields", {})
        result_fields: dict[str, dict[str, Any]] = {}
        result_errors: list[str] = []
        available_count = 0

        for fname in fields:
            if fname in page_fields:
                value = page_fields[fname]
                if value is None:
                    result_fields[fname] = {
                        "value": None,
                        "status": "missing",
                        "source": "web_fallback",
                    }
                else:
                    result_fields[fname] = {
                        "value": value,
                        "status": "available",
                        "source": "web_fallback",
                    }
                    available_count += 1
            else:
                result_fields[fname] = {
                    "value": None,
                    "status": "missing",
                    "source": "web_fallback",
                }
                result_errors.append(f"Field '{fname}' not found in page.")

        # Determine overall quality
        if available_count == len(fields):
            quality = "complete"
        elif available_count > 0:
            quality = "partial"
        else:
            quality = "failed"

        return WebFetchResult(
            fields=result_fields,
            errors=result_errors,
            source_url=url,
            quality=quality,
        )

    def close(self) -> None:
        self._closed = True
        if self._driver is not None and hasattr(self._driver, "close"):
            self._driver.close()


# ── Factory ──────────────────────────────────────────────────────


def create_provider(
    driver: Any | None = None,
) -> SimpleWebProvider | None:
    """Create a web fallback provider if enabled.

    Returns None when HOXIT_WEB_FALLBACK env var is not "1".
    Pass a custom driver for testing; omit for production (needs real browser).
    """
    if os.environ.get("HOXIT_WEB_FALLBACK") != "1":
        return None
    return SimpleWebProvider(driver=driver)
