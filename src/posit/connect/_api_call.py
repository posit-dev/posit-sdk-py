from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ._json import Jsonifiable
    from .context import Context


class ApiContextProtocol(Protocol):
    _ctx: Context
    _path: str


def endpoint(ctx: Context, path: str, *, extra_endpoint: str = "") -> str:
    return ctx.url + path + extra_endpoint


def get_api(ctx: Context, path: str, *, extra_endpoint: str = "") -> Jsonifiable:
    response = ctx.session.get(endpoint(ctx, path, extra_endpoint=extra_endpoint))
    return response.json()


class ApiCallMixin(ApiContextProtocol):
    _ctx: Context
    """The context object containing the session and URL for API interactions."""
    _path: str
    """The HTTP path component for the resource endpoint."""

    def _endpoint(self, extra_endpoint: str = "") -> str:
        return endpoint(self._ctx, self._path, extra_endpoint=extra_endpoint)

    def _get_api(self, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(extra_endpoint))
        return response.json()

    def _delete_api(self, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.get(self._endpoint(extra_endpoint))
        return response.json()

    def _patch_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.patch(self._endpoint(extra_endpoint), json=json)
        return response.json()

    def _put_api(self, json: Jsonifiable | None, *, extra_endpoint: str = "") -> Jsonifiable:
        response = self._ctx.session.put(self._endpoint(extra_endpoint), json=json)
        return response.json()
