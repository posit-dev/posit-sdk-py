from __future__ import annotations

import functools
import weakref
from typing import TYPE_CHECKING, Protocol

from packaging.version import Version

if TYPE_CHECKING:
    import requests

    from .client import Client
    from .urls import Url


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
        self.session: requests.Session = client.session
        self.url: Url = client.cfg.url
        # Since this is a child object of the client, we use a weak reference to avoid circular
        # references (which would prevent garbage collection)
        # Note, it might need to be a strong reference, but a `del client` test will need to be
        # updated
        self.client: Client = weakref.proxy(client)

    @property
    def version(self) -> str | None:
        if not hasattr(self, "_version"):
            endpoint = self.url + "server_settings"
            response = self.session.get(endpoint)
            result = response.json()
            self._version: str | None = result.get("version")

        return self._version

    @version.setter
    def version(self, value: str | None):
        self._version = value


class ContextManager(Protocol):
    _ctx: Context
