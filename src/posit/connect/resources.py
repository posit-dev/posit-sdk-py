from __future__ import annotations


from abc import ABC, abstractmethod
from typing import Generic, Iterator, Optional, TypeVar, List, TypedDict, Tuple


class Resource(TypedDict):
    pass


T = TypeVar("T", bound=Resource)


class CachedResources(ABC, Generic[T], Iterator[T]):
    def __init__(self, data: List[T] = []) -> None:
        super().__init__()
        self.data = data

    @abstractmethod
    def find(self, *args, **kwargs) -> CachedResources[T]:
        raise NotImplementedError()

    @abstractmethod
    def find_one(self, *args, **kwargs) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, id: str) -> T:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[T]:
        self.index = 0
        return self

    def __next__(self) -> T:
        if self.index >= len(self.data):
            raise StopIteration

        v = self.data[self.index]
        self.index += 1
        return v

    def to_pandas(self):
        try:
            from pandas import DataFrame

            return DataFrame(self)
        except ImportError:
            return None


class Resources(CachedResources[T]):
    def __init__(self, data: List[T] = []) -> None:
        super().__init__(data)
        self.data = data
        self.exhausted = False
        self.index = 0

    @abstractmethod
    def fetch(self, index) -> Tuple[Optional[Iterator[T]], bool]:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[T]:
        self.index = 0
        return self

    def __next__(self) -> T:
        if self.index >= len(self.data):
            if self.exhausted:
                raise StopIteration

            results, self.exhausted = self.fetch(self.index)
            if not results:
                raise StopIteration

            self.data += results

        v = self.data[self.index]
        self.index += 1
        return v
