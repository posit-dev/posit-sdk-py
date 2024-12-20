"""Package resources."""

from __future__ import annotations

from typing_extensions import (
    Iterable,
    Literal,
    Protocol,
)

from .resources import Resource, ResourceSequence


class ContentPackage(Resource, Protocol):
    pass


class ContentPackages(ResourceSequence[ContentPackage], Protocol):
    def fetch(
        self,
        *,
        language: Literal["python", "r"] = ...,
        name: str = ...,
        version: str = ...,
        hash: str | None = ...,  # noqa: A002
    ) -> Iterable[ContentPackage]:
        """
        Fetch all records matching the specified conditions.

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
        List[ContentPackage]
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...

    def find_by(
        self,
        *,
        language: Literal["python", "r"] = ...,
        name: str = ...,
        version: str = ...,
        hash: str | None = ...,  # noqa: A002
    ) -> ContentPackage | None:
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
        ContentPackage | None
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...


class Package(Resource, Protocol):
    pass


class Packages(ResourceSequence[Package], Protocol):
    def fetch(
        self,
        *,
        language: Literal["python", "r"] = ...,
        name: str = ...,
        version: str = ...,
        hash: str | None = ...,  # noqa: A002,
        bundle_id: str = ...,
        app_id: str = ...,
        app_guid: str = ...,
    ) -> Iterable[Package]:
        """
        Fetch all records matching the specified conditions.

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
        List[Package]
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...

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
    ) -> Package | None:
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
        Package | None
            The first record matching the specified conditions, or `None` if no such record exists.
        """
        ...
