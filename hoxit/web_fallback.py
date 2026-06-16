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


# ── Playwright driver ────────────────────────────────────────────


class PlaywrightDriver:
    """Real Playwright-based driver for headless Chromium scraping.

    Usage::

        driver = PlaywrightDriver()
        page = driver.get_page("https://...")
        driver.close()
    """

    def __init__(self, *, headless: bool = True) -> None:
        from playwright.sync_api import sync_playwright
        self._pw_cm = sync_playwright()
        self._pw = self._pw_cm.start()
        self._browser = self._pw.chromium.launch(headless=headless)
        self._closed = False

    def get_page(self, url: str, *, wait_until: str = "networkidle", timeout: float = 30000) -> dict[str, Any]:
        """Navigate to URL and return page content as a dict.

        Returns dict with keys:
            content: HTML string
            text: inner text
            url: final URL after redirects
        """
        if self._closed:
            raise WebNavigationError("Driver is closed.", url=url)
        page = self._browser.new_page()
        try:
            page.goto(url, wait_until=wait_until, timeout=timeout)
            return {
                "content": page.content(),
                "text": page.inner_text("body"),
                "url": page.url,
            }
        except Exception as exc:
            if "timeout" in str(exc).lower():
                raise WebTimeoutError(f"Page load timed out: {exc}", url=url) from exc
            raise WebNavigationError(f"Navigation failed: {exc}", url=url) from exc
        finally:
            page.close()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                self._browser.close()
            except Exception:
                pass
            try:
                self._pw_cm.__exit__(None, None, None)
            except Exception:
                pass


# ── Eastmoney F10 bank metrics scraper ───────────────────────────


def _parse_cn_number(text: str) -> float | None:
    """Parse a Chinese-formatted number like '2.245万亿', '3359亿', '0.76'."""
    text = text.strip()
    if text in ("--", "", "-", "N/A"):
        return None
    multiplier = 1.0
    if text.endswith("万亿"):
        multiplier = 1e12
        text = text[:-2]
    elif text.endswith("亿"):
        multiplier = 1e8
        text = text[:-1]
    elif text.endswith("万"):
        multiplier = 1e4
        text = text[:-1]
    try:
        return float(text) * multiplier
    except (ValueError, TypeError):
        return None


def _extract_indicators_from_text(
    page_text: str,
    indicators: dict[str, str],
) -> dict[str, float | None]:
    """Extract indicator values from eastmoney F10 page text.

    Args:
        page_text: Full inner text of the F10 page.
        indicators: Mapping of {search_label: result_key}, e.g.
                    {"不良贷款率(%)": "npl_ratio"}.

    Returns:
        Dict of {result_key: first_found_value_or_None}.
    """
    results: dict[str, float | None] = {v: None for v in indicators.values()}
    lines = page_text.split("\n")

    for label, key in indicators.items():
        if results[key] is not None:
            continue  # already found
        for i, line in enumerate(lines):
            if label in line:
                # The line may be: "不良贷款率(%)	0.76	0.76	0.76 ..."
                parts = line.split("\t")
                # Find the part that contains the label, take the next non-empty part
                found_label = False
                for part in parts:
                    if found_label:
                        val = _parse_cn_number(part)
                        if val is not None:
                            results[key] = val
                            break
                    if label in part:
                        found_label = True
                # If no value on same line, check next line
                if results[key] is None and i + 1 < len(lines):
                    next_parts = lines[i + 1].split("\t")
                    for part in next_parts:
                        val = _parse_cn_number(part)
                        if val is not None:
                            results[key] = val
                            break
                break  # found the label, stop searching this line

    return results


