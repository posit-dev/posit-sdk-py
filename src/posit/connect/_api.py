# TODO-barret-future; Piecemeal migrate everything to leverage `ApiDictEndpoint` and `ApiListEndpoint` classes.
# TODO-barret-future; Merge any trailing behavior of `Active` or `ActiveList` into the new classes.

from __future__ import annotations

import itertools
import posixpath
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generator, Generic, Optional, TypeVar, cast, overload

from ._api_call import ApiCallMixin, get_api
from ._json import Jsonifiable, JsonifiableDict, ResponseAttrs

if TYPE_CHECKING:
    from .context import Context


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


# This class should not have typing about the class keys as that would fix the class's typing. If
# for some reason, we _know_ the keys are fixed (as we've moved on to a higher version), we can add
# `Generic[AttrsT]` to the class.
class ReadOnlyDict(Mapping):
    _attrs: ResponseAttrs
    """Resource attributes passed."""

    def __init__(self, attrs: ResponseAttrs) -> None:
        """
        A read-only dict abstraction for any HTTP endpoint that returns a singular resource.

        Parameters
        ----------
        attrs : dict
            Resource attributes passed
        """
        super().__init__()
        self._attrs = attrs

    def get(self, key: str, default: Any = None) -> Any:
        return self._attrs.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._attrs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError(
            "Resource attributes are locked. "
            "To retrieve updated values, please retrieve the parent object again."
        )

    def __len__(self) -> int:
        return self._attrs.__len__()

    def __iter__(self):
        return self._attrs.__iter__()

    def __contains__(self, key: object) -> bool:
        return self._attrs.__contains__(key)

    def __repr__(self) -> str:
        return repr(self._attrs)

    def __str__(self) -> str:
        return str(self._attrs)

    def keys(self):
        return self._attrs.keys()

    def values(self):
        return self._attrs.values()

    def items(self):
        return self._attrs.items()


class ApiDictEndpoint(ApiCallMixin, ReadOnlyDict):
    _ctx: Context
    """The context object containing the session and URL for API interactions."""
    _path: str
    """The HTTP path component for the resource endpoint."""

    def _get_api(self, *path) -> JsonifiableDict | None:
        super()._get_api(*path)

    def __init__(
        self,
        ctx: Context,
        path: str,
        get_data: Optional[bool] = None,
        /,
        **attrs: Jsonifiable,
    ) -> None:
        """
        A dict abstraction for any HTTP endpoint that returns a singular resource.

        Adds helper methods to interact with the API with reduced boilerplate.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        path : str
            The HTTP path component for the resource endpoint
        get_data : Optional[bool]
            If `True`, fetch the API and set the attributes from the response. If `False`, only set
            the provided attributes. If `None` [default], fetch the API if no attributes are
            provided.
        attrs : dict
            Resource attributes passed
        """
        # If no attributes are provided, fetch the API and set the attributes from the response
        if get_data is None:
            get_data = len(attrs) == 0

        # If we should get data, fetch the API and set the attributes from the response
        if get_data:
            init_attrs: Jsonifiable = get_api(ctx, path)
            init_attrs_dict = cast(ResponseAttrs, init_attrs)
            # Overwrite the initial attributes with `attrs`: e.g. {'key': value} | {'content_guid': '123'}
            init_attrs_dict.update(attrs)
            attrs = init_attrs_dict

        super().__init__(attrs)
        self._ctx = ctx
        self._path = path


T = TypeVar("T", bound="ReadOnlyDict")
"""A type variable that is bound to the `Active` class"""


class ApiListEndpoint(ApiCallMixin, Generic[T], ABC, object):
    """A HTTP GET endpoint that can fetch a collection."""

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

    @abstractmethod
    def _create_instance(self, path: str, /, **kwargs: Any) -> T:
        """Create an instance of 'T'."""
        raise NotImplementedError()

    def fetch(self) -> Generator[T, None, None]:
        """Fetch the collection.

        Fetches the collection directly from Connect. This operation does not effect the cache state.

        Returns
        -------
        List[T]
        """
        results: Jsonifiable = self._get_api()
        results_list = cast(list[JsonifiableDict], results)
        for result in results_list:
            yield self._to_instance(result)

    def __iter__(self) -> Generator[T, None, None]:
        return self.fetch()

    def _to_instance(self, result: dict) -> T:
        """Converts a result into an instance of T."""
        uid = result[self._uid_key]
        path = posixpath.join(self._path, uid)
        return self._create_instance(path, **result)

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Generator[T, None, None]: ...

    def __getitem__(self, index: int | slice) -> T | Generator[T, None, None]:
        if isinstance(index, slice):
            results = itertools.islice(self.fetch(), index.start, index.stop, index.step)
            for result in results:
                yield result
        else:
            return list(itertools.islice(self.fetch(), index, index + 1))[0]

    # def __len__(self) -> int:
    #     return len(self.fetch())

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        # Jobs - 123 items
        return repr(
            f"{self.__class__.__name__} - { len(list(self.fetch())) } items - {self._path}"
        )

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
        result: Jsonifiable = self._get_api(uid)
        result_obj = cast(JsonifiableDict, result)

        return self._to_instance(result_obj)

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

        conditions_items = conditions.items()

        # Get the first item of the generator that matches the conditions
        # If no item is found, return None
        return next(
            (
                # Return result
                result
                # Iterate through `results` generator
                for result in results
                # If all `conditions`'s key/values are found in `result`'s key/values...
                if result.items() >= conditions_items
            ),
            None,
        )
