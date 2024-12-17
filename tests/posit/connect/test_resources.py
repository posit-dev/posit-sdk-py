import warnings
from unittest import mock
from unittest.mock import Mock

from typing_extensions import Optional

from posit.connect.resources import BaseResource

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
