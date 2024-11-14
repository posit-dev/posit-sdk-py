# ################################
# Design Notes
#
# Please see the design notes in `src/posit/connect/README.md` for example usages.
# ################################

from __future__ import annotations

import posixpath
from abc import ABC, abstractmethod
from collections.abc import Mapping as Mapping_abc
from typing import (
    Any,
    Generator,
    Iterator,
    Optional,
    SupportsIndex,
    Tuple,
    TypeVar,
    cast,
    overload,
)

from ._api_call import ApiCallMixin, ContextP, get_api
from ._json import Jsonifiable, JsonifiableList, ResponseAttrs
from ._types_context import ContextT

ReadOnlyDictT = TypeVar("ReadOnlyDictT", bound="ReadOnlyDict")
"""A type variable that is bound to the `Active` class"""
ResourceDictT = TypeVar("ResourceDictT", bound="ResourceDict")
"""A type variable that is bound to the `ResourceDict` class"""


# This class should not have typing about the class keys as that would fix the class's typing. If
# for some reason, we _know_ the keys are fixed (as we've moved on to a higher version), we can add
# `Generic[AttrsT]` to the class.
class ReadOnlyDict(Mapping_abc):
    """A read-only dict abstraction."""

    _dict: ResponseAttrs
    """Data dictionary."""

    def __init__(self, **kwargs: Any) -> None:
        """
        A read-only dict abstraction for any HTTP endpoint that returns a singular resource.

        Parameters
        ----------
        **kwargs : Any
            Values to be stored
        """
        super().__init__()
        self._dict = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        return self._dict.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._dict[key]

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError(
            "Attributes are locked. "
            "To retrieve updated values, please retrieve the parent object again."
        )

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError(
            "Attributes are locked. "
            "To retrieve updated values, please retrieve the parent object again."
        )

    # * Only expose methods needed for `ReadOnlyDict`.
    #   * Ex: If inheriting from `dict`, we would need to shut down `update`, `pop`, etc.

    def __len__(self) -> int:
        return self._dict.__len__()

    def __iter__(self):
        return self._dict.__iter__()

    def __contains__(self, key: object) -> bool:
        return self._dict.__contains__(key)

    def __repr__(self) -> str:
        if hasattr(self, "_dict"):
            return repr(self._dict)
        return object.__repr__(self)

    def __str__(self) -> str:
        return str(self._dict)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()


class ResourceDict(ReadOnlyDict, ContextP[ContextT]):
    """An abstraction to contain the context and read-only information."""

    _ctx: ContextT
    """The context object containing the session and URL for API interactions."""

    def __init__(
        self,
        ctx: ContextT,
        /,
        **kwargs: Any,
    ) -> None:
        """
        A dict abstraction for any HTTP endpoint that returns a singular resource.

        Adds helper methods to interact with the API with reduced boilerplate.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        **kwargs : Any
            Values to be stored
        """
        super().__init__(**kwargs)
        self._ctx = ctx


class ActiveDict(ApiCallMixin, ResourceDict[ContextT]):
    """A dict abstraction for any HTTP endpoint that returns a singular resource."""

    _ctx: ContextT
    """The context object containing the session and URL for API interactions."""
    _path: str
    """The HTTP path component for the resource endpoint."""

    def __init__(
        self,
        ctx: ContextT,
        path: str,
        get_data: Optional[bool] = None,
        /,
        **kwargs: Any,
    ) -> None:
        """
        A dict abstraction for any HTTP endpoint that returns a singular resource.

        Adds helper methods to interact with the API with reduced boilerplate.

        Parameters
        ----------
        ctx : ContextT
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the resource endpoint
        get_data : Optional[bool]
            If `True`, fetch the API and set the attributes from the response. If `False`, only set
            the provided attributes. If `None` [default], fetch the API if no attributes are
            provided.
        **kwargs : Any
            Resource attributes passed
        """
        # If no attributes are provided, fetch the API and set the attributes from the response
        if get_data is None:
            get_data = len(kwargs) == 0

        # If we should get data, fetch the API and set the attributes from the response
        if get_data:
            init_kwargs: Jsonifiable = get_api(ctx, path)
            init_kwargs_dict = cast(ResponseAttrs, init_kwargs)
            # Overwrite the initial attributes with `kwargs`: e.g. {'key': value} | {'content_guid': '123'}
            init_kwargs_dict.update(kwargs)
            kwargs = init_kwargs_dict

        super().__init__(ctx, **kwargs)
        self._path = path


