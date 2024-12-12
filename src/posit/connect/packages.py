from __future__ import annotations

from collections.abc import Mapping, Sized
from typing import Any, Literal, Protocol, SupportsIndex, overload


class _ContentPackage(Mapping[str, Any]):
    pass


class _ContentPackages(Sized, Protocol):
    @overload
    def __getitem__(self, index: SupportsIndex) -> _ContentPackage: ...

    @overload
    def __getitem__(self, index: slice) -> _ContentPackage: ...

    def find_by(
        self,
        *,
        language: Literal["python", "r"] = ...,
        name: str = ...,
        version: str = ...,
        hash: str | None = ...,  # noqa: A002
    ) -> _ContentPackage | None:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
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
        _ContentPackage | None
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...


class _Package(Mapping[str, Any]):
    pass


class _Packages(Sized, Protocol):
    @overload
    def __getitem__(self, index: SupportsIndex) -> _ContentPackage: ...

    @overload
    def __getitem__(self, index: slice) -> _ContentPackage: ...

    def find_by(
        self,
        *,
        language: Literal["python", "r"] = ...,
        name: str = ...,
        version: str = ...,
        hash: str | None = ...,  # noqa: A002,
        bundle_id: str = ...,
        app_id: str = ...,
        app_guid: str = ...,
    ) -> _ContentPackage | None:
        """
        Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        language : {"python", "r"}, not required
            Programming language ecosystem, options are 'python' and 'r'
        name : str, not required
            The package name
        version : str, not required
            The package version
        hash : str or None, optional, not required
            Package description hash for R packages.
        bundle_id: str, not required
            The unique identifier of the bundle this package is associated with.
        app_id: str, not required
            The numerical identifier of the application this package is associated with.
        app_guid: str, not required
            The unique identifier of the application this package is associated with.

        Returns
        -------
        _Package | None
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...
