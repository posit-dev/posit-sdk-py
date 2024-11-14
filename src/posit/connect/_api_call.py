from __future__ import annotations

import posixpath
from typing import TYPE_CHECKING, Any, Optional, Protocol

from ._types_context import ContextP

if TYPE_CHECKING:
    from .context import Context


class ApiCallProtocol(ContextP, Protocol):
    _path: str

    def _endpoint(self, *path) -> str: ...
    def _get_api(self, *path) -> Any: ...
    def _delete_api(self, *path) -> Any | None: ...
    def _patch_api(self, *path, json: Any | None) -> Any: ...
    def _post_api(self, *path, json: Any | None) -> Any | None: ...
    def _put_api(self, *path, json: Any | None) -> Any: ...


def endpoint(ctx: Context, *path) -> str:
    return ctx.url + posixpath.join(*path)


# Helper methods for API interactions
def get_api(ctx: Context, *path) -> Any:
    response = ctx.session.get(endpoint(ctx, *path))
    return response.json()


def put_api(
    ctx: Context,
    *path,
    json: Any | None,
) -> Any:
    response = ctx.session.put(endpoint(ctx, *path), json=json)
    return response.json()


# Mixin class for API interactions


class ApiCallMixin:
    def _endpoint(self: ApiCallProtocol, *path) -> str:
        return endpoint(self._ctx, self._path, *path)

    def _get_api(self: ApiCallProtocol, *path, params: Optional[dict] = None) -> Any:
        response = self._ctx.session.get(self._endpoint(*path), params=params)
        return response.json()

    def _delete_api(self: ApiCallProtocol, *path) -> Any | None:
        response = self._ctx.session.delete(self._endpoint(*path))
        if len(response.content) == 0:
            return None
        return response.json()

    def _patch_api(
        self: ApiCallProtocol,
        *path,
        json: Any | None,
    ) -> Any:
        response = self._ctx.session.patch(self._endpoint(*path), json=json)
        return response.json()

    def _post_api(
        self: ApiCallProtocol,
        *path,
        json: Any | None,
    ) -> Any | None:
        response = self._ctx.session.post(self._endpoint(*path), json=json)
        if len(response.content) == 0:
            return None
        return response.json()

    def _put_api(
        self: ApiCallProtocol,
        *path,
        json: Any | None,
    ) -> Any | None:
        response = self._ctx.session.put(self._endpoint(*path), json=json)
        if len(response.content) == 0:
            return None
        return response.json()
