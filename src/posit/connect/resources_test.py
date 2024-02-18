from typing import Iterator, Tuple, Optional
from unittest.mock import Mock

from .resources import Resource, CachedResources, Resources


class FakeResource(Resource):
    pass


class FakeCachedResources(CachedResources[FakeResource]):
    def find(self) -> CachedResources[FakeResource]:
        return self

    def find_one(self) -> Optional[FakeResource]:
        return Mock(spec=FakeResource)

    def get(self, _: str) -> FakeResource:
        return Mock(spec=FakeResource)


class TestCachedResources:
    def test_init(self):
        resources = FakeCachedResources()
        assert resources == resources.find()
        assert resources.find_one()
        assert resources.get(None)


class FakeResources(FakeCachedResources, Resources):
    def __init__(self) -> None:
        super().__init__("")

    def fetch(self, index) -> Tuple[Optional[Iterator[FakeResource]], bool]:
        return iter([FakeResource()]), len(self.data) > 0


class TestFakeResources:
    def test_init(self):
        resources = FakeResources()
        assert resources == resources.find()
        assert resources.find_one()
        assert resources.get(None)
