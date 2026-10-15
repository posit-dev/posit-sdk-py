"""Server info for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Protocol, cast

from . import rpc
from .resources import Resources
from .rpc import ContextProtocol

if TYPE_CHECKING:
    from .types import VersionInfo


class Server(Protocol):
    """Server-level metadata."""

    def version(self) -> VersionInfo:
        """Get the server version and enabled feature list.

        Confirmed against a live server: unlike every other method, this one returns its
        payload bare, not wrapped in ``{"result": ...}``.
        """
        ...


class _Server(Resources[ContextProtocol], Server):
    """Server-level metadata."""

    def version(self) -> VersionInfo:
        return cast("VersionInfo", rpc.call_raw(self._ctx.client, "version"))
