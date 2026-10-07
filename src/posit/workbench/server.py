"""Server info for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, cast

from . import rpc
from .resources import Resources

if TYPE_CHECKING:
    from .rpc import ContextProtocol
    from .types import VersionInfo


class Server(Resources):
    """Server-level metadata."""

    def __init__(self, ctx: ContextProtocol) -> None:
        # Not super().__init__(ctx): Resources.__init__ types ctx as the specific in-session
        # Context, but this manager is shared with the Bearer-token admin.Context too -- see
        # ContextProtocol's docstring in rpc.py.
        self._ctx = ctx

    def version(self) -> VersionInfo:
        """Get the server version and enabled feature list.

        Confirmed against a live server: unlike every other method, this one returns its
        payload bare, not wrapped in ``{"result": ...}``.
        """
        return cast("VersionInfo", rpc.call_raw(self._ctx.client, "version"))
