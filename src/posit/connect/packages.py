import posixpath
from typing import Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from .resources import Active, ActiveFinderMethods, ActiveSequence


class Package(Active):
    class _Package(TypedDict):
        language: Required[str]
        name: Required[str]
        version: Required[str]
        hash: Required[Optional[str]]

    def __init__(self, ctx, path, /, **attributes: Unpack[_Package]):
        super().__init__(ctx, path, **attributes)


class Packages(ActiveFinderMethods["Package"], ActiveSequence["Package"]):
    """A collection of packages."""

    def __init__(self, ctx, path):
        super().__init__(ctx, path, "name")

    def _create_instance(self, path, /, **attributes):
        return Package(self._ctx, path, **attributes)

    class _FindBy(TypedDict, total=False):
        language: NotRequired[str]
        name: NotRequired[str]
        version: NotRequired[str]
        hash: NotRequired[Optional[str]]

    @overload
    def find_by(self, **conditions: Unpack[_FindBy]):
        ...

    @overload
    def find_by(self, **conditions):
        ...

    def find_by(self, **conditions):
        return super().find_by(**conditions)

class PackagesMixin(Active):
    """Mixin class to add a packages attribute."""

    def __init__(self, ctx, path, /, **attributes):
        """Mixin class which adds a `packages` attribute.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        path : str
            The HTTP path component for the resource endpoint
        **attributes : dict
            Resource attributes passed
        """
        super().__init__(ctx, path, **attributes)

        path = posixpath.join(path, "packages")
        self.packages = Packages(ctx, path)
