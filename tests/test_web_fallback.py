"""Tests for hoxit web fallback provider infrastructure.

All tests use FakeWebDriver — no network, no browser, no Playwright.
"""

from __future__ import annotations

import os

import pytest

from hoxit.web_fallback import (
    FakeWebDriver,
    SimpleWebProvider,
    UserAssistanceRequest,
    WebAuthRequiredError,
    WebCaptchaError,
    WebExtractionError,
    WebFallbackError,
    WebFallbackProvider,
    WebFetchResult,
    WebNavigationError,
    WebTimeoutError,
    create_provider,
)


# ── WebFetchResult ───────────────────────────────────────────────


class TestWebFetchResult:
    def test_default_construction(self):
        result = WebFetchResult()
        assert result.fields == {}
        assert result.errors == []
        assert result.source_url == ""
        assert result.quality == "partial"
        assert result.fetched_at > 0
        assert result.user_assistance == []

    def test_available_fields_filter(self):
        result = WebFetchResult(
            fields={
                "roe": {"value": 15.2, "status": "available", "source": "web_fallback"},
                "revenue": {"value": None, "status": "missing", "source": "web_fallback"},
                "nim": {"value": None, "status": "error", "source": "web_fallback"},
            }
        )
        available = result.available_fields
        assert available == {"roe": 15.2}
        assert "revenue" not in available
        assert "nim" not in available

    def test_has_user_assistance(self):
        result = WebFetchResult()
        assert result.has_user_assistance is False

        req = UserAssistanceRequest(
            kind="login", url="https://x.com", message="Please log in."
        )
        result.user_assistance.append(req)
        assert result.has_user_assistance is True


# ── Error hierarchy ──────────────────────────────────────────────


class TestErrorHierarchy:
    def test_base_error(self):
        exc = WebFallbackError("fail", url="http://x", detail="bad")
        assert str(exc) == "fail"
        assert exc.url == "http://x"
        assert exc.detail == "bad"

    def test_timeout_is_fallback_error(self):
        assert issubclass(WebTimeoutError, WebFallbackError)

    def test_navigation_is_fallback_error(self):
        assert issubclass(WebNavigationError, WebFallbackError)

    def test_extraction_is_fallback_error(self):
        assert issubclass(WebExtractionError, WebFallbackError)

    def test_auth_is_fallback_error(self):
        assert issubclass(WebAuthRequiredError, WebFallbackError)

    def test_captcha_is_fallback_error(self):
        assert issubclass(WebCaptchaError, WebFallbackError)

    def test_all_errors_catchable_by_base(self):
        errors = [
            WebTimeoutError("t"),
            WebNavigationError("n"),
            WebExtractionError("e"),
            WebAuthRequiredError("a"),
            WebCaptchaError("c"),
        ]
        for exc in errors:
            with pytest.raises(WebFallbackError):
                raise exc


# ── UserAssistanceRequest ────────────────────────────────────────


class TestUserAssistanceRequest:
    def test_construction(self):
        req = UserAssistanceRequest(
            kind="captcha",
            url="https://ths.com/f10",
            message="CAPTCHA detected.",
            fields=("roe", "revenue"),
            detail="Cloudflare challenge",
        )
        assert req.kind == "captcha"
        assert req.url == "https://ths.com/f10"
        assert req.message == "CAPTCHA detected."
        assert req.fields == ("roe", "revenue")
        assert req.detail == "Cloudflare challenge"

    def test_frozen(self):
        req = UserAssistanceRequest(kind="login", url="u", message="m")
        with pytest.raises(AttributeError):
            req.kind = "other"  # type: ignore[misc]

    def test_defaults(self):
        req = UserAssistanceRequest(kind="login", url="u", message="m")
        assert req.fields == ()
        assert req.detail == ""


# ── FakeWebDriver ────────────────────────────────────────────────


class TestFakeWebDriver:
    def test_set_and_get_page(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"fields": {"a": 1}})
        page = driver.get_page("https://x.com")
        assert page["fields"]["a"] == 1

    def test_get_unknown_url_raises_navigation_error(self):
        driver = FakeWebDriver()
        with pytest.raises(WebNavigationError):
            driver.get_page("https://unknown.com")

    def test_close(self):
        driver = FakeWebDriver()
        assert driver.closed is False
        driver.close()
        assert driver.closed is True


# ── SimpleWebProvider ────────────────────────────────────────────


