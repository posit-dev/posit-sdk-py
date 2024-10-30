import posixpath
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Sequence, TypeVar, overload

import requests
from typing_extensions import Self

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
            )
            return self[name]
        return None

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params


class Active(ABC, Resource):
    def __init__(self, ctx: Context, path: str, pathinfo: str = "", /, **attributes):
        """A dict abstraction for any HTTP endpoint that returns a singular resource.

        Extends the `Resource` class and provides additional functionality for via the session context and an optional parent resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the collection endpoint
        pathinfo : str
            The HTTP part of the path directed at a specific resource
        **attributes : dict
            Resource attributes passed

        Attributes
        ----------
        _ctx : Context
            The context object containing the session and URL for API interactions
        _path : str
            The HTTP path for the collection endpoint.
        """
        params = ResourceParameters(ctx.session, ctx.url)
        super().__init__(params, **attributes)
        self._ctx = ctx
        self._path = posixpath.join(path, pathinfo)


T = TypeVar("T", bound="Active")
"""A type variable that is bound to the `Active` class"""


class ActiveSequence(ABC, Generic[T], Sequence[T]):
    """A sequence for any HTTP endpoint that returns a collection."""

    def __init__(self, ctx: Context, path: str, pathinfo: str = "", uid: str = "guid"):
        """A sequence abstraction for any HTTP GET endpoint that returns a collection."""
        super().__init__()
        self._ctx: Context = ctx
        self._path: str = posixpath.join(path, pathinfo)
        self._uid: str = uid
        self._cache: Optional[List[T]] = None

    @abstractmethod
    def _create_instance(self, path: str, pathinfo: str, /, **kwargs: Any) -> T:
        """Create an instance of 'T'."""
        raise NotImplementedError()

    def cached(self) -> bool:
        """Returns True if the collection is cached.

        Returns
        -------
        bool

        See Also
        --------
        reload
        """
        return self._cache is not None

    def reload(self) -> Self:
        """Reloads the collection from Connect.

        Returns
        -------
        Self
        """
        self._cache = None
        return self

    def _fetch(self) -> List[T]:
        """Fetch the collection.

        Fetches the collection directly from Connect. This operation does not effect the cache state.

        Returns
        -------
        List[T]
        """
        endpoint = self._ctx.url + self._path
        response = self._ctx.session.get(endpoint)
        results = response.json()
        return [self._to_instance(result) for result in results]

    def _to_instance(self, result: dict) -> T:
        """Converts a result into an instance of T."""
        uid = result[self._uid]
        return self._create_instance(self._path, uid, **result)

    @property
    def _data(self) -> List[T]:
        """Get the collection.

        Fetches the collection from Connect and caches the result. Subsequent invocations return the cached results unless the cache is explicitly reset.

        Returns
        -------
        List[T]

        See Also
        --------
        cached
        reload
        """
        if self._cache is None:
            self._cache = self._fetch()
        return self._cache

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T]: ...

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)


class ActiveFinderMethods(ActiveSequence[T], ABC):
    """Finder methods.

    Provides various finder methods for locating records in any endpoint supporting HTTP GET requests.
    """

    def find(self, uid) -> T:
        """
        Find a record by its unique identifier.

        If the cache is already populated, it is checked first for matching record. If not, a conventional GET request is made to the Connect server.

        Parameters
        ----------
        uid : Any
            The unique identifier of the record.

        Returns
        -------
        T
        """
        if self.cached():
            conditions = {self._uid: uid}
            result = self.find_by(**conditions)
            if result:
                return result

        endpoint = self._ctx.url + self._path + uid
        response = self._ctx.session.get(endpoint)
        result = response.json()
        return self._to_instance(result)

    def find_by(self, **conditions: Any) -> Optional[T]:
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
        return next((v for v in self._data if v.items() >= conditions.items()), None)
