"""Compute environment lookup for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from . import rpc
from .resources import Resources

if TYPE_CHECKING:
    from .rpc import ContextProtocol
    from .types import ComputeEnvsResult


class ComputeEnvs(Resources):
    """Look up available compute environments (clusters) and IDE configuration."""

    def __init__(self, ctx: ContextProtocol) -> None:
        # Not super().__init__(ctx): Resources.__init__ types ctx as the specific in-session
        # Context, but this manager is shared with the Bearer-token admin.Context too -- see
        # ContextProtocol's docstring in rpc.py.
        self._ctx = ctx

    def list(self, *, user: str | None = None) -> ComputeEnvsResult:
        """List supported compute environments/IDEs and their resource limits."""
        return rpc.call(self._ctx.client, "get_compute_envs", user=user)
