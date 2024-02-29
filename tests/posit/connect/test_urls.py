import pytest

from posit.connect.urls import append_path, server_to_api_url, validate


def test_append_path():
    assert append_path("http://foo.bar/__api__", "baz") == "http://foo.bar/__api__/baz"


def test_append_path_with_leading_slash():
    assert append_path("http://foo.bar/__api__", "/baz") == "http://foo.bar/__api__/baz"


def test_fix_with_correct_url():
    assert server_to_api_url("http://foo.bar/__api__") == "http://foo.bar/__api__"
    assert server_to_api_url("http://foo.bar/__api__/") == "http://foo.bar/__api__"


def test_fix_without_path():
    assert server_to_api_url("http://foo.bar") == "http://foo.bar/__api__"


def test_fix_with_proxy_path():
    assert server_to_api_url("http://foo.bar/baz") == "http://foo.bar/baz/__api__"


def test_validate_without_scheme():
    with pytest.raises(ValueError):
        validate("foo.bar/__api__")


def test_validate_without_netloc():
    with pytest.raises(ValueError):
        validate("http:///__api__")
