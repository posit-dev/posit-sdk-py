from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, TypedDict, overload

from .resources import (
    Active,
    ActiveDestroyer,
    ActiveFinderMethods,
    ActiveSequence,
    ActiveSequenceCreator,
    ActiveUpdater,
)

if TYPE_CHECKING:
    from .context import Context


class _Installation(TypedDict):
    """Interpreter installation in an execution environment."""

    path: str
    """The absolute path to the interpreter's executable."""

    version: str
    """The semantic version of the interpreter."""


class _Installations(TypedDict):
    """Interpreter installations in an execution environment."""

    installations: List[_Installation]
    """Interpreter installations in an execution environment."""


class Environment(ActiveUpdater, ActiveDestroyer, Active):
    @overload
    def __init__(
        self,
        ctx: Context,
        path: str,
        /,
        *,
        id: str,
        guid: str,
        created_time: str,
        updated_time: str,
        title: str,
        name: str,
        description: str | None,
        cluster_name: str | Literal["Kubernetes"],
        environment_type: str | Literal["Kubernetes"],
        matching: Literal["any", "exact", "none"],
        supervisor: str | None,
        python: _Installations | None,
        quarto: _Installations | None,
        r: _Installations | None,
        tensorflow: _Installations | None,
    ):
        """Initialize an environment.

        Parameters
        ----------
        ctx : Context
            The SDK context.
        path : str
            The URL endpoint path.
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
        matching : Literal["any", "exact", "none"]
            Directions for how environments are considered for selection.
            any: The image may be selected by Connect if not defined in the bundle manifest.
            exact: The image must be defined in the bundle manifest
            none: Never use this environment
        supervisor : str, optional
            Path to the supervisor script
        python : _Installations, optional
            The Python installations available in this environment
        quarto : _Installations, optional
            The Quarto installations available in this environment
        r : _Installations, optional
            The R installations available in this environment
        tensorflow : _Installations, optional
            The Tensorflow installations available in this environment
        """

    @overload
    def __init__(self, ctx: Context, path: str, /, **attributes): ...

    def __init__(self, ctx: Context, path: str, /, **attributes):
        super().__init__(ctx, path, **attributes)

    def destroy(self):
        """Destroy the environment.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator privileges.
        """
        return super().destroy()

    @overload
    def update(
        self,
        /,
        *,
        title: str,
        description: str | None = ...,
        matching: Literal["any", "exact", "none"] = ...,
        supervisor: str | None = ...,
        python: _Installations | None = ...,
        quarto: _Installations | None = ...,
        r: _Installations | None = ...,
        tensorflow: _Installations | None = ...,
    ) -> None:
        """Update the environment.

        Parameters
        ----------
        title : str
            A human-readable title.
        description : str | None, optional, not required
            A human-readable description.
        matching : Literal["any", "exact", "none"], optional, not required
            Directions for how environments are considered for selection.
            any: The image may be selected by Connect if not defined in the bundle manifest.
            exact: The image must be defined in the bundle manifest
            none: Never use this environment
        supervisor : str | None, optional, not required
            Path to the supervisor script.
        python : _Installations | None, optional, not required
            The Python installations available in this environment
        quarto : _Installations | None, optional, not required
            The Quarto installations available in this environment
        r : _Installations | None, optional, not required
            The Python installations available in this environment
        tensorflow : _Installations | None, optional, not required
            The Python installations available in this environment

        Note
        ----
        This action requires administrator privileges.
        """

    @overload
    def update(self, /, **attributes) -> None:
        """Update the environment.

        Note
        ----
        This action requires administrator privileges.
        """

    def update(self, /, **attributes) -> None:
        """Update the environment.

        Note
        ----
        This action requires administrator privileges.
        """
        return super().update(**attributes)


class Environments(
    ActiveFinderMethods[Environment],
    ActiveSequenceCreator[Environment],
    ActiveSequence[Environment],
):
    def _create_instance(self, path, /, **attributes) -> Environment:
        return Environment(self._ctx, path, **attributes)

    @overload
    def create(
        self,
        /,
        *,
        title: str,
        name: str,
        cluster_name: str | Literal["Kubernetes"],
        description: str | None = ...,
        matching: Literal["any", "exact", "none"] = "any",
        supervisor: str | None = ...,
        python: _Installations | None = ...,
        quarto: _Installations | None = ...,
        r: _Installations | None = ...,
        tensorflow: _Installations | None = ...,
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
        matching : Literal["any", "exact", "none"]
            Directions for how environments are considered for selection.
            any: The image may be selected by Connect if not defined in the bundle manifest.
            exact: The image must be defined in the bundle manifest
            none: Never use this environment
        supervisor : str, optional
            Path to the supervisor script
        python : _Installations, optional
            The Python installations available in this environment
        quarto : _Installations, optional
            The Quarto installations available in this environment
        r : _Installations, optional
            The R installations available in this environment
        tensorflow : _Installations, optional
            The Tensorflow installations available in this environment

        Returns
        -------
        Environment

        Note
        ----
        This action requires administrator privileges.
        """

    @overload
    def create(self, **attributes) -> Environment:
        """Create an environment.

        Returns
        -------
        Environment

        Note
        ----
        This action requires administrator privileges.
        """

    def create(self, **attributes) -> Environment:
        """Create an environment.

        Returns
        -------
        Environment

        Note
        ----
        This action requires administrator privileges.
        """
        return super().create(**attributes)

    def find(self, uid: str) -> Environment:
        """Find a record by its unique identifier.

        Parameters
        ----------
        uid : str
            The unique identifier.

        Returns
        -------
        Environment
        """
        return super().find(uid)

    @overload
    def find_by(
        self,
        *,
        id: str,
        guid: str,
        created_time: str,
        updated_time: str,
        title: str,
        name: str,
        description: str | None,
        cluster_name: str | Literal["Kubernetes"],
        environment_type: str | Literal["Kubernetes"],
        matching: Literal["any", "exact", "none"],
        supervisor: str | None,
        python: _Installations | None,
        quarto: _Installations | None,
        r: _Installations | None,
        tensorflow: _Installations | None,
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
        matching : Literal["any", "exact", "none"]
            Directions for how environments are considered for selection.
            any: The image may be selected by Connect if not defined in the bundle manifest.
            exact: The image must be defined in the bundle manifest
            none: Never use this environment
        supervisor : str, optional
            Path to the supervisor script
        python : _Installations, optional
            The Python installations available in this environment
        quarto : _Installations, optional
            The Quarto installations available in this environment
        r : _Installations, optional
            The R installations available in this environment
        tensorflow : _Installations, optional
            The Tensorflow installations available in this environment

        Returns
        -------
        Environment | None

        Note
        ----
        This action requires administrator or publisher privileges.
        """

    @overload
    def find_by(self, **conditions) -> Environment | None:
        """Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Returns
        -------
        Environment | None

        Note
        ----
        This action requires administrator or publisher privileges.
        """

    def find_by(self, **conditions) -> Environment | None:
        """Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Returns
        -------
        Environment | None

        Note
        ----
        This action requires administrator or publisher privileges.
        """
        return super().find_by(**conditions)
