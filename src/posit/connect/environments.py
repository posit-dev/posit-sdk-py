"""Environment resources."""

from __future__ import annotations

from abc import abstractmethod

from typing_extensions import (
    List,
    Literal,
    Protocol,
    TypedDict,
    runtime_checkable,
)

from .resources import Resource, ResourceSequence

MatchingType = Literal["any", "exact", "none"]
"""Directions for how environments are considered for selection.

    - any: The image may be selected by Connect if not defined in the bundle manifest.
    - exact: The image must be defined in the bundle manifest
    - none: Never use this environment
"""


class Installation(TypedDict):
    """Interpreter installation in an execution environment."""

    path: str
    """The absolute path to the interpreter's executable."""

    version: str
    """The semantic version of the interpreter."""


class Installations(TypedDict):
    """Interpreter installations in an execution environment."""

    installations: List[Installation]
    """Interpreter installations in an execution environment."""


class Environment(Resource):
    @abstractmethod
    def destroy(self) -> None:
        """Destroy the environment.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator privileges.
        """

    @abstractmethod
    def update(
        self,
        *,
        title: str,
        description: str | None = ...,
        matching: MatchingType | None = ...,
        supervisor: str | None = ...,
        python: Installations | None = ...,
        quarto: Installations | None = ...,
        r: Installations | None = ...,
        tensorflow: Installations | None = ...,
    ) -> None:
        """Update the environment.

        Parameters
        ----------
        title : str
            A human-readable title.
        description : str | None, optional, not required
            A human-readable description.
        matching : MatchingType, optional, not required
            Directions for how the environment is considered for selection
        supervisor : str | None, optional, not required
            Path to the supervisor script.
        python : Installations, optional, not required
            The Python installations available in this environment
        quarto : Installations, optional, not required
            The Quarto installations available in this environment
        r : Installations, optional, not required
            The R installations available in this environment
        tensorflow : Installations, optional, not required
            The Tensorflow installations available in this environment

        Note
        ----
        This action requires administrator privileges.
        """


@runtime_checkable
class Environments(ResourceSequence[Environment], Protocol):
    def create(
        self,
        *,
        title: str,
        name: str,
        cluster_name: str | Literal["Kubernetes"],
        matching: MatchingType = "any",
        description: str | None = ...,
        supervisor: str | None = ...,
        python: Installations | None = ...,
        quarto: Installations | None = ...,
        r: Installations | None = ...,
        tensorflow: Installations | None = ...,
    ) -> Environment:
        """Create an environment.

        Parameters
        ----------
        title : str
            A human-readable title.
        name : str
            The container image name used for execution in this environment.
        cluster_name : str | Literal["Kubernetes"]
            The cluster identifier for this environment. Defaults to "Kubernetes" when Off-Host-Execution is enabled.
        description : str, optional
            A human-readable description.
        matching : MatchingType
            Directions for how the environment is considered for selection, by default is "any".
        supervisor : str, optional
            Path to the supervisor script
        python : Installations, optional
            The Python installations available in this environment
        quarto : Installations, optional
            The Quarto installations available in this environment
        r : Installations, optional
            The R installations available in this environment
        tensorflow : Installations, optional
            The Tensorflow installations available in this environment

        Returns
        -------
        Environment

        Note
        ----
        This action requires administrator privileges.
        """
        ...

    def find(self, guid: str, /) -> Environment: ...

    def find_by(
        self,
        *,
        id: str = ...,  # noqa: A002
        guid: str = ...,
        created_time: str = ...,
        updated_time: str = ...,
        title: str = ...,
        name: str = ...,
        description: str | None = ...,
        cluster_name: str | Literal["Kubernetes"] = ...,
        environment_type: str | Literal["Kubernetes"] = ...,
        matching: MatchingType = ...,
        supervisor: str | None = ...,
        python: Installations | None = ...,
        quarto: Installations | None = ...,
        r: Installations | None = ...,
        tensorflow: Installations | None = ...,
    ) -> Environment | None:
        """Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        id : str
            The numerical identifier.
        guid : str
            The unique identifier.
        created_time : str
            The timestamp (RFC3339) when the environment was created.
        updated_time : str
            The timestamp (RFC3339) when the environment was updated.
        title : str
            A human-readable title.
        name : str
            The container image name used for execution in this environment.
        description : str, optional
            A human-readable description.
        cluster_name : str | Literal["Kubernetes"]
            The cluster identifier for this environment. Defaults to "Kubernetes" when Off-Host-Execution is enabled.
        environment_type : str | Literal["Kubernetes"]
            The cluster environment type. Defaults to "Kubernetes" when Off-Host-Execution is enabled.
        matching : MatchingType
            Directions for how the environment is considered for selection.
        supervisor : str, optional
            Path to the supervisor script
        python : Installations, optional
            The Python installations available in this environment
        quarto : Installations, optional
            The Quarto installations available in this environment
        r : Installations, optional
            The R installations available in this environment
        tensorflow : Installations, optional
            The Tensorflow installations available in this environment

        Returns
        -------
        Environment | None

        Note
        ----
        This action requires administrator or publisher privileges.
        """
