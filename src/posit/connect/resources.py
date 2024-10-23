import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar, overload

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
            )
            return self[name]
        return None

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params


class Active(Resource):
    """
    A base class representing an active resource.

    Extends the `Resource` class and provides additional functionality for via the session context and an optional parent resource.

    Parameters
    ----------
    ctx : Context
        The context object containing the session and URL for API interactions.
    parent : Optional[Active], optional
        An optional parent resource that establishes a hierarchical relationship, by default None.
    **kwargs : dict
        Additional keyword arguments passed to the parent `Resource` class.

    Attributes
    ----------
    _ctx : Context
        The session context.
    _parent : Optional[Active]
        The parent resource, if provided, which establishes a hierarchical relationship.
    """

    def __init__(self, ctx: Context, parent: Optional["Active"] = None, **kwargs):
        """
        Initialize the `Active` resource.

        Parameters
        ----------
        ctx : Context
            The context object containing session and URL for API interactions.
        parent : Optional[Active], optional
            An optional parent resource to establish a hierarchical relationship, by default None.
        **kwargs : dict
            Additional keyword arguments passed to the parent `Resource` class.
        """
        params = ResourceParameters(ctx.session, ctx.url)
        super().__init__(params, **kwargs)
        self._ctx = ctx
        self._parent = parent


T_co = TypeVar("T_co", bound="Active", covariant=True)
"""A covariant type variable that is bound to the `Active` class, meaning that `T_co` must be or derive from `Active`."""


class ActiveSequence(ABC, Generic[T_co], Sequence[T_co]):
    """
    A sequence abstraction for any HTTP GET endpoint that returns a collection.

    It lazily fetches data on demand, caches the results, and allows for standard sequence operations like indexing and slicing.

    Parameters
    ----------
    cls : Type[T_co]
        The class used to represent each item in the sequence.
    ctx : Context
        The context object that holds the HTTP session used for sending the GET request.
    parent : Optional[Active], optional
        An optional parent resource to establish a nested relationship, by default None.

    Attributes
    ----------
    _cls : Type[T_co]
        The class used to instantiate each item in the sequence.
    _ctx : Context
        The context containing the HTTP session used to interact with the API.
    _parent : Optional[Active]
        Optional parent resource for maintaining hierarchical relationships.
    _cache : Optional[List[T_co]]
        Cached list of items returned from the API. Set to None initially, and populated after the first request.

    Abstract Properties
    -------------------
    _endpoint : str
        The API endpoint URL for the HTTP GET request. Subclasses are required to implement this property.

    Methods
    -------
    _data() -> List[T_co]
        Fetch and cache the data from the API. This method sends a GET request to `_endpoint`, parses the
        response as JSON, and instantiates each item using `cls`.

    __getitem__(index) -> Union[T_co, Sequence[T_co]]
        Retrieve an item or slice from the sequence. Indexing follows the standard Python sequence semantics.

    __len__() -> int
        Return the number of items in the sequence.

    __str__() -> str
        Return a string representation of the cached data.

    __repr__() -> str
        Return a detailed string representation of the cached data.

    reload() -> ActiveSequence
        Clear the cache and mark to reload the data from the API on the next operation.
    """

    def __init__(self, cls: Type[T_co], ctx: Context, parent: Optional[Active] = None):
        super().__init__()
        self._cls = cls
        self._ctx = ctx
        self._parent = parent
        self._cache = None

    @property
    @abstractmethod
    def _endpoint(self) -> str:
        """
        Abstract property to define the endpoint URL for the GET request.

        Subclasses must implement this property to return the API endpoint URL that will
        be queried to fetch the data.

        Returns
        -------
        str
            The API endpoint URL.
        """
        raise NotImplementedError()

    @property
    def _data(self) -> List[T_co]:
        """
        Fetch and cache the data from the API.

        This method sends a GET request to the `_endpoint` and parses the response as a list of JSON objects.
        Each JSON object is used to instantiate an item of type `T_co` using the class specified by `_cls`.
        The results are cached after the first request and reused for subsequent access unless reloaded.

        Returns
        -------
        List[T_co]
            A list of items of type `T_co` representing the fetched data.
        """
        if self._cache:
            return self._cache

        response = self._ctx.session.get(self._endpoint)
        results = response.json()
        self._cache = [self._cls(self._ctx, self._parent, **result) for result in results]
        return self._cache

    @overload
    def __getitem__(self, index: int) -> T_co: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[T_co]: ...

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def reload(self) -> "ActiveSequence":
        """
        Clear the cache and reload the data from the API on the next access.

        Returns
        -------
        ActiveSequence
            The current instance with cleared cache, ready to reload data on next access.
        """
        self._cache = None
        return self


class ActiveFinderMethods(ActiveSequence[T_co], ABC, Generic[T_co]):
    """
    Finder methods.

    Provides various finder methods for locating records in any endpoint supporting HTTP GET requests.

    Attributes
    ----------
    _uid : str
        The default field name used to uniquely identify records. Defaults to 'guid'.

    Methods
    -------
    find(uid) -> T_co
        Finds and returns a record by its unique identifier (`uid`). If a cached result exists, it searches within the cache;
        otherwise, it makes a GET request to retrieve the data from the endpoint.

    find_by(**conditions: Any) -> Optional[T_co]
        Finds the first record that matches the provided conditions. If no record is found, returns None.
    """

    _uid: str = "guid"
    """The default field name used to uniquely identify records. Defaults to 'guid'."""

    def find(self, uid) -> T_co:
        """
        Find a record by its unique identifier.

        Fetches a record either by searching the cache or by making a GET request to the endpoint.

        Parameters
        ----------
        uid : Any
            The unique identifier of the record.

        Returns
        -------
        T_co

        Raises
        ------
        ValueError
            If no record is found.
        """
        if self._cache:
            conditions = {self._uid: uid}
            result = self.find_by(**conditions)
        else:
            endpoint = self._endpoint + uid
            response = self._ctx.session.get(endpoint)
            result = response.json()
            result = self._cls(self._ctx, self._parent, **result)

        if not result:
            raise ValueError(f"Failed to find instance where {self._uid} is '{uid}'")

        return result

    def find_by(self, **conditions: Any) -> Optional[T_co]:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Any

        Returns
        -------
        Optional[T_co]
            The first record matching the conditions, or `None` if no match is found.
        """
        return next((v for v in self._data if v.items() >= conditions.items()), None)