class ReadOnlySequence(Tuple[ResourceDictT, ...]):
    """Read only Sequence."""

    _data: Tuple[ResourceDictT, ...]

    def _set_data(self, data: Tuple[ResourceDictT, ...]) -> None:
        self._data = data

    def __init__(self, *args: ResourceDictT) -> None:
        """
        A read-only sequence abstraction.

        Parameters
        ----------
        *args : Any
            Values to be stored
        """
        super().__init__()
        self._data = args

    def __len__(self) -> int:
        return len(tuple(self._data))

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> ResourceDictT: ...

    @overload
    def __getitem__(self, key: slice, /) -> tuple[ResourceDictT, ...]: ...

    def __getitem__(
        self,
        key: SupportsIndex | slice,
        /,
    ) -> ResourceDictT | tuple[ResourceDictT, ...]:
        return self._data[key]

    def __iter__(self) -> Iterator[ResourceDictT]:
        return iter(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return repr(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReadOnlySequence):
            return NotImplemented
        return self._data == other._data

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ReadOnlySequence):
            return NotImplemented
        return self._data != other._data

    def __setitem__(self, key: int, value: Any) -> None:
        raise NotImplementedError(
            "Values are locked. "
            "To retrieve updated values, please retrieve the parent object again."
        )

    def __delitem__(self, key: int) -> None:
        raise NotImplementedError(
            "Values are locked. "
            "To retrieve updated values, please retrieve the parent object again."
        )


class ResourceSequence(ReadOnlySequence[ResourceDictT], ContextP[ContextT]):
    """An abstraction to contain the context and read-only tuple-like information."""

    _ctx: ContextT
    """The context object containing the session and URL for API interactions."""

    def __init__(
        self,
        ctx: ContextT,
        /,
        *,
        arr: list[ResourceDictT] | tuple[ResourceDictT, ...],
    ) -> None:
        """
        A read-only sequence abstraction that is Context aware.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        *args : Any
            Values to be stored
        """
        super().__init__(*tuple(arr))
        self._ctx = ctx


class ActiveSequence(ApiCallMixin, ABC, ResourceSequence[ResourceDictT, ContextT]):
    """A read only sequence for any HTTP GET endpoint that returns a collection."""

    def __init__(
        self,
        ctx: ContextT,
        path: str,
        /,
        *,
        uid: str = "guid",
        # Named parameter to allow for future param expansion
        arr: Optional[tuple[ResourceDictT, ...]] = None,
        get_data: Optional[bool] = None,
    ):
        """
        A sequence abstraction for any HTTP GET endpoint that returns a collection.

        Parameters
        ----------
        ctx : ContextT
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the collection endpoint
        uid : str, optional
            The field name of that uniquely identifiers an instance of T, by default "guid"
        arr : tuple[ResourceDictT, ...], optional
            Values to be stored. If no values are given, they are retrieved from the API.
        get_data : Optional[bool]
            If `True`, fetch the API and set the `arr` from the response. If `False`, do not fetch
            any data for `arr`. If `None` [default], fetch data from the API if `arr` is `None`.

        """
        if get_data is None:
            get_data = arr is None
            arr = ()

        assert arr is not None

        super().__init__(ctx, arr=arr)
        self._path = path
        self._uid = uid

        # TODO-barret-future; Figure out how to better handle this. I'd like to call
        # self._get_data() here, but it hasn't been initialized yet.
        if get_data:
            self._set_data(tuple(self._get_data()))

    @abstractmethod
    def _create_instance(self, path: str, /, **kwargs: Any) -> ResourceDictT:
        """Create an instance of 'T'."""
        raise NotImplementedError()

    def _to_instance(self, result: dict) -> ResourceDictT:
        """Converts a result into an instance of T."""
        uid = result[self._uid]
        path = posixpath.join(self._path, uid)
        return self._create_instance(path, **result)

    # TODO-barret-future-q: Include params to `._get_api()`?
    def _get_data(self) -> Generator[ResourceDictT, None, None]:
        """Fetch the collection.

        Fetches the collection directly from Connect.

        Returns
        -------
        List[T]
        """
        results: Jsonifiable = self._get_api()
        results_list = cast(JsonifiableList, results)
        return (self._to_instance(result) for result in results_list)


class ActiveFinderSequence(ActiveSequence[ResourceDictT, ContextT]):
    """Finder methods.

    Provides various finder methods for locating records in any endpoint supporting HTTP GET requests.
    """

    def find(self, uid: str) -> ResourceDictT:
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
        self._get_api(uid)
        endpoint = self._ctx.url + self._path + uid
        response = self._ctx.session.get(endpoint)
        result = response.json()
        return self._to_instance(result)

    def find_by(
        self,
        **conditions: object,
    ) -> ResourceDictT | None:
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
        collection = self._get_data()
        conditions_items = conditions.items()

        # Get the first item of the generator that matches the conditions
        return next(
            (
                # Return result
                result
                # Iterate through `collection` list
                for result in collection
                # If all `conditions`'s key/values are found in `result`'s key/values...
                if result.items() >= conditions_items
            ),
            # If no item is found, return None
            None,
        )
