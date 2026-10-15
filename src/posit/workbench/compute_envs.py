"""Compute environment lookup for the Workbench launcher API."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Iterable, Protocol

from . import rpc
from .resources import Resource, ResourceSequence, _Resource, _ResourceSequence

if TYPE_CHECKING:
    from .rpc import ContextProtocol
    from .types import ComputeEnvsResult


class ComputeEnv(Resource, Protocol):
    """A Workbench compute environment with dictionary field access."""


class ComputeEnvs(ResourceSequence[ComputeEnv], Protocol):
    """Look up available compute environments (clusters) and IDE configuration."""

    def fetch(self, *, user: str = ...) -> Iterable[ComputeEnv]:
        """Fetch compute environment records without the IDE configuration.

        Parameters
        ----------
        user : str, optional
            The user whose available environments to retrieve.

        Returns
        -------
        Iterable[ComputeEnv]
            Compute environments from the launcher response.
        """
        ...

    def find_by(
        self,
        *,
        name: str = ...,
        type: str = ...,  # noqa: A002
        supportsContainers: bool = ...,
    ) -> ComputeEnv | None:
        """Find the first environment matching all record fields exactly.

        Parameters
        ----------
        name : str, optional
            The environment name.
        type : str, optional
            The launcher cluster type.
        supportsContainers : bool, optional
            Whether the environment supports containers.

        Returns
        -------
        ComputeEnv or None
            The first matching environment, or None when no record matches.
        """
        ...

    def list(self, *, user: str | None = None) -> ComputeEnvsResult:
        """List supported compute environments/IDEs and their resource limits."""
        ...


class _ComputeEnvs(_ResourceSequence[ComputeEnv], ComputeEnvs):
    """Look up available compute environments (clusters) and IDE configuration."""

    def __init__(self, ctx: ContextProtocol) -> None:
        super().__init__(ctx, "get_compute_envs", resource_type=_Resource, result_key="clusters")

    def list(self, *, user: str | None = None) -> ComputeEnvsResult:
        return rpc.call(self._ctx.client, "get_compute_envs", user=user)
