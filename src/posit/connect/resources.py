from __future__ import annotations

import posixpath
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import islice
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    TypeVar,
    overload,
)

if TYPE_CHECKING:
    import requests

    from .context import Context
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
                stacklevel=2,
            )
            return self[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params


class Active(ABC, Resource):
    def __init__(self, ctx: Context, path: str, /, **attributes):
        """A dict abstraction for any HTTP endpoint that returns a singular resource.

        Extends the `Resource` class and provides additional functionality for via the session context and an optional parent resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the resource endpoint
        **attributes : dict
            Resource attributes passed
        """
        params = ResourceParameters(ctx.session, ctx.url)
        super().__init__(params, **attributes)
        self._ctx = ctx
        self._path = path


T = TypeVar("T", bound="Active")
"""A type variable that is bound to the `Active` class"""


class ActiveSequence(ABC, Generic[T], Sequence[T]):
    """A sequence for any HTTP GET endpoint that returns a collection."""

    _cache: Optional[List[T]]

    def __init__(self, ctx: Context, path: str, uid: str = "guid"):
        """A sequence abstraction for any HTTP GET endpoint that returns a collection.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the collection endpoint
        uid : str, optional
            The field name of that uniquely identifiers an instance of T, by default "guid"
        """
        super().__init__()
        self._ctx = ctx
        self._path = path
        self._uid = uid

    @abstractmethod
    def _create_instance(self, path: str, /, **kwargs: Any) -> T:
        """Create an instance of 'T'."""
        raise NotImplementedError()

    def fetch(self, **conditions) -> Iterable[T]:
        """Fetch the collection.

        Fetches the collection directly from Connect. This operation does not effect the cache state.

        Returns
        -------
        List[T]
        """
        endpoint = self._ctx.url + self._path
        response = self._ctx.session.get(endpoint, params=conditions)
        results = response.json()
        return [self._to_instance(result) for result in results]

    def _to_instance(self, result: dict) -> T:
        """Converts a result into an instance of T."""
        uid = result[self._uid]
        path = posixpath.join(self._path, uid)
        return self._create_instance(path, **result)

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index) -> Sequence[T] | T:
        data = self.fetch()

        if isinstance(index, int):
            if index < 0:
                # Handle negative indexing
                data = list(data)
                return data[index]
            for i, value in enumerate(data):
                if i == index:
                    return value
            raise KeyError(f"Index {index} is out of range.")

        if isinstance(index, slice):
            # Handle slicing with islice
            start = index.start or 0
            stop = index.stop
            step = index.step or 1
            if step == 0:
                raise ValueError("slice step cannot be zero")
            return [
                value
                for i, value in enumerate(islice(data, start, stop))
                if (i + start) % step == 0
            ]

        raise TypeError(f"Index must be int or slice, not {type(index).__name__}.")

    def __iter__(self):
        return iter(self.fetch())

    def __len__(self) -> int:
        return len(list(self.fetch()))

    def __str__(self) -> str:
        return str(list(self.fetch()))

    def __repr__(self) -> str:
        return repr(list(self.fetch()))


class ActiveFinderMethods(ActiveSequence[T], ABC):
    """Finder methods.

    Provides various finder methods for locating records in any endpoint supporting HTTP GET requests.
    """

    def find(self, uid) -> T:
        """
        Find a record by its unique identifier.

        Fetches the record from Connect by it's identifier.

        Parameters
        ----------
        uid : Any
            The unique identifier of the record.

        Returns
        -------
        T
        """
        endpoint = self._ctx.url + self._path + uid
        response = self._ctx.session.get(endpoint)
        result = response.json()
        return self._to_instance(result)

    def find_by(self, **conditions) -> Optional[T]:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Any

        Returns
        -------
        Optional[T]
            The first record matching the conditions, or `None` if no match is found.
        """
        collection = self.fetch(**conditions)
        return next((v for v in collection if v.items() >= conditions.items()), None)
