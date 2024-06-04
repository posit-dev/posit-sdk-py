from unittest.mock import Mock
import pytest
import warnings

from typing import Any, List, Optional

from requests.sessions import Session as Session

from posit.connect.resources import Resource, Resources

config = Mock()
session = Mock()


class FakeResource(Resource):
    @property
    def foo(self) -> Optional[str]:
        return self.get("foo")


class TestResource:
    def test_init(self):
        k = "foo"
        v = "bar"
        d = dict({k: v})
        r = FakeResource(config, session, **d)
        assert r.session == session
        assert r.config == config

    def test__getitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v = "bar"
        d = dict({k: v})
        r = FakeResource(config, session, **d)
        assert r.__getitem__(k) == d.__getitem__(k)
        assert r[k] == d[k]

    def test__setitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v1 = "bar"
        v2 = "baz"
        d = dict({k: v1})
        r = FakeResource(config, session, **d)
        assert r[k] == v1
        r[k] = v2
        assert r[k] == v2

    def test__delitem__(self):
        warnings.filterwarnings("ignore", category=FutureWarning)
        k = "foo"
        v = "bar"
        d = dict({k: v})
        r = FakeResource(config, session, **d)
        assert k in r
        assert r[k] == v
        del r[k]
        assert k not in r

    def test_foo(self):
        k = "foo"
        v = "bar"
        d = dict({k: v})
        r = FakeResource(config, session, **d)
        assert r.foo == v
