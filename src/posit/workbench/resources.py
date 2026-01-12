from __future__ import annotations

import re

from typing_extensions import TYPE_CHECKING, Any, Hashable, Protocol

if TYPE_CHECKING:
    from .context import Context


class Resource(Protocol):
    """Protocol for Workbench resource objects."""

    def __getitem__(self, key: Hashable, /) -> Any: ...


class _Resource(dict, Resource):
    """Base implementation for Workbench resource objects.

    Provides dictionary-style access to resource fields.
    """

    def __init__(self, ctx: Context, **attributes):
        self._ctx = ctx
        super().__init__(**attributes)


class Resources:
    """Base class for Workbench resource collections."""

    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx


# Filter helper functions for find_by operations


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
