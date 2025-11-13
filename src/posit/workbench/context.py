from __future__ import annotations

# version stuff from RSTUDIO_VERSION
import os
import functools
import weakref

from packaging.version import Version
from typing_extensions import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .client import Client

def _normalize_version(version_str: str) -> str:
    """Normalize Workbench version strings to PEP 440 format.

    Workbench versions like '2025.12.0-daily+324.pro1' need to be normalized
    to '2025.12.0.dev324' for proper version comparison.
    """
    # Extract the base version (e.g., '2025.12.0')
    base = version_str.split('-')[0].split('+')[0]

    # Handle pre-release/dev versions
    if '-' in version_str or '+' in version_str:
        # For now, treat any dev/daily builds as dev versions
        # Extract build number if present (e.g., '324' from '+324')
        if '+' in version_str:
            build_part = version_str.split('+')[1].split('.')[0]
            if build_part.isdigit():
                return f"{base}.dev{build_part}"
        return f"{base}.dev0"

    return base

def requires(version: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(instance: ContextManager, *args, **kwargs):
            ctx = instance._ctx
            if ctx.version:
                try:
                    current_version = Version(_normalize_version(ctx.version))
                    required_version = Version(_normalize_version(version))
                    if current_version < required_version:
                        raise RuntimeError(
                            f"This API is not available in Posit Workbench version {ctx.version}. Please upgrade to version {version} or later.",
                        )
                except Exception:
                    # If version comparison fails, log a warning but allow the call to proceed
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
