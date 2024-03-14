import pytest

from dataclasses import dataclass
from typing import Any, List, Optional

from posit.connect.resources import Resources, Resource


@dataclass(init=False)
class FakeResource(Resource):
    foo: str
    bar: str

    @property
    def _compatibility(self):
        return {"backwards": "foo"}

    @property
    def backwards(self):
        """A field which was removed from the API.

        This property provides backwards compatibility when a Connect is upgraded to a newer version which no longer provides "backwards".
        """
        return self.foo


class TestResource:
    def test_init(self):
        r = FakeResource(foo="foo", bar="bar")
        assert r.foo == "foo"
        assert r.bar == "bar"

    def test_from_dict(self):
        o = {"foo": "foo", "bar": "bar"}
        r = FakeResource(**o)
        assert r.foo == "foo"
        assert r.bar == "bar"

    def test_from_dict_with_missing_fields(self):
        o = {"bar": "bar"}
        r = FakeResource(**o)
        assert r.foo is None
        assert r.bar == "bar"

    def test_from_dict_with_additional_fields(self):
        o = {"foo": "foo", "bar": "bar", "baz": "baz"}
        r = FakeResource(**o)
        assert r.foo == "foo"

    def test_forwards_compatibility(self):
        o = {"foo": "foo", "bar": "bar"}
        r = FakeResource(**o)
        assert r.backwards == "foo"
        assert r.bar == "bar"

    def test_client_backwards_compatibility(self):
        o = {"foo": "foo", "bar": "bar"}
        r = FakeResource(**o)
        assert r.foo == "foo"
        assert r.bar == "bar"
        assert r.backwards == "foo"

    def test_server_backwards_compatibility(self):
        """Asserts backwards compatibility for changes on the server.

        This checks that client code written for a current version of Connect can continue to function with previous versions of Connect when we implement backwards compatibility.
        """
        o = {"bar": "bar", "backwards": "backwards"}
        r = FakeResource(**o)
        assert r.foo == "backwards"
        assert r.backwards == "backwards"


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
