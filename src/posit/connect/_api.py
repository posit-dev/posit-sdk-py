from __future__ import annotations

import posixpath
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, cast

from ._json import Jsonifiable, JsonifiableDict, ResponseAttrs

if TYPE_CHECKING:
    from .context import Context

# Design Notes:
# * Perform API calls on property retrieval
# * Dictionary endpoints: Retrieve all attributes during init unless provided
# * List endpoints: Do not retrieve until `.fetch()` is called directly. Avoids cache invalidation issues.


class ApiContextProtocol(Protocol):
    _ctx: Context
    _path: str


# TODO-future; Add type hints for the ReadOnlyDict class
# ArgsT = TypeVar("ArgsT", bound="ResponseAttrs")


class ReadOnlyDict(
    # Generic[ArgsT],
):
    # _attrs: ArgsT
    _attrs: ResponseAttrs
    """Resource attributes passed."""
    _attrs_locked: bool
    """Semaphore for locking the resource attributes. Deters setting new attributes after initialization."""

    def __init__(self, attrs: ResponseAttrs) -> None:
        """
        A read-only dict abstraction for any HTTP endpoint that returns a singular resource.

        Parameters
        ----------
        attrs : dict
            Resource attributes passed
        """
        self._attrs = attrs
        self._attrs_locked = True

    def get(self, key: str, default: Any = None) -> Any:
        return self._attrs.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._attrs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if self._attrs_locked:
            raise AttributeError(
                "Resource attributes are locked. "
                "To retrieve updated values, please retrieve the parent object again."
            )
        self._attrs[key] = value

    def _set_attrs(self, **kwargs: Any) -> None:
        # Unlock
        self._attrs_locked = False
        # Set
        for key, value in kwargs.items():
            self._attrs[key] = value
        # Lock
        self._attrs_locked = True

    def __len__(self) -> int:
        return self._attrs.__len__()


class EndpointMixin(ApiContextProtocol):
    _ctx: Context
    """The context object containing the session and URL for API interactions."""
    _path: str
    """The HTTP path component for the resource endpoint."""

    def _endpoint(self, extra_endpoint: str = "") -> str:
        return self._ctx.url + self._path + extra_endpoint

    def _get_api(self, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(extra_endpoint))
        return response.json()

    def _delete_api(self, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(extra_endpoint))
        return response.json()

    def _patch_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.patch(self._endpoint(extra_endpoint), json=json)
        return response.json()

    def _put_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.put(self._endpoint(extra_endpoint), json=json)
        return response.json()


class ApiDictEndpoint(EndpointMixin, ReadOnlyDict):
    def _get_api(self, *, extra_endpoint: str = "") -> JsonifiableDict | None:
        super()._get_api(extra_endpoint=extra_endpoint)

    def __init__(self, *, ctx: Context, path: str, attrs: ResponseAttrs | None = None) -> None:
        """
        A dict abstraction for any HTTP endpoint that returns a singular resource.

        Adds helper methods to interact with the API with reduced boilerplate.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the resource endpoint
        attrs : dict
            Resource attributes passed
        """
        super().__init__(attrs or {})
        self._ctx = ctx
        self._path = path

        # If attrs is None, Fetch the API and set the attributes
        if attrs is None:
            init_attrs = self._get_api() or {}
            self._set_attrs(**init_attrs)


T = TypeVar("T", bound="ReadOnlyDict")
"""A type variable that is bound to the `Active` class"""


class ApiListEndpoint(EndpointMixin, Generic[T], ABC, object):
    """A tuple for any HTTP GET endpoint that returns a collection."""

    _data: tuple[T, ...]

    def _get_api(self, *, extra_endpoint: str = "") -> tuple[JsonifiableDict, ...]:
        vals: Jsonifiable = super()._get_api(extra_endpoint=extra_endpoint)
        return cast(tuple[JsonifiableDict, ...], vals)

    def __init__(self, *, ctx: Context, path: str, uid_key: str = "guid") -> None:
        """A sequence abstraction for any HTTP GET endpoint that returns a collection.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the collection endpoint
        uid_key : str, optional
            The field name of that uniquely identifiers an instance of T, by default "guid"
        """
        super().__init__()
        self._ctx = ctx
        self._path = path
        self._uid_key = uid_key
        # # TODO-barret; Key component! Fetch the data immediately?
        # self._data = self._fetch_data()

    @abstractmethod
    def _create_instance(self, path: str, /, **kwargs: Any) -> T:
        """Create an instance of 'T'."""
        raise NotImplementedError()

    def fetch(self) -> tuple[T, ...]:
        """Fetch the collection.

        Fetches the collection directly from Connect. This operation does not effect the cache state.

        Returns
        -------
        List[T]
        """
        results = self._get_api()
        return tuple(self._to_instance(result) for result in results)

    def __iter__(self) -> tuple[T, ...]:
        return self.fetch()

    def _to_instance(self, result: dict) -> T:
        """Converts a result into an instance of T."""
        uid = result[self._uid_key]
        path = posixpath.join(self._path, uid)
        return self._create_instance(path, **result)

    # @overload
    # def __getitem__(self, index: int) -> T: ...

    # @overload
    # def __getitem__(self, index: slice) -> Sequence[T]: ...

    # def __getitem__(self, index: int | slice) -> T | Sequence[T]:
    #     return self.fetch()[index]

    # def __len__(self) -> int:
    #     return len(self.fetch())

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        # Jobs - 123 items
        return repr(f"{self.__class__.__name__} - { len(self.fetch()) } items")

    def find(self, uid: str) -> T | None:
        """
        Find a record by its unique identifier.

        Fetches the record from Connect by it's identifier.

        Parameters
        ----------
        uid : str
            The unique identifier of the record.

        Returns
        -------
        :
            Single instance of T if found, else None
        """
        return self.find_by(**{self._uid_key: uid})

    def find_by(self, **conditions: Any) -> T | None:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Any

        Returns
        -------
        T
            The first record matching the conditions, or `None` if no match is found.
        """
        results = self.fetch()
        for item in results:
            if obj_has_attrs(item, conditions):
                return item
        return None


def obj_has_attrs(obj: ReadOnlyDict, attrs: dict[str, Any]) -> bool:
    for attr_key, attr_val in attrs.items():
        if not hasattr(obj, attr_key):
            return False
        obj_val = getattr(obj, attr_key)
        if obj_val != attr_val:
            return False
    return True
