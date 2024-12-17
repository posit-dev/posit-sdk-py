from __future__ import annotations

import functools
import weakref

from packaging.version import Version
from typing_extensions import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .client import Client


def requires(version: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(instance: ContextManager, *args, **kwargs):
            ctx = instance._ctx
            if ctx.version and Version(ctx.version) < Version(version):
                raise RuntimeError(
                    f"This API is not available in Connect version {ctx.version}. Please upgrade to version {version} or later.",
                )
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
        if not hasattr(self, "_version"):
            response = self.client.get("server_settings")
            result = response.json()
            self._version: str | None = result.get("version")

        return self._version

    @version.setter
    def version(self, value: str | None):
        self._version = value


class ContextManager(Protocol):
    _ctx: Context
