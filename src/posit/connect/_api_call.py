from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._json import Jsonifiable
    from .context import Context


class ApiCallProtocol(Protocol):
    _ctx: Context
    _path: str

    def _endpoint(self, extra_endpoint: str = "") -> str: ...
    def _get_api(self, *, extra_endpoint: str = "") -> Jsonifiable: ...
    def _delete_api(self, *, extra_endpoint: str = "") -> Jsonifiable | None: ...
    def _patch_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable: ...
    def _put_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable: ...


def endpoint(ctx: Context, path: str, *, extra_endpoint: str = "") -> str:
    return ctx.url + path + extra_endpoint


# Helper methods for API interactions
def get_api(ctx: Context, path: str, *, extra_endpoint: str = "") -> Jsonifiable:
    response = ctx.session.get(endpoint(ctx, path, extra_endpoint=extra_endpoint))
    return response.json()


def put_api(
    ctx: Context, path: str, json: Jsonifiable | None, *, extra_endpoint: str = ""
) -> Jsonifiable:
    response = ctx.session.put(endpoint(ctx, path, extra_endpoint=extra_endpoint), json=json)
    return response.json()


# Mixin class for API interactions


class ApiCallMixin:
    def _endpoint(self: ApiCallProtocol, extra_endpoint: str = "") -> str:
        return endpoint(self._ctx, self._path, extra_endpoint=extra_endpoint)

    def _get_api(self: ApiCallProtocol, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(extra_endpoint))
        return response.json()

    def _delete_api(self: ApiCallProtocol, *, extra_endpoint: str = "") -> Jsonifiable | None:
        response = self._ctx.session.delete(self._endpoint(extra_endpoint))
        if len(response.content) == 0:
            return None
        return response.json()

    def _patch_api(
        self: ApiCallProtocol, json: Jsonifiable | None, *, extra_endpoint: str = ""
    ) -> Jsonifiable:
        response = self._ctx.session.patch(self._endpoint(extra_endpoint), json=json)
        return response.json()

    def _put_api(
        self: ApiCallProtocol, json: Jsonifiable | None, *, extra_endpoint: str = ""
    ) -> Jsonifiable:
        response = self._ctx.session.put(self._endpoint(extra_endpoint), json=json)
        return response.json()
