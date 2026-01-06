from __future__ import annotations

import re
import warnings
from typing_extensions import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context import Context


class BaseResource(dict):
    """Base class for Workbench resource objects.

    Extends dict to provide attribute-style access with deprecation warnings,
    similar to Connect's BaseResource implementation.
    """

    def __init__(self, ctx: Context, /, **kwargs):
        super().__init__(**kwargs)
        self._ctx = ctx

    def __getattr__(self, name):
        if name in self:
            warnings.warn(
                f"Accessing the field '{name}' via attribute is deprecated and will be removed in v1.0.0. "
                f"Please use __getitem__ (e.g., {self.__class__.__name__.lower()}['{name}']) for field access instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def update(self, *args, **kwargs):
        """Update the resource data."""
        super().update(*args, **kwargs)


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
