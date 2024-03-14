from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from typing import Generic, List, Optional, TypeVar


T = TypeVar("T")


@dataclass
class Resource(ABC):
    def __init__(self, **kwargs) -> None:
        mapping = {self._compatibility.get(k, k): v for k, v in kwargs.items()}
        for prop in fields(self):
            setattr(
                self, prop.name, mapping.get(prop.name, kwargs.get(prop.name, None))
            )

    @property
    def _compatibility(self):
        return {}

    def asdict(self) -> dict:
        return asdict(self)


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
