import posixpath
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar, overload

import requests

from posit.connect.context import Context

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


T = TypeVar("T", bound="Active", covariant=True)


class Active(Resource):
    def __init__(self, ctx: Context, parent: Optional["Active"] = None, **kwargs):
        params = ResourceParameters(ctx.session, ctx.url)
        super().__init__(params, **kwargs)
        self._ctx = ctx
        self._parent = parent


class ActiveReader(ABC, Generic[T], Sequence[T]):
    def __init__(self, cls: Type[T], ctx: Context, parent: Optional[Active] = None):
        super().__init__()
        self._cls = cls
        self._ctx = ctx
        self._parent = parent
        self._cache = None

    @property
    @abstractmethod
    def _endpoint(self) -> str:
        raise NotImplementedError()

    @property
    def _data(self) -> List[T]:
        if self._cache:
            return self._cache

        response = self._ctx.session.get(self._endpoint)
        results = response.json()
        self._cache = [self._cls(self._ctx, self._parent, **result) for result in results]
        return self._cache

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index):
        """Retrieve an item or slice from the sequence."""
        return self._data[index]

    def __len__(self):
        """Return the length of the sequence."""
        return len(self._data)

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)

    def reload(self):
        self._cache = None
        return self


class ActiveFinderMethods(ActiveReader[T], ABC, Generic[T]):
    _uid: str = "guid"

    def find(self, uid) -> T:
        if self._cache:
            conditions = {self._uid: uid}
            result = self.find_by(**conditions)
        else:
            endpoint = posixpath.join(self._endpoint + uid)
            response = self._ctx.session.get(endpoint)
            result = response.json()
            result = self._cls(self._ctx, self._parent, **result)

        if not result:
            raise ValueError(f"Failed to find instance where {self._uid} is '{uid}'")

        return result

    def find_by(self, **conditions: Any) -> Optional[T]:
        """Finds the first record matching the specified conditions.

        There is no implied ordering so if order matters, you should specify it yourself.

        Returns
        -------
        Optional[T]
        """
        return next((v for v in self._data if v.items() >= conditions.items()), None)
