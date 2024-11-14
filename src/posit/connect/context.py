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


# Big mystery: `Context` is a subclass of `dict`. However, this is unnecessary.
# BUT, when `dict` is removed, the following errors occur:
# ```
# uv run pyright
# /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/client.py
#   /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/client.py:274:25 - error: Argument of type "Context" cannot be assigned to parameter "iterable" of type "Iterable[Package]" in function "__new__"
#     "Context" is incompatible with protocol "Iterable[Package]"
#       "__iter__" is not present (reportArgumentType)
# /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/jobs.py
#   /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/jobs.py:302:21 - error: Argument of type "ContentItemContext" cannot be assigned to parameter "iterable" of type "Iterable[Job]" in function "__new__"
#     "ContentItemContext" is incompatible with protocol "Iterable[Job]"
#       "__iter__" is not present (reportArgumentType)
# /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/packages.py
#   /Users/barret/Documents/git/rstudio/posit-sdk-py/posit-sdk-py.nosync/src/posit/connect/packages.py:102:32 - error: Argument of type "ContentItemContext" cannot be assigned to parameter "iterable" of type "Iterable[ContentPackage]" in function "__new__"
#     "ContentItemContext" is incompatible with protocol "Iterable[ContentPackage]"
#       "__iter__" is not present (reportArgumentType)
# 3 errors, 0 warnings, 0 informations
# ```
# This is a mystery because `Context` is not used as an iterable in the codebase.


class Context(dict):
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