class TestSimpleWebProvider:
    def test_fetch_extracts_fields(self):
        driver = FakeWebDriver()
        driver.set_page("https://ths.com/f10", {
            "fields": {"roe": 15.2, "revenue": 1000.0, "net_profit": None},
        })
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://ths.com/f10", fields=["roe", "revenue", "net_profit"])

        assert result.quality == "partial"
        assert result.fields["roe"]["value"] == 15.2
        assert result.fields["roe"]["status"] == "available"
        assert result.fields["revenue"]["value"] == 1000.0
        assert result.fields["revenue"]["status"] == "available"
        assert result.fields["net_profit"]["value"] is None
        assert result.fields["net_profit"]["status"] == "missing"
        assert result.source_url == "https://ths.com/f10"

    def test_fetch_complete_quality(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"fields": {"a": 1, "b": 2}})
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["a", "b"])
        assert result.quality == "complete"

    def test_fetch_failed_quality_when_no_fields_found(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"fields": {"other": 1}})
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["missing_field"])
        assert result.quality == "failed"
        assert "missing_field" not in result.available_fields

    def test_fetch_auth_required(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"auth_required": True})
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["roe"])

        assert result.quality == "failed"
        assert result.has_user_assistance
        assert result.user_assistance[0].kind == "login"
        assert result.user_assistance[0].fields == ("roe",)

    def test_fetch_captcha(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"captcha": True})
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["roe"])

        assert result.quality == "failed"
        assert result.has_user_assistance
        assert result.user_assistance[0].kind == "captcha"

    def test_fetch_navigation_error(self):
        driver = FakeWebDriver()
        # No page configured → WebNavigationError
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://unknown.com", fields=["roe"])

        assert result.quality == "failed"
        assert len(result.errors) == 1
        assert "No fake page configured" in result.errors[0]

    def test_fetch_injected_error(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {
            "error": WebTimeoutError("Page load timed out", url="https://x.com"),
        })
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["roe"])
        assert result.quality == "failed"
        assert "timed out" in result.errors[0]

    def test_fetch_no_driver(self):
        provider = SimpleWebProvider(driver=None)
        result = provider.fetch("https://x.com", fields=["roe"])
        assert result.quality == "failed"
        assert "not available" in result.errors[0].lower()

    def test_is_available(self):
        provider = SimpleWebProvider(driver=None)
        assert provider.is_available() is False

        driver = FakeWebDriver()
        provider = SimpleWebProvider(driver=driver)
        assert provider.is_available() is True

        provider.close()
        assert provider.is_available() is False

    def test_close_idempotent(self):
        driver = FakeWebDriver()
        provider = SimpleWebProvider(driver=driver)
        provider.close()
        provider.close()  # should not raise
        assert driver.closed is True

    def test_fetch_preserves_source_annotation(self):
        driver = FakeWebDriver()
        driver.set_page("https://x.com", {"fields": {"roe": 12.0}})
        provider = SimpleWebProvider(driver=driver)
        result = provider.fetch("https://x.com", fields=["roe"])
        assert result.fields["roe"]["source"] == "web_fallback"


# ── create_provider factory ─────────────────────────────────────


class TestCreateProvider:
    def test_returns_none_when_env_not_set(self, monkeypatch):
        monkeypatch.delenv("HOXIT_WEB_FALLBACK", raising=False)
        assert create_provider() is None

    def test_returns_none_when_env_not_one(self, monkeypatch):
        monkeypatch.setenv("HOXIT_WEB_FALLBACK", "0")
        assert create_provider() is None

    def test_returns_provider_when_env_is_one(self, monkeypatch):
        monkeypatch.setenv("HOXIT_WEB_FALLBACK", "1")
        provider = create_provider()
        assert provider is not None
        assert isinstance(provider, SimpleWebProvider)
        provider.close()

    def test_returns_provider_with_custom_driver(self, monkeypatch):
        monkeypatch.setenv("HOXIT_WEB_FALLBACK", "1")
        driver = FakeWebDriver()
        provider = create_provider(driver=driver)
        assert provider is not None
        assert provider.is_available() is True
        provider.close()


# ── Protocol conformance ─────────────────────────────────────────


class TestProtocolConformance:
    def test_simple_provider_satisfies_protocol(self):
        provider = SimpleWebProvider(driver=FakeWebDriver())
        assert isinstance(provider, WebFallbackProvider)
        provider.close()
