import pytest

from posit.connect import urls


class TestCreate:
    def test(self):
        url = "http://example.com/__api__"
        assert urls.create(url) == url

    def test_append_path(self):
        assert (
            urls.create("http://example.com/") == "http://example.com/__api__"
        )

    def test_missing_scheme(self):
        with pytest.raises(ValueError):
            urls.create("example.com")

    def test_missing_netloc(self):
        with pytest.raises(ValueError):
            urls.create("http://")


class TestAppend:
    def test(self):
        url = "http://example.com/__api__"
        url = urls.create(url)
        assert urls.append(url, "path") == "http://example.com/__api__/path"

    def test_slash_prefix(self):
        url = "http://example.com/__api__"
        url = urls.create(url)
        assert urls.append(url, "/path") == "http://example.com/__api__/path"

    def test_slash_suffix(self):
        url = "http://example.com/__api__"
        url = urls.create(url)
        assert urls.append(url, "path/") == "http://example.com/__api__/path"
