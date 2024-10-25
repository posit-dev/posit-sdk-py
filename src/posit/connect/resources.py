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
    def __init__(self, ctx: Context, **kwargs):
        """A base class representing an active resource.

        Extends the `Resource` class and provides additional functionality for via the session context and an optional parent resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        **kwargs : dict
            Additional keyword arguments passed to the parent `Resource` class.
        """
        params = ResourceParameters(ctx.session, ctx.url)
        super().__init__(params, **kwargs)
        self._ctx = ctx


T = TypeVar("T", bound="Active")
"""A type variable that is bound to the `Active` class"""


class ActiveSequence(ABC, Generic[T], Sequence[T]):
    def __init__(self, ctx: Context, base: str, name: str, uid="guid"):
        """A sequence abstraction for any HTTP GET endpoint that returns a collection.

        It lazily fetches data on demand, caches the results, and allows for standard sequence operations like indexing and slicing.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        base : str
            The base HTTP path for the collection endpoint
        name : str
            The collection name
        uid : str, optional
            The field name used to uniquely identify records, by default "guid"

        Attributes
        ----------
        _ctx : Context
            The context object containing the session and URL for API interactions
        _path : str
            The HTTP path for the collection endpoint.
        _endpoint : Url
            The HTTP URL for the collection endpoint.
        _uid : str
            The default field name used to uniquely identify records.
        _cache: Optional[List[T]]
        """
        super().__init__()
        self._ctx = ctx
        self._path: str = posixpath.join(base, name)
        self._endpoint: Url = ctx.url + self._path
        self._uid: str = uid
        self._cache: Optional[List[T]] = None

    @property
    def _data(self) -> List[T]:
        """
        Fetch and cache the data from the API.

        This method sends a GET request to the `_endpoint` and parses the response as a list of JSON objects.
        Each JSON object is used to instantiate an item of type `T` using the class specified by `_cls`.
        The results are cached after the first request and reused for subsequent access unless reloaded.

        Returns
        -------
        List[T]
            A list of items of type `T` representing the fetched data.
        """
        if self._cache:
            return self._cache

        response = self._ctx.session.get(self._endpoint)
        results = response.json()

        self._cache = []
        for result in results:
            uid = result[self._uid]
            instance = self._create_instance(self._path, uid, **result)
            self._cache.append(instance)

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

    @abstractmethod
    def _create_instance(self, base: str, uid: str, /, **kwargs: Any) -> T:
        """Create an instance of 'T'.

        Returns
        -------
        T
        """
        raise NotImplementedError()

    def reload(self) -> Self:
        """
        Clear the cache and reload the data from the API on the next access.

        Returns
        -------
        ActiveSequence
            The current instance with cleared cache, ready to reload data on next access.
        """
        self._cache = None
        return self


class ActiveFinderMethods(ActiveSequence[T], ABC):
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
        if self._cache:
            # Check if the record already exists in the cache.
            # It is assumed that local cache scan is faster than an additional HTTP request.
            conditions = {self._uid: uid}
            result = self.find_by(**conditions)
            if result:
                return result

        endpoint = self._endpoint + uid
        response = self._ctx.session.get(endpoint)
        result = response.json()
        result = self._create_instance(self._path, uid, **result)

        # Invalidate the cache.
        # It is assumed that the cache is stale since a record exists on the server and not in the cache.
        self._cache = None

        return result

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
