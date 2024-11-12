import functools
from typing import Optional, Protocol

import requests
from packaging.version import Version

from .urls import Url


def requires(version: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(instance: ContextManager, *args, **kwargs):
            ctx = instance.ctx
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
        self._version: str | None

    @property
    def version(self) -> Optional[str]:
        value = self._version
        if isinstance(value, str):
            return value

        # Populate version
        endpoint = self.url + "server_settings"
        response = self.session.get(endpoint)
        result = response.json()
        value = self._version = result.get("version")
        return value

    @version.setter
    def version(self, value):
        self._version = value


class ContextManager(Protocol):
    ctx: Context
