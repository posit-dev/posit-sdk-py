import warnings

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar


T = TypeVar("T")


class Resource(ABC, dict):
    def __getitem__(self, key):
        warnings.warn(
            f"__getitem__ for '{key}' does not support backwards compatibility. Consider using field based access instead: 'instance.{key}'",
            FutureWarning,
        )
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        warnings.warn(
            f"__setitem__ for '{key}' does not support backwards compatibility. Consider using field based access instead: 'instance.{key} = {value}",
            FutureWarning,
        )
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        warnings.warn(
            f"__delitem__ for '{key}' does not support backwards compatibility. Consider using field based access instead: 'del instance.{key}'",
            FutureWarning,
        )
        return super().__delitem__(key)


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
