from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar


T = TypeVar("T")


class Resources(ABC, Generic[T]):
    @abstractmethod
    def create(self, *args, **kwargs) -> T:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    def find(self, *args, **kwargs) -> List[T]:
        raise NotImplementedError()

    @abstractmethod
    def find_one(self, *args, **kwargs) -> Optional[T]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, *args, **kwargs) -> T:
        raise NotImplementedError()

    @abstractmethod
    def update(self, *args, **kwargs) -> T:
        raise NotImplementedError()
