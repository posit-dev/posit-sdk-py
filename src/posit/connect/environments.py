from typing import Dict, Literal, Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from .resources import (
    ActiveCreatorMethods,
    ActiveDestroyerMethods,
    ActiveFinderMethods,
    ActiveUpdaterMethods,
)


class Environment(ActiveUpdaterMethods, ActiveDestroyerMethods):
    class _UpdateEnvironment(TypedDict, total=False):
        title: Required[str]
        description: NotRequired[Optional[str]]
        matching: NotRequired[Optional[Literal["any", "exact", "none"]]]
        supervisor: NotRequired[Optional[str]]
        python: NotRequired[Dict]
        quarto: NotRequired[Dict]
        r: NotRequired[Dict]
        tensorflow: NotRequired[Dict]

    @overload
    def update(self, /, **attributes: Unpack[_UpdateEnvironment]): ...

    @overload
    def update(self, /, **attributes): ...

    def update(self, /, **attributes):
        return super().update(**attributes)


class Environments(ActiveFinderMethods[Environment], ActiveCreatorMethods[Environment]):
    def __init__(self, ctx, path, pathinfo="environments", uid="guid"):
        super().__init__(ctx, path, pathinfo, uid)

    class _CreateEnvironment(TypedDict, total=False):
        title: Required[str]
        description: NotRequired[Optional[str]]
        cluster_name: Required[Literal["Kubernetes"]]
        name: Required[str]
        matching: NotRequired[Optional[Literal["any", "exact", "none"]]]
        supervisor: NotRequired[Optional[str]]
        python: NotRequired[Dict]
        quarto: NotRequired[Dict]
        r: NotRequired[Dict]
        tensorflow: NotRequired[Dict]

    @overload
    def create(self, **attributes: Unpack[_CreateEnvironment]): ...

    @overload
    def create(self, **attributes): ...

    def create(self, **attributes):
        return super().create(**attributes)

    def _create_instance(self, path, pathinfo, /, **attributes):
        return Environment(self._ctx, path, pathinfo, **attributes)
