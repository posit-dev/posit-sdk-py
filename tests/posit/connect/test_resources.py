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


class TestResources(Resources[Any]):
    def create(self) -> Any:
        return super().create()  # type: ignore [safe-super]

    def delete(self) -> None:
        return super().delete()  # type: ignore [safe-super]

    def find(self) -> List[Any]:
        return super().find()  # type: ignore [safe-super]

    def find_one(self) -> Optional[Any]:
        return super().find_one()  # type: ignore [safe-super]

    def get(self) -> Any:
        return super().get()  # type: ignore [safe-super]

    def update(self) -> Any:
        return super().update()  # type: ignore [safe-super]

    def count(self) -> int:
        return super().count()  # type: ignore [safe-super]

    def test_create(self):
        with pytest.raises(NotImplementedError):
            self.create()

    def test_delete(self):
        with pytest.raises(NotImplementedError):
            self.delete()

    def test_find(self):
        with pytest.raises(NotImplementedError):
            self.find()

    def test_find_one(self):
        with pytest.raises(NotImplementedError):
            self.find_one()

    def test_get(self):
        with pytest.raises(NotImplementedError):
            self.get()

    def test_update(self):
        with pytest.raises(NotImplementedError):
            self.update()

    def test_count(self):
        with pytest.raises(NotImplementedError):
            self.count()
