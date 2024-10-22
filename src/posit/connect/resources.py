import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Type, TypeVar

import requests

from .urls import Url


@dataclass(frozen=True)
class ResourceParameters:
    """Shared parameter object for resources.

    Attributes
    ----------
    session: requests.Session
    url: str
        The Connect API base URL (e.g., https://connect.example.com/__api__)
    """

    session: requests.Session
    url: Url


class Resource(dict):
    def __init__(self, /, params: ResourceParameters, **kwargs):
        self.params = params
        super().__init__(**kwargs)

    def __getattr__(self, name):
        if name in self:
            warnings.warn(
                f"Accessing the field '{name}' via attribute is deprecated and will be removed in v1.0.0. "
                f"Please use __getitem__ (e.g., {self.__class__.__name__.lower()}['{name}']) for field access instead.",
                DeprecationWarning,
            )
            return self[name]
        return None

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params


T = TypeVar("T", bound=Resource)


class FinderMethods(
    Generic[T],
    ABC,
    Resources,
):
    def __init__(self, cls: Type[T], params, endpoint):
        super().__init__(params)
        self._cls = cls
        self._endpoint = endpoint

    @property
    @abstractmethod
    def _data(self) -> List[T]:
        raise NotImplementedError()

    def find(self, uid):
        endpoint = self._endpoint + str(uid)
        response = self.params.session.get(endpoint)
        result = response.json()
        return self._cls(self.params, endpoint=self._endpoint, **result)

    def find_by(self, **conditions: Any) -> Optional[T]:
        """Finds the first record matching the specified conditions.

        There is no implied ordering so if order matters, you should specify it yourself.

        Returns
        -------
        Optional[T]
        """
        return next((v for v in self._data if v.items() >= conditions.items()), None)
