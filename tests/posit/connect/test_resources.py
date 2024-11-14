import warnings
from typing import Optional
from unittest import mock
from unittest.mock import Mock

import pytest

from posit.connect._active import ResourceDict

config = Mock()
session = Mock()


class FakeResource(ResourceDict):
    @property
    def foo(self) -> Optional[str]:
        return self.get("foo")


class TestResource:
    def test_init(self):
        ctx = mock.Mock()
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(ctx, **d)
        assert r._ctx == ctx

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
        with pytest.raises(NotImplementedError):
            r[k] = v2

    def test__delitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(mock.Mock(), **d)
        assert k in r
        assert r[k] == v
        with pytest.raises(NotImplementedError):
            del r[k]

    def test_foo(self):
        k = "foo"
        v = "bar"
        d = {k: v}
        r = FakeResource(mock.Mock(), **d)
        assert r.foo == v
