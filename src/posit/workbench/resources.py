from __future__ import annotations

import re

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    Protocol,
    Sequence,
    SupportsIndex,
    TypeVar,
    overload,
)

from . import rpc

if TYPE_CHECKING:
    from .rpc import ContextProtocol


class Resource(Protocol):
    """Protocol for Workbench resource objects."""

    _ctx: ContextProtocol

    def __getitem__(self, key: Hashable, /) -> Any: ...


class _Resource(dict, Resource):
    """Base implementation for Workbench resource objects.

    Provides dictionary-style access to resource fields.
    """

    def __init__(self, ctx: ContextProtocol, **attributes):
        self._ctx = ctx
        super().__init__(**attributes)


ContextT = TypeVar("ContextT", bound="ContextProtocol")


class Resources(Generic[ContextT]):
    """Base class for Workbench resource collections."""

    def __init__(self, ctx: ContextT) -> None:
        self._ctx = ctx


T = TypeVar("T", bound=Resource)


class ResourceSequence(Protocol[T]):
    """Sequence contract for Workbench resource collections."""

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> T: ...

    @overload
    def __getitem__(self, index: slice, /) -> list[T]: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[T]: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...


class _ResourceSequence(Sequence[T], Resources["ContextProtocol"]):
    """Fetch and wrap records from a Workbench RPC result.

    Collection access fetches records on demand without caching. Lookup conditions
    apply locally, so record fields never become unsupported RPC parameters.
    """

    def __init__(
        self,
        ctx: ContextProtocol,
        method: str,
        *,
        resource_type: Callable[..., T],
        result_key: str | None = None,
    ) -> None:
        super().__init__(ctx)
        self._method = method
        self._resource_type = resource_type
        self._result_key = result_key

    @overload
    def __getitem__(self, index: SupportsIndex) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> T | list[T]:
        return list(self.fetch())[index]

    def __len__(self) -> int:
        return len(list(self.fetch()))

    def __iter__(self) -> Iterator[T]:
        return iter(self.fetch())

    def __str__(self) -> str:
        return str(list(self.fetch()))

    def __repr__(self) -> str:
        return repr(list(self.fetch()))

    def fetch(self, **params: Any) -> Iterable[T]:
        result = rpc.call(self._ctx.client, self._method, **params)
        records = result if self._result_key is None else result.get(self._result_key) or []
        return [self._resource_type(self._ctx, **record) for record in records]

    def find_by(self, **conditions: Any) -> T | None:
        """Return the first record matching all conditions exactly, or None."""
        for resource in self.fetch():
            try:
                matches = all(resource[key] == value for key, value in conditions.items())
            except KeyError:
                continue
            if matches:
                return resource
        return None


def _matches_exact(resource: dict, /, key: str, value: Any) -> bool:
    """Check if resource field matches value exactly."""
    return resource.get(key) == value


def _matches_pattern(resource: dict, /, key: str, pattern: str) -> bool:
    """Check if resource field matches regex pattern."""
    field_value = resource.get(key)
    if field_value is None:
        return False
    return re.search(pattern, str(field_value)) is not None


def _contains_dict_key_values(resource: dict, /, key: str, value: dict) -> bool:
    """Check if resource's dict field contains all key-value pairs from value."""
    resource_value = resource.get(key)
    if not isinstance(resource_value, dict):
        return False
    return all(k in resource_value and resource_value[k] == v for k, v in value.items())
