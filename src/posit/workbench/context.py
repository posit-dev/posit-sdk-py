from __future__ import annotations

import functools

# version stuff from RSTUDIO_VERSION
import os
import weakref

from packaging.version import Version
from typing_extensions import TYPE_CHECKING, Callable, Concatenate, ParamSpec, Protocol, TypeVar

if TYPE_CHECKING:
    from .client import Client


def _normalize_version(version_str: str) -> str:
    """Normalize Workbench version strings to PEP 440 format.

    Workbench versions like '2025.12.0-daily+324.pro1' or '2025.12.0-dev' need
    to be normalized by stripping metadata for version comparison.

    Note: Dev version checking is handled separately in the @requires decorator.
    This function only extracts the base version for numeric comparison.
    """
    # Extract the base version (e.g., '2025.12.0' from '2025.12.0-daily+324.pro1')
    base = version_str.split("-")[0].split("+")[0]
    return base


P = ParamSpec("P")
R = TypeVar("R")
CM = TypeVar("CM", bound="ContextManager")


def requires(
    version: str,
) -> Callable[
    [Callable[Concatenate[CM, P], R]],
    Callable[Concatenate[CM, P], R],
]:
    def decorator(func: Callable[Concatenate[CM, P], R]) -> Callable[Concatenate[CM, P], R]:
        @functools.wraps(func)
        def wrapper(instance: CM, *args: P.args, **kwargs: P.kwargs) -> R:
            ctx = instance._ctx
            if ctx.version:
                # Skip version check for development versions (matches R implementation)
                if "dev" in ctx.version.lower():
                    return func(instance, *args, **kwargs)

                try:
                    current_version = Version(_normalize_version(ctx.version))
                    required_version = Version(_normalize_version(version))
                    if current_version < required_version:
                        raise RuntimeError(
                            f"This API is not available in Posit Workbench version {ctx.version}. Please upgrade to version {version} or later.",
                        )
                except RuntimeError:
                    # Re-raise version requirement errors
                    raise
                except Exception:
                    # If version parsing fails, allow the call to proceed
                    # This prevents version parsing issues from blocking functionality
                    pass
            return func(instance, *args, **kwargs)

        return wrapper

    return decorator


class Context:
    def __init__(self, client: Client):
        # Since this is a child object of the client, we use a weak reference to avoid circular
        # references (which would prevent garbage collection)
        self.client: Client = weakref.proxy(client)

    @property
    def version(self) -> str | None:
        # Check RSTUDIO_VERSION environment variable
        if not hasattr(self, "_version"):
            self._version = os.environ.get("RSTUDIO_VERSION")
        return self._version

    @version.setter
    def version(self, value: str | None):
        self._version = value


class ContextManager(Protocol):
    _ctx: Context
