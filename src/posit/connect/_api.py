# TODO-barret-future; Piecemeal migrate everything to leverage `ApiDictEndpoint`
# TODO-barret-future; Merge any trailing behavior of `Active` or `ActiveList` into the new classes.

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Optional, cast

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
