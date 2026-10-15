"""User lookup for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Iterable, Protocol

from . import rpc
from .resources import Resource, ResourceSequence, _Resource, _ResourceSequence

if TYPE_CHECKING:
    import builtins

    from .rpc import ContextProtocol
    from .types import WorkbenchUser


class User(Resource, Protocol):
    """A registered Workbench user with dictionary field access."""


class Users(ResourceSequence[User], Protocol):
    """Look up registered Workbench users. Requires an admin/super-admin token."""

    def fetch(self) -> Iterable[User]:
        """Fetch all registered user records.

        Returns
        -------
        Iterable[User]
            Registered Workbench users.
        """
        ...

    def find_by(
        self,
        *,
        username: str = ...,
        status: str = ...,
        isAdmin: bool = ...,
        isSuperAdmin: bool = ...,
        uid: int = ...,
    ) -> User | None:
        """Find the first user matching all record fields exactly.

        Parameters
        ----------
        username : str, optional
            The login name.
        status : str, optional
            The account status.
        isAdmin : bool, optional
            Whether the account has administrator privileges.
        isSuperAdmin : bool, optional
            Whether the account has super-administrator privileges.
        uid : int, optional
            The numeric user identifier.

        Returns
        -------
        User or None
            The first matching user, or None when no record matches.
        """
        ...

    def list(self) -> builtins.list[WorkbenchUser]:
        """List registered Workbench users."""
        ...


class _Users(_ResourceSequence[User], Users):
    """Look up registered Workbench users. Requires an admin/super-admin token."""

    def __init__(self, ctx: ContextProtocol) -> None:
        super().__init__(ctx, "get_users", resource_type=_Resource)

    def list(self) -> builtins.list[WorkbenchUser]:
        return rpc.call(self._ctx.client, "get_users")
