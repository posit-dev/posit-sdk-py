from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Literal, Optional, TypedDict

from typing_extensions import NotRequired, Required, Unpack

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


class Environment(ActiveUpdater, ActiveDestroyer, Active):
    class _Installation(TypedDict):
        """Represents an interpreter installation in an execution environment."""

        path: Required[str]
        """The absolute path to the interpreter's executable."""

        version: Required[str]
        """The semantic version of the interpreter."""

    class _Environment(TypedDict):
        # Identifiers
        id: Required[str]
        """The internal numeric identifier of this environment."""

        guid: Required[str]
        """The unique identifier of this environment to be used with REST API requests."""

        # Timestamps
        created_time: Required[str]
        """The timestamp (RFC3339) indicating when this environment was created."""

        updated_time: Required[str]
        """The timestamp (RFC3339) indicating when this environment was last updated."""

        # Descriptive Information
        title: NotRequired[str]
        """A human-readable title for this environment."""

        description: Required[Optional[str]]
        """A human-readable description of this environment. Defaults to null."""

        # Cluster Information
        cluster_name: Required[str]
        """The cluster identifier for this environment. Always 'Kubernetes' when Off Host Execution is enabled."""

        # Execution Details
        name: Required[str]
        """The container image used when executing content with this environment."""

        environment_type: Required[str]
        """The type of environment. Always 'Kubernetes' when Off Host Execution is enabled."""

        matching: Required[Literal["any", "exact", "none"]]
        """How environments are considered for selection:
        - any: Default. The image can be automatically selected by Connect or targeted in the bundle's manifest.
        - exact: The image must be explicitly asked for in the bundle's manifest.
        - none: The image should never be selected by Posit Connect."""

        supervisor: Required[Optional[str]]
        """The path to the script or command used as the program supervisor when executing content with this environment. Defaults to null."""

        # Installations
        python: Required[Optional[Dict[str, List[Environment._Installation]]]]
        """Available Python installations in this environment."""

        quarto: Optional[Dict[str, List[Environment._Installation]]]
        """Available Quarto installations in this environment."""

        r: Optional[Dict[str, List[Environment._Installation]]]
        """Available R installations in this environment."""

        tensorflow: Optional[Dict[str, List["Environment._Installation"]]]
        """Available TensorFlow installations in this environment."""

    def __init__(self, ctx: Context, path: str, /, **attributes: Unpack[_Environment]):
        super().__init__(ctx, path, **attributes)


class Environments(
    ActiveFinderMethods[Environment],
    ActiveSequenceCreator[Environment],
    ActiveSequence[Environment],
):
    def _create_instance(self, path, /, **attributes) -> Environment:
        return Environment(self._ctx, path, **attributes)
