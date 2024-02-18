import pytest

from .urls import append_path


def test_fix_without_scheme():
    with pytest.raises(ValueError):
        append_path("foo.bar/__api__", "baz")


def test_fix_without_netloc():
    with pytest.raises(ValueError):
        append_path("http:///__api__", "baz")


def test_fix_without_path():
    with pytest.raises(ValueError):
        append_path("http://foo.bar", "baz")


def test_fix_without_correct_path():
    with pytest.raises(ValueError):
        append_path("http://foo.bar/baz", "qux")


def test_fix_with_no_errors():
    url = append_path("http://foo.bar/baz/__api__", "qux")
    assert url == "http://foo.bar/baz/__api__/qux"
