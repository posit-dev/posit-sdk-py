from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Protocol

from packaging.version import Version

if TYPE_CHECKING:
    import requests

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
    def __init__(self, session: requests.Session, url: Url):
        self.session = session
        self.url = url

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
