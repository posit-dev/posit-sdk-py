import warnings
from unittest import mock
from unittest.mock import Mock

from typing_extensions import Optional

from posit.connect.resources import (
    BaseResource,
    _contains_dict_key_values,
    _matches_exact,
    _matches_pattern,
)

config = Mock()
session = Mock()


class FakeResource(BaseResource):
    @property
    def foo(self) -> Optional[str]:
        return self.get("foo")


class TestResource:
    def test_init(self):
        p = mock.Mock()
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(p, **d)
        assert r._ctx == p

    def test__getitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(mock.Mock(), **d)
        assert r.__getitem__(k) == d.__getitem__(k)
        assert r[k] == d[k]

    def test__setitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v1 = "bar"
        v2 = "baz"
        d = {k: v1}
        r = FakeResource(mock.Mock(), **d)
        assert r[k] == v1
        r[k] = v2
        assert r[k] == v2

    def test__delitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(mock.Mock(), **d)
        assert k in r
        assert r[k] == v
        del r[k]
        assert k not in r

    def test_foo(self):
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(mock.Mock(), **d)
        assert r.foo == v


class TestContainsDictKeyValues:
    def test_empty_value_dict(self):
        r = FakeResource(mock.Mock(), foo={"a": 1, "b": 2})
        assert _contains_dict_key_values(r, "foo", {}) is True

    def test_matching_single_key_value(self):
        r = FakeResource(mock.Mock(), foo={"a": 1, "b": 2})
        assert _contains_dict_key_values(r, "foo", {"a": 1}) is True

    def test_matching_multiple_key_values(self):
        r = FakeResource(mock.Mock(), foo={"a": 1, "b": 2, "c": 3})
        assert _contains_dict_key_values(r, "foo", {"a": 1, "b": 2}) is True

    def test_non_matching_key_value(self):
        r = FakeResource(mock.Mock(), foo={"a": 1, "b": 2})
        assert _contains_dict_key_values(r, "foo", {"a": 2}) is False

    def test_missing_key_in_item(self):
        r = FakeResource(mock.Mock(), foo={"a": 1})
        assert _contains_dict_key_values(r, "foo", {"b": 2}) is False

    def test_missing_field_in_resource(self):
        r = FakeResource(mock.Mock())
        assert _contains_dict_key_values(r, "nonexistent", {"a": 1}) is False

    def test_non_dict_field_value(self):
        r = FakeResource(mock.Mock(), foo="not_a_dict")
        assert _contains_dict_key_values(r, "foo", {"a": 1}) is False

    def test_nested_dict_values(self):
        r = FakeResource(mock.Mock(), foo={"nested": {"x": 10}, "simple": "value"})
        assert _contains_dict_key_values(r, "foo", {"nested": {"x": 10}}) is True
        assert _contains_dict_key_values(r, "foo", {"nested": {"x": 20}}) is False


class TestMatchesPattern:
    def test_pattern_matches(self):
        r = FakeResource(mock.Mock(), name="test-app-123")
        assert _matches_pattern(r, "name", r"test-.*-\d+") is True

    def test_pattern_does_not_match(self):
        r = FakeResource(mock.Mock(), name="production-app")
        assert _matches_pattern(r, "name", r"test-.*-\d+") is False

    def test_missing_field_returns_false(self):
        r = FakeResource(mock.Mock())
        assert _matches_pattern(r, "nonexistent", ".*") is False

    def test_empty_pattern_matches_any_string(self):
        r = FakeResource(mock.Mock(), description="any text here")
        assert _matches_pattern(r, "description", "") is True

    def test_partial_match_returns_true(self):
        r = FakeResource(mock.Mock(), title="My Great App")
        assert _matches_pattern(r, "title", "Great") is True


class TestMatchesExact:
    def test_exact_match_returns_true(self):
        r = FakeResource(mock.Mock(), name="test-app")
        assert _matches_exact(r, "name", "test-app") is True

    def test_no_match_returns_false(self):
        r = FakeResource(mock.Mock(), name="test-app")
        assert _matches_exact(r, "name", "other-app") is False

    def test_missing_field_returns_false(self):
        r = FakeResource(mock.Mock())
        assert _matches_exact(r, "nonexistent", "value") is False
