from typing import Iterator, Tuple, Optional
from unittest.mock import Mock

from .resources import Resource, Resources, LazyResources


class FakeResource(Resource):
    pass


class FakeResources(Resources[FakeResource]):
    def find(self) -> Resources[FakeResource]:
        return self

    def find_one(self) -> Optional[FakeResource]:
        return Mock(spec=FakeResource)

    def get(self, _: str) -> FakeResource:
        return Mock(spec=FakeResource)


class TestResources:
    def test(self):
        resources = FakeResources()
        assert resources == resources.find()
        assert resources.find_one()
        assert resources.get(None)


class FakeLazyResources(FakeResources, LazyResources):
    def fetch(self, index) -> Tuple[Optional[Iterator[FakeResource]], bool]:
        return iter([FakeResource()]), len(self.data) > 0


class TestFakeLazyResources:
    def test(self):
        resources = FakeLazyResources()
        assert resources == resources.find()
        assert resources.find_one()
        assert resources.get(None)
