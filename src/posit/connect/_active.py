# TODO-barret-future; Piecemeal migrate everything to leverage `ApiDictEndpoint` and `ApiListEndpoint` classes.
# TODO-barret-future; Merge any trailing behavior of `Active` or `ActiveList` into the new classes.

from __future__ import annotations

import posixpath
from abc import ABC, abstractmethod
from collections.abc import Mapping as Mapping_abc
from collections.abc import Sequence as Sequence_abc
from typing import (
    Any,
    Generator,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    cast,
    overload,
)

from ._api_call import ApiCallMixin, ContextP, get_api
from ._json import Jsonifiable, JsonifiableDict, JsonifiableList, ResponseAttrs
from ._types_context import ContextT

# Design Notes:
# * Perform API calls on property retrieval. e.g. `my_content.repository`
# * Dictionary endpoints: Retrieve all attributes during init unless provided
# * List endpoints: Do not retrieve until `.fetch()` is called directly. Avoids cache invalidation issues.
#   * While slower, all ApiListEndpoint helper methods should `.fetch()` on demand.
# * Only expose methods needed for `ReadOnlyDict`.
#   * Ex: When inheriting from `dict`, we'd need to shut down `update`, `pop`, etc.
# * Use `ApiContextProtocol` to ensure that the class has the necessary attributes for API calls.
#    * Inherit from `ApiCallMixin` to add all helper methods for API calls.
# * Classes should write the `path` only once within its init method.
#    * Through regular interactions, the path should only be written once.

# When making a new class,
# * Use a class to define the parameters and their types
#    * If attaching the type info class to the parent class, start with `_`. E.g.: `ContentItemRepository._Attrs`
# * Document all attributes like normal
#    * When the time comes that there are multiple attribute types, we can use overloads with full documentation and unpacking of type info class for each overload method.
# * Inherit from `ApiDictEndpoint` or `ApiListEndpoint` as needed
#    * Init signature should be `def __init__(self, ctx: Context, path: str, /, **attrs: Jsonifiable) -> None:`


ReadOnlyDictT = TypeVar("ReadOnlyDictT", bound="ReadOnlyDict")
"""A type variable that is bound to the `Active` class"""
ResourceDictT = TypeVar("ResourceDictT", bound="ResourceDict")
"""A type variable that is bound to the `ResourceDict` class"""


# This class should not have typing about the class keys as that would fix the class's typing. If
# for some reason, we _know_ the keys are fixed (as we've moved on to a higher version), we can add
# `Generic[AttrsT]` to the class.
class ReadOnlyDict(Mapping_abc):
    _dict: ResponseAttrs
    """Read only dictionary."""

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

    def __len__(self) -> int:
        return self._dict.__len__()

    def __iter__(self):
        return self._dict.__iter__()

    def __contains__(self, key: object) -> bool:
        return self._dict.__contains__(key)

    def __repr__(self) -> str:
        return repr(self._dict)

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

    def _get_api(self, *path) -> JsonifiableDict | None:
        super()._get_api(*path)

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


class ReadOnlySequence(Sequence_abc[ResourceDictT]):
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
        return len(self._data)

    @overload
    def __getitem__(self, index: int) -> ResourceDictT: ...

    @overload
    def __getitem__(self, index: slice) -> Tuple[ResourceDictT, ...]: ...

    def __getitem__(self, index: int | slice) -> ResourceDictT | Tuple[ResourceDictT, ...]:
        return self._data[index]

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

    # def count(self, value: object) -> int:
    #     return self._data.count(value)

    # def index(self, value: object, start: int = 0, stop: int = 9223372036854775807) -> int:
    #     return self._data.index(value, start, stop)

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

    # @overload
    # def __getitem__(self, index: int) -> T: ...

    # @overload
    # def __getitem__(self, index: slice) -> tuple[T, ...]: ...

    # def __getitem__(self, index):
    #     return self[index]

    # def __len__(self) -> int:
    #     return len(self._data)

    # def __iter__(self):
    #     return iter(self._data)

    # def __str__(self) -> str:
    #     return str(self._data)

    # def __repr__(self) -> str:
    #     return repr(self._data)


# class ActiveSequenceP(  # pyright: ignore[reportInvalidTypeVarUse]
#     Generic[ResourceDictT, ContextT],
#     Protocol,
# ):
#     _ctx: ContextT
#     _path: str

