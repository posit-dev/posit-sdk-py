from typing import Dict, Literal, Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from .resources import (
    ActiveCreatorMethods,
    ActiveDestroyerMethods,
    ActiveFinderMethods,
    ActiveUpdaterMethods,
)

_Kubernetes = Literal["Kubernetes"]
_Matching = Literal["any", "exact", "none"]
_Installation = TypedDict("_Installation", { 'path': Required[str], 'version': Required[str] })
_Installations = Dict[Literal["installations"], _Installation]


class Environment(ActiveUpdaterMethods, ActiveDestroyerMethods):
    class _UpdateEnvironment(TypedDict, total=False):
        title: Required[str]
        description: NotRequired[Optional[str]]
        matching: NotRequired[Optional[_Matching]]
        supervisor: NotRequired[Optional[str]]
        python: NotRequired[_Installations]
        quarto: NotRequired[_Installations]
        r: NotRequired[_Installations]
        tensorflow: NotRequired[_Installations]

    @overload
    def update(self, /, **attributes: Unpack[_UpdateEnvironment]): ...

    @overload
    def update(self, /, **attributes): ...

    def update(self, /, **attributes):
        return super().update(**attributes)


class Environments(ActiveFinderMethods[Environment], ActiveCreatorMethods[Environment]):
    def __init__(self, ctx, path, pathinfo="environments", uid="guid"):
        super().__init__(ctx, path, pathinfo, uid)

    class _CreateEnvironment(TypedDict):
        title: Required[str]
        description: NotRequired[Optional[str]]
        cluster_name: Required[_Kubernetes]
        name: Required[str]
        matching: NotRequired[Optional[_Matching]]
        supervisor: NotRequired[Optional[str]]
        python: NotRequired[_Installations]
        quarto: NotRequired[_Installations]
        r: NotRequired[_Installations]
        tensorflow: NotRequired[_Installations]

    @overload
    def create(self, **attributes: Unpack[_CreateEnvironment]) -> Environment: ...

    @overload
    def create(self, **attributes) -> Environment: ...

    def create(self, **attributes) -> Environment:
        return super().create(**attributes)

    class _FindByEnvironment(TypedDict):
        title: NotRequired[str]
        description: NotRequired[Optional[str]]
        cluster_name: NotRequired[_Kubernetes]
        name: NotRequired[str]
        matching: NotRequired[Optional[_Matching]]
        supervisor: NotRequired[Optional[str]]
        python: NotRequired[_Installations]
        quarto: NotRequired[_Installations]
        r: NotRequired[_Installations]
        tensorflow: NotRequired[_Installations]

    @overload
    def find_by(self, **conditions: Unpack[_FindByEnvironment]): ...

    @overload
    def find_by(self, **conditions): ...

    def find_by(self, **conditions):
        return super().find_by(**conditions)

    def _create_instance(self, path, pathinfo, /, **attributes):
        return Environment(self._ctx, path, pathinfo, **attributes)
