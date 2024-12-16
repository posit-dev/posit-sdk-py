from __future__ import annotations

import posixpath

from typing_extensions import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._json import Jsonifiable
    from .context import Context


class ApiCallProtocol(Protocol):
    _ctx: Context
    _path: str

    def _endpoint(self, *path) -> str: ...
    def _get_api(self, *path) -> Jsonifiable: ...
    def _delete_api(self, *path) -> Jsonifiable | None: ...
    def _patch_api(self, *path, json: Jsonifiable | None) -> Jsonifiable: ...
    def _put_api(self, *path, json: Jsonifiable | None) -> Jsonifiable: ...


def endpoint(*path) -> str:
    return posixpath.join(*path)


# Helper methods for API interactions
def get_api(ctx: Context, *path) -> Jsonifiable:
    response = ctx.client.get(*path)
    return response.json()


def put_api(
    ctx: Context,
    *path,
    json: Jsonifiable | None,
) -> Jsonifiable:
    response = ctx.client.put(*path, json=json)
    return response.json()


# Mixin class for API interactions


class ApiCallMixin:
    def _endpoint(self: ApiCallProtocol, *path) -> str:
        return endpoint(self._path, *path)

    def _get_api(self: ApiCallProtocol, *path) -> Jsonifiable:
        response = self._ctx.client.get(self._endpoint(*path))
        return response.json()

    def _delete_api(self: ApiCallProtocol, *path) -> Jsonifiable | None:
        response = self._ctx.client.delete(self._endpoint(*path))
        if len(response.content) == 0:
            return None
        return response.json()

    def _patch_api(
        self: ApiCallProtocol,
        *path,
        json: Jsonifiable | None,
    ) -> Jsonifiable:
        response = self._ctx.client.patch(self._endpoint(*path), json=json)
        return response.json()

    def _put_api(
        self: ApiCallProtocol,
        *path,
        json: Jsonifiable | None,
    ) -> Jsonifiable:
        response = self._ctx.client.put(self._endpoint(*path), json=json)
        return response.json()
