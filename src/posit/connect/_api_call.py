from __future__ import annotations

import posixpath
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._json import Jsonifiable
    from .context import Context


# Just the same as `.context.py` ContextManager but with `._ctx` attribute, not `.ctx`
class ContextP(Protocol):
    _ctx: Context


class ContextCls(ContextP):
    """Class that contains the client context."""

    _ctx: Context

    def __init__(self, ctx: Context):
        self._ctx = ctx


class ApiCallProtocol(ContextP, Protocol):
    _path: str

    def _endpoint(self, *path) -> str: ...
    def _get_api(self, *path) -> Jsonifiable: ...
    def _delete_api(self, *path) -> Jsonifiable | None: ...
    def _patch_api(self, *path, json: Jsonifiable | None) -> Jsonifiable: ...
    def _put_api(self, *path, json: Jsonifiable | None) -> Jsonifiable: ...


def endpoint(ctx: Context, *path) -> str:
    return ctx.url + posixpath.join(*path)


# Helper methods for API interactions
def get_api(ctx: Context, *path) -> Jsonifiable:
    response = ctx.session.get(endpoint(ctx, *path))
    return response.json()


def put_api(
    ctx: Context,
    *path,
    json: Jsonifiable | None,
) -> Jsonifiable:
    response = ctx.session.put(endpoint(ctx, *path), json=json)
    return response.json()


# Mixin class for API interactions


class ApiCallMixin:
    def _endpoint(self: ApiCallProtocol, *path) -> str:
        return endpoint(self._ctx, self._path, *path)

    def _get_api(self: ApiCallProtocol, *path) -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(*path))
        return response.json()

    def _delete_api(self: ApiCallProtocol, *path) -> Jsonifiable | None:
        response = self._ctx.session.delete(self._endpoint(*path))
        if len(response.content) == 0:
            return None
        return response.json()

    def _patch_api(
        self: ApiCallProtocol,
        *path,
        json: Jsonifiable | None,
    ) -> Jsonifiable:
        response = self._ctx.session.patch(self._endpoint(*path), json=json)
        return response.json()

    def _put_api(
        self: ApiCallProtocol,
        *path,
        json: Jsonifiable | None,
    ) -> Jsonifiable:
        response = self._ctx.session.put(self._endpoint(*path), json=json)
        return response.json()
