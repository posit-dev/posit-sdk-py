"""Group resources."""

from __future__ import annotations
from typing import List, overload

import requests

from . import me, urls

from .config import Config
from .paginator import Paginator
from .resources import Resource, Resources


class Group(Resource):
    """Group resource.

    Attributes
    ----------
    guid : str
    name: str
    owner_guid: str
    """

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def name(self) -> str:
        return self.get("name")  # type: ignore

    @property
    def owner_guid(self) -> str | None:
        return self.get("owner_guid")  # type: ignore

    @property
    def temp_ticket(self) -> str | None:
        return self.get("temp_ticket")  # type: ignore

    # CRUD Methods

    def delete(self) -> None:
        """Delete the group."""
        path = f"v1/groups/{self.guid}"
        url = urls.append(self.config.url, path)
        self.session.delete(url)


class Groups(Resources):
    """Groups resource."""

    def __init__(self, config: Config, session: requests.Session) -> None:
        self.config = config
        self.session = session

    @overload
    def create(
        self, name: str, *, unique_id: str | None = None, **kwargs
    ) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None
            The unique identifier field, by default None

        Returns
        -------
        Group

        Examples
        --------
        >>> create("example")
        >>> create("example", unique_id="string")
        >>> create(name="example)
        >>> create(name="example", unique_id="string")
        """
        ...

    @overload
    def create(self, *, temp_ticket: str, **kwargs) -> Group:
        """Create a group from a remote authentication provider (LDAP).

        Create a group after obtaining a temporary ticket from `remote`.

        Parameters
        ----------
        temp_ticket: str

        Returns
        -------
        Group

        Examples
        --------
        >>> group = find_one("example", remote=True)
        >>> create(temp_ticket=group.temp_ticket)
        """
        ...

    @overload
    def create(self, *args, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group
        """
        ...

    def create(self, *args, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group

        Examples
        --------
        >>> create("example")
        >>> create("example", unique_id="string")
        >>> create(name="example)
        >>> create(name="example", unique_id="string")
        >>> create(temp_ticket="56jhI0rq19Nw4luL")
        """
        ...
        if len(args) == 1 and isinstance(args[0], str):
            body = {"name": args[0], **kwargs}
        else:
            body = kwargs

        path = "v1/groups"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json=body)
        return Group(self.config, self.session, **response.json())

    @overload
    def find(
        self, prefix: str = ..., *, remote: bool = False, **kwargs
    ) -> List[Group]:
        """Find groups.

        Parameters
        ----------
        prefix : str,
            Filter by group name prefix
        remote : bool, optional
            Use a remote provider, by default False

        Returns
        -------
        List[Group]

        Examples
        --------
        >>> find()
        >>> find("example")
        >>> find(prefix="example")

        Find groups from a remote authentication provider (LDAP).
        >>> find(remote=True)
        >>> find("example", remote=True)
        >>> find(prefix="example", remote=True)
        """
        ...

    @overload
    def find(self, *args, **kwargs) -> List[Group]: ...

    def find(self, *args, **kwargs) -> List[Group]:
        """Find groups.

        Set remote=True to find groups from a remote authentication provider (LDAP).

        Returns
        -------
        List[Group]

        Examples
        --------
        >>> find()
        >>> find("example")
        >>> find(prefix="example")
        >>> find(remote=True)
        >>> find("example", remote=True)
        >>> find(remote=True, prefix="example")
        """
        if len(args) == 1 and isinstance(args[0], str):
            params = {"prefix": args[0], **kwargs}
        else:
            params = kwargs

        # set path to 'v1/groups/remote' if remote is True
        path = "v1/groups"
        if "remote" in params:
            if params["remote"]:
                path = "v1/groups/remote"
            del params["remote"]

        url = urls.append(self.config.url, path)
        paginator = Paginator(self.session, url, params=params)
        results = paginator.fetch_results()
        return [
            Group(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in results
        ]

    @overload
    def find_one(
        self, prefix: str = ..., *, remote: bool = False, **kwargs
    ) -> Group | None:
        """Find groups.

        Parameters
        ----------
        prefix : str,
            Filter by group name prefix
        remote : bool, optional
            Use a remote provider, by default False

        Returns
        -------
        Group | None

        Examples
        --------
        >>> find_one()
        >>> find_one("example")
        >>> find_one(prefix="example")

        Find groups from a remote authentication provider (LDAP).
        >>> find_one(remote=True)
        >>> find_one("example", remote=True)
        >>> find_one(prefix="example", remote=True)
        """
        ...

    @overload
    def find_one(self, *args, **kwargs) -> Group | None: ...

    def find_one(self, *args, **kwargs) -> Group | None:
        """Find a groups.

        Set remote=True to find groups from a remote authentication provider (LDAP).

        Returns
        -------
        Group | None

        Examples
        --------
        >>> find_one()
        >>> find_one("example")
        >>> find_one(prefix="example")

        Find groups from a remote authentication provider (LDAP).
        >>> find_one(remote=True)
        >>> find_one("example", remote=True)
        >>> find_one(prefix="example", remote=True)
        """
        if len(args) == 1 and isinstance(args[0], str):
            params = {"prefix": args[0], **kwargs}
        else:
            params = kwargs

        # set path to 'v1/groups/remote' if remote is True
        path = "v1/groups"
        if "remote" in params:
            if params["remote"]:
                path = "v1/groups/remote"
            del params["remote"]

        url = urls.append(self.config.url, path)
        paginator = Paginator(self.session, url, params=params)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        groups = (
            Group(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in results
        )
        return next(groups, None)

    def get(self, guid: str) -> Group:
        """Get group.

        Parameters
        ----------
        guid : str

        Returns
        -------
        Group
        """
        url = urls.append(self.config.url, f"v1/groups/{guid}")
        response = self.session.get(url)
        return Group(
            config=self.config,
            session=self.session,
            **response.json(),
        )

    @overload
    def count(
        self, prefix: str = ..., *, remote: bool = False, **kwargs
    ) -> int:
        """Count the number of groups.

        Parameters
        ----------
        prefix : str
        remote: bool
            Use a remote provider, by defualt False

        Returns
        -------
        int
            The number of groups.

        Examples
        --------
        >>> count()
        >>> count("example")
        >>> count(prefix="example")

        Count the number of groups from a remote authentication provider (LDAP).
        >>> count(remote=True)
        >>> count("example", remote=True)
        >>> count(prefix="example", remote=True)
        """
        ...

    @overload
    def count(self, *args, **kwargs) -> int: ...

    def count(self, *args, **kwargs) -> int:
        """Count the number of groups.

        Set remote=True to count groups from a remote authentication provider (LDAP).

        Returns
        -------
        int
            The number of groups.

        Examples
        --------
        >>> count()
        >>> count("example")
        >>> count(prefix="example")

        Count the number of groups from a remote authentication provider (LDAP).
        >>> count(remote=True)
        >>> count("example", remote=True)
        >>> count(prefix="example", remote=True)
        """
        if len(args) == 1 and isinstance(args[0], str):
            params = {"prefix": args[0], **kwargs}
        else:
            params = kwargs

        path = "v1/groups"
        if "remote" in params:
            if params["remote"]:
                path = "v1/groups/remote"
            del params["remote"]

        url = urls.append(self.config.url, path)
        response: requests.Response = self.session.get(
            url, params={**params, "page_size": 1}
        )
        result: dict = response.json()
        return result["total"]
