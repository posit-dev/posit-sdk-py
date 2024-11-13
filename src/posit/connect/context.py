import functools
from typing import Optional, Protocol

import requests
from packaging.version import Version

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


class Context(dict):
    def __init__(self, session: requests.Session, url: Url):
        self.session = session
        self.url = url

    @property
    def version(self) -> Optional[str]:
        try:
            value = self["version"]
        except KeyError:
            endpoint = self.url + "server_settings"
            response = self.session.get(endpoint)
            result = response.json()
            value = self["version"] = result.get("version")
        return value

    @version.setter
    def version(self, value):
        self["version"] = value


class ContextManager(Protocol):
    _ctx: Context
