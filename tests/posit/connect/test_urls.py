import pytest

from posit.connect import urls


class TestCreate:
    def test(self):
        url = "http://example.com/__api__"
        assert urls.Url(url) == url

    def test_append_path(self):
        assert urls.Url("http://example.com/") == "http://example.com/__api__"

    def test_missing_scheme(self):
        with pytest.raises(ValueError):
            urls.Url("example.com")

    def test_missing_netloc(self):
        with pytest.raises(ValueError):
            urls.Url("http://")


class TestAppend:
    def test(self):
        url = "http://example.com/__api__"
        url = urls.Url(url)
        assert url + "path" == "http://example.com/__api__/path"

    def test_slash_prefix(self):
        url = "http://example.com/__api__"
        url = urls.Url(url)
        assert url + "/path" == "http://example.com/__api__/path"

    def test_slash_suffix(self):
        url = "http://example.com/__api__"
        url = urls.Url(url)
        assert url + "path/" == "http://example.com/__api__/path"

    def test_protocol_relative_is_neutralized(self):
        # A protocol-relative fragment must not escape the base host.
        url = urls.Url("http://example.com/__api__")
        joined = url + "//evil.com/path"
        from urllib.parse import urlsplit

        assert urlsplit(joined).hostname == "example.com"

    def test_absolute_url_is_neutralized(self):
        # An absolute-URL fragment must not escape the base host.
        url = urls.Url("http://example.com/__api__")
        joined = url + "https://evil.com/path"
        from urllib.parse import urlsplit

        assert urlsplit(joined).hostname == "example.com"


class TestSafeUrljoin:
    base = "http://example.com/__api__"

    def test_relative_path(self):
        assert (
            urls.safe_urljoin(self.base, "content/abc")
            == "http://example.com/__api__/content/abc"
        )

    def test_absolute_from_root(self):
        # A leading slash must not escape the base path.
        assert (
            urls.safe_urljoin(self.base, "/content/abc")
            == "http://example.com/__api__/content/abc"
        )

    def test_protocol_relative(self):
        # ``//evil.com/path`` must be treated as a relative path under base.
        assert (
            urls.safe_urljoin(self.base, "//evil.com/path")
            == "http://example.com/__api__/evil.com/path"
        )

    def test_absolute_url(self):
        # A fully-qualified absolute URL fragment must be rejected because it
        # would otherwise resolve to an attacker-controlled host.
        with pytest.raises(ValueError):
            urls.safe_urljoin(self.base, "https://evil.com/path")

    def test_normal_case(self):
        assert (
            urls.safe_urljoin("http://example.com/__api__/", "v1/users")
            == "http://example.com/__api__/v1/users"
        )

    def test_port_mismatch_rejected(self):
        # A fragment targeting a different port on the same host must be rejected.
        with pytest.raises(ValueError):
            urls.safe_urljoin("http://example.com/__api__", "http://example.com:8080/x")
