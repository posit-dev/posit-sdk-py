from __future__ import annotations

import posixpath
from typing import Generator, Literal, Optional, TypedDict

from typing_extensions import NotRequired, Required, Unpack

from posit.connect.context import requires
from posit.connect.errors import ClientError
from posit.connect.paginator import Paginator

from .resources import Active, ActiveFinderMethods, ActiveSequence


class ContentPackage(Active):
    class _Package(TypedDict):
        language: Required[str]
        name: Required[str]
        version: Required[str]
        hash: Required[Optional[str]]

    def __init__(self, ctx, /, **attributes: Unpack[_Package]):
        # todo - passing "" is a hack since path isn't needed. Instead, this class should inherit from Resource, but ActiveSequence is designed to operate on Active. That should change.
        super().__init__(ctx, "", **attributes)


class ContentPackages(ActiveFinderMethods["ContentPackage"], ActiveSequence["ContentPackage"]):
    """A collection of packages."""

    def __init__(self, ctx, path):
        super().__init__(ctx, path, "name")

    def _create_instance(self, path, /, **attributes):  # noqa: ARG002
        return ContentPackage(self._ctx, **attributes)

    def fetch(self, **conditions):
        try:
            return super().fetch(**conditions)
        except ClientError as e:
            if e.http_status == 204:
                return []
            raise e

    def find(self, uid):
        raise NotImplementedError("The 'find' method is not support by the Packages API.")

    class _FindBy(TypedDict, total=False):
        language: NotRequired[Literal["python", "r"]]
        """Programming language ecosystem, options are 'python' and 'r'"""

        name: NotRequired[str]
        """The package name"""

        version: NotRequired[str]
        """The package version"""

        hash: NotRequired[Optional[str]]
        """Package description hash for R packages."""

    def find_by(self, **conditions: Unpack[_FindBy]):  # type: ignore
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Unpack[_FindBy]
            Conditions for filtering packages. The following keys are accepted:

        language : {"python", "r"}, not required
            Programming language ecosystem, options are 'python' and 'r'

        name : str, not required
            The package name

        version : str, not required
            The package version

        hash : str or None, optional, not required
            Package description hash for R packages.

        Returns
        -------
        Optional[T]
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        return super().find_by(**conditions)


class ContentPackagesMixin(Active):
    """Mixin class to add a packages attribute."""

    @property
    @requires(version="2024.10.0-dev")
    def packages(self):
        path = posixpath.join(self._path, "packages")
        return ContentPackages(self._ctx, path)


class Package(Active):
    class _Package(TypedDict):
        language: Required[Literal["python", "r"]]
        """Programming language ecosystem, options are 'python' and 'r'"""

        language_version: Required[str]
        """Programming language version"""

        name: Required[str]
        """The package name"""

        version: Required[str]
        """The package version"""

        hash: Required[Optional[str]]
        """Package description hash for R packages."""

        bundle_id: Required[str]
        """The unique identifier of the bundle this package is associated with"""

        app_id: Required[str]
        """The numerical identifier of the application this package is associated with"""

        app_guid: Required[str]
        """The unique identifier of the application this package is associated with"""

    def __init__(self, ctx, /, **attributes: Unpack[_Package]):
        # todo - passing "" is a hack since path isn't needed. Instead, this class should inherit from Resource, but ActiveSequence is designed to operate on Active. That should change.
        super().__init__(ctx, "", **attributes)


class Packages(ActiveFinderMethods["Package"], ActiveSequence["Package"]):
    def __init__(self, ctx, path):
        super().__init__(ctx, path, "name")

    def _create_instance(self, path, /, **attributes):  # noqa: ARG002
        return Package(self._ctx, **attributes)

    class _Fetch(TypedDict, total=False):
        language: Required[Literal["python", "r"]]
        """Programming language ecosystem, options are 'python' and 'r'"""

        name: Required[str]
        """The package name"""

        version: Required[str]
        """The package version"""

    def fetch(self, **conditions: Unpack[_Fetch]) -> Generator["Package"]:  # type: ignore
        # todo - add pagination support to ActiveSequence
        url = self._ctx.url + self._path
        paginator = Paginator(self._ctx.session, url, dict(**conditions))
        for page in paginator.fetch_pages():
            results = page.results
            yield from (self._create_instance("", **result) for result in results)

    def find(self, uid):
        raise NotImplementedError("The 'find' method is not support by the Packages API.")

    class _FindBy(TypedDict, total=False):
        language: NotRequired[Literal["python", "r"]]
        """Programming language ecosystem, options are 'python' and 'r'"""

        language_version: NotRequired[str]
        """Programming language version"""

        name: NotRequired[str]
        """The package name"""

        version: NotRequired[str]
        """The package version"""

        hash: NotRequired[Optional[str]]
        """Package description hash for R packages."""

        bundle_id: NotRequired[str]
        """The unique identifier of the bundle this package is associated with"""

        app_id: NotRequired[str]
        """The numerical identifier of the application this package is associated with"""

        app_guid: NotRequired[str]
        """The unique identifier of the application this package is associated with"""

    def find_by(self, **conditions: Unpack[_FindBy]) -> "Package | None":  # type: ignore
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        **conditions : Unpack[_FindBy]
            Conditions for filtering packages. The following keys are accepted:

        language : {"python", "r"}, not required
            Programming language ecosystem, options are 'python' and 'r'

        name : str, not required
            The package name

        version : str, not required
            The package version

        hash : str or None, optional, not required
            Package description hash for R packages.

        Returns
        -------
        Optional[Package]
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        return super().find_by(**conditions)