#     def _get_api(self, *path) -> Jsonifiable | None: ...
#     def _to_instance(self, result: dict) -> ResourceDictT: ...
#     def _get_data(self, **conditions: object) -> Generator[ResourceDictT, None, None]: ...


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


# class ApiListEndpoint(ApiCallMixin, Generic[ReadOnlyDictT], ABC, object):
#     """A HTTP GET endpoint that can fetch a collection."""

#     def __init__(self, *, ctx: Context, path: str, uid_key: str = "guid") -> None:
#         """A sequence abstraction for any HTTP GET endpoint that returns a collection.

#         Parameters
#         ----------
#         ctx : Context
#             The context object containing the session and URL for API interactions.
#         path : str
#             The HTTP path component for the collection endpoint
#         uid_key : str, optional
#             The field name of that uniquely identifiers an instance of T, by default "guid"
#         """
#         super().__init__()
#         self._ctx = ctx
#         self._path = path
#         self._uid_key = uid_key

#     @abstractmethod
#     def _create_instance(self, path: str, /, **kwargs: Any) -> ReadOnlyDictT:
#         """Create an instance of 'ReadOnlyDictT'."""
#         raise NotImplementedError()

#     def fetch(self) -> Generator[ReadOnlyDictT, None, None]:
#         """Fetch the collection.

#         Fetches the collection directly from Connect. This operation does not effect the cache state.

#         Returns
#         -------
#         List[ReadOnlyDictT]
#         """
#         results: Jsonifiable = self._get_api()
#         results_list = cast(list[JsonifiableDict], results)
#         for result in results_list:
#             yield self._to_instance(result)

#     def __iter__(self) -> Generator[ReadOnlyDictT, None, None]:
#         return self.fetch()

#     def _to_instance(self, result: dict) -> ReadOnlyDictT:
#         """Converts a result into an instance of ReadOnlyDictT."""
#         uid = result[self._uid_key]
#         path = posixpath.join(self._path, uid)
#         return self._create_instance(path, **result)

#     @overload
#     def __getitem__(self, index: int) -> ReadOnlyDictT: ...

#     @overload
#     def __getitem__(self, index: slice) -> Generator[ReadOnlyDictT, None, None]: ...

#     def __getitem__(
#         self, index: int | slice
#     ) -> ReadOnlyDictT | Generator[ReadOnlyDictT, None, None]:
#         if isinstance(index, slice):
#             results = itertools.islice(self.fetch(), index.start, index.stop, index.step)
#             for result in results:
#                 yield result
#         else:
#             return list(itertools.islice(self.fetch(), index, index + 1))[0]

#     # def __len__(self) -> int:
#     #     return len(self.fetch())

#     def __str__(self) -> str:
#         return self.__repr__()

#     def __repr__(self) -> str:
#         # Jobs - 123 items
#         return repr(
#             f"{self.__class__.__name__} - { len(list(self.fetch())) } items - {self._path}"
#         )

#     def find(self, uid: str) -> ReadOnlyDictT | None:
#         """
#         Find a record by its unique identifier.

#         Fetches the record from Connect by it's identifier.

#         Parameters
#         ----------
#         uid : str
#             The unique identifier of the record.

#         Returns
#         -------
#         :
#             Single instance of T if found, else None
#         """
#         result: Jsonifiable = self._get_api(uid)
#         result_obj = cast(JsonifiableDict, result)

#         return self._to_instance(result_obj)

#     def find_by(self, **conditions: Any) -> ReadOnlyDictT | None:
#         """
#         Find the first record matching the specified conditions.

#         There is no implied ordering, so if order matters, you should specify it yourself.

#         Parameters
#         ----------
#         **conditions : Any

#         Returns
#         -------
#         ReadOnlyDictT
#             The first record matching the conditions, or `None` if no match is found.
#         """
#         results = self.fetch()

#         conditions_items = conditions.items()

#         # Get the first item of the generator that matches the conditions
#         # If no item is found, return None
#         return next(
#             (
#                 # Return result
#                 result
#                 # Iterate through `results` generator
#                 for result in results
#                 # If all `conditions`'s key/values are found in `result`'s key/values...
#                 if result.items() >= conditions_items
#             ),
#             None,
#         )
