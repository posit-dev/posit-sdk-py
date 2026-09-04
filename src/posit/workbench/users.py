"""User lookup for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from . import rpc
from .resources import Resources

if TYPE_CHECKING:
    import builtins

    from .rpc import ContextProtocol
    from .types import WorkbenchUser


class Users(Resources):
    """Look up registered Workbench users. Requires an admin/super-admin token."""

    def __init__(self, ctx: ContextProtocol) -> None:
        # Not super().__init__(ctx): Resources.__init__ types ctx as the specific in-session
        # Context, but this manager is shared with the Bearer-token admin.Context too -- see
        # ContextProtocol's docstring in rpc.py.
        self._ctx = ctx

    def list(self) -> builtins.list[WorkbenchUser]:
        """List registered Workbench users."""
        return rpc.call(self._ctx.client, "get_users")
