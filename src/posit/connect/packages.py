import posixpath
from typing import Literal, Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from posit.connect.context import requires
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

    def _create_instance(self, path, /, **attributes):
        return ContentPackage(self._ctx, **attributes)

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

    @overload
    def find_by(self, **conditions: Unpack[_FindBy]):
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

    @overload
    def find_by(self, **conditions): ...

    def find_by(self, **conditions):
        return super().find_by(**conditions)


class ContentPackagesMixin(Active):
    """Mixin class to add a packages attribute."""

    @property
    @requires(version="2024.11.0")
    def packages(self):
        path = posixpath.join(self._path, "packages")
        return ContentPackages(self._ctx, path)


class GlobalPackage(Active):
    class _GlobalPackage(TypedDict):
        language: Required[str]
        name: Required[str]
        version: Required[str]
        hash: Required[Optional[str]]

    def __init__(self, ctx, /, **attributes: Unpack[_GlobalPackage]):
        # todo - passing "" is a hack since path isn't needed. Instead, this class should inherit from Resource, but ActiveSequence is designed to operate on Active. That should change.
        super().__init__(ctx, "", **attributes)


class GlobalPackages(ContentPackages):
    def __init__(self, ctx, path):
        super().__init__(ctx, path, "name")

    def _create_instance(self, path, /, **attributes):
        return ContentPackage(self._ctx, **attributes)

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

    def fetch(self, **conditions):
        url = self._ctx.url + self._path
        paginator = Paginator(self._ctx.session, url, conditions)
        results = paginator.fetch_results()
        return [self._create_instance("", **result) for result in results]

    @overload
    def find_by(self, **conditions: Unpack[_FindBy]):
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

    @overload
    def find_by(self, **conditions): ...

    def find_by(self, **conditions):
        return super().find_by(**conditions)