def scrape_eastmoney_bank_metrics(
    code: str,
    *,
    driver: PlaywrightDriver | None = None,
    headless: bool = True,
) -> WebFetchResult:
    """Scrape bank-specific metrics from eastmoney F10 page.

    Extracts: npl_ratio, provision_coverage, capital_adequacy,
    core_capital_adequacy from the 专项指标 section.

    Args:
        code: 6-digit A-share code (e.g. "002142").
        driver: Optional PlaywrightDriver instance. Creates one if None.
        headless: Whether to run browser headless (default True).

    Returns:
        WebFetchResult with extracted bank metrics.
    """
    # Build eastmoney F10 URL
    prefix = "SZ" if code.startswith(("0", "3")) else "SH"
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/FinanceAnalysis/Index?type=web&code={prefix}{code}"

    own_driver = False
    if driver is None:
        try:
            driver = PlaywrightDriver(headless=headless)
            own_driver = True
        except Exception as exc:
            return WebFetchResult(
                source_url=url,
                errors=[f"Failed to start Playwright: {exc}"],
                quality="failed",
            )

    try:
        page_data = driver.get_page(url)
    except WebFallbackError as exc:
        return WebFetchResult(
            source_url=url,
            errors=[str(exc)],
            quality="failed",
        )
    finally:
        if own_driver:
            driver.close()

    page_text = page_data.get("text", "")

    # Indicators to extract from the 专项指标 section
    indicators = {
        "不良贷款率(%)": "npl_ratio",
        "不良贷款拨备覆盖率(%)": "provision_coverage",
        "资本充足率(%)": "capital_adequacy",
        "核心资本充足率(%)": "core_capital_adequacy",
    }

    values = _extract_indicators_from_text(page_text, indicators)

    # Build result fields
    result_fields: dict[str, dict[str, Any]] = {}
    available_count = 0
    for key, value in values.items():
        if value is not None:
            result_fields[key] = {
                "value": value,
                "status": "available",
                "source": "web_fallback.eastmoney_f10",
            }
            available_count += 1
        else:
            result_fields[key] = {
                "value": None,
                "status": "missing",
                "source": "web_fallback.eastmoney_f10",
            }

    total = len(values)
    if available_count == total:
        quality = "complete"
    elif available_count > 0:
        quality = "partial"
    else:
        quality = "failed"

    return WebFetchResult(
        fields=result_fields,
        errors=[] if available_count > 0 else ["No bank metrics found on page."],
        source_url=url,
        quality=quality,
    )


def scrape_eastmoney_finance_overview(
    code: str,
    *,
    driver: PlaywrightDriver | None = None,
    headless: bool = True,
) -> WebFetchResult:
    """Scrape main financial indicators from eastmoney F10 page.

    Extracts: roe, net_profit, revenue, net_margin, eps, book_value_per_share
    from the 主要指标 section.

    Args:
        code: 6-digit A-share code.
        driver: Optional PlaywrightDriver. Creates one if None.
        headless: Whether to run browser headless.

    Returns:
        WebFetchResult with extracted finance fields.
    """
    prefix = "SZ" if code.startswith(("0", "3")) else "SH"
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/FinanceAnalysis/Index?type=web&code={prefix}{code}"

    own_driver = False
    if driver is None:
        try:
            driver = PlaywrightDriver(headless=headless)
            own_driver = True
        except Exception as exc:
            return WebFetchResult(
                source_url=url,
                errors=[f"Failed to start Playwright: {exc}"],
                quality="failed",
            )

    try:
        page_data = driver.get_page(url)
    except WebFallbackError as exc:
        return WebFetchResult(
            source_url=url,
            errors=[str(exc)],
            quality="failed",
        )
    finally:
        if own_driver:
            driver.close()

    page_text = page_data.get("text", "")

    # Main financial indicators
    indicators = {
        "净资产收益率(加权)(%)": "roe",
        "基本每股收益(元)": "eps",
        "每股净资产(元)": "book_value_per_share",
        "净利率(%)": "net_margin",
    }

    values = _extract_indicators_from_text(page_text, indicators)

    # Also extract revenue and net profit from the growth section
    growth_indicators = {
        "营业总收入(元)": "revenue",
        "归属净利润(元)": "net_profit",
    }
    growth_values = _extract_indicators_from_text(page_text, growth_indicators)
    values.update(growth_values)

    # Build result
    result_fields: dict[str, dict[str, Any]] = {}
    available_count = 0
    for key, value in values.items():
        if value is not None:
            result_fields[key] = {
                "value": value,
                "status": "available",
                "source": "web_fallback.eastmoney_f10",
            }
            available_count += 1
        else:
            result_fields[key] = {
                "value": None,
                "status": "missing",
                "source": "web_fallback.eastmoney_f10",
            }

    total = len(values)
    if available_count == total:
        quality = "complete"
    elif available_count > 0:
        quality = "partial"
    else:
        quality = "failed"

    return WebFetchResult(
        fields=result_fields,
        errors=[] if available_count > 0 else ["No finance indicators found on page."],
        source_url=url,
        quality=quality,
    )
