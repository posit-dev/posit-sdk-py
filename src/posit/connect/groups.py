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
    def create(self, name: str, *, unique_id: str | None) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None

        Returns
        -------
        Group
        """
        ...

    @overload
    def create(self, *, temp_ticket: str) -> Group:
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
        >>> group = find_one(prefix="example", remote=True)
        >>> groups.create(temp_ticket=group.temp_ticket)
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
        >>> create(name="example")
        >>> create("example", unique_id="00g1a2b3c4d5e6f7g8h9i0j1k2l3m4n5")
        >>> create(temp_ticket="56jhI0rq19Nw4luL")
        """
        ...
        if len(args) == 1 and isinstance(args[0], str):
            body = {"name": args[0], **kwargs}
        elif "temp_ticket" in kwargs:
            body = {"temp_ticket": kwargs["temp_ticket"]}
        else:
            body = kwargs

        path = "v1/groups"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json=body)
        return Group(self.config, self.session, **response.json())

    @overload
    def find(
        self,
        prefix: str = ...,
    ) -> List[Group]:
        """Find groups.

        Parameters
        ----------
        prefix : str, optional
            Filter by group name prefix, by default None

        Returns
        -------
        List[Group]

        Examples
        --------
        >>> find()
        >>> find(prefix="example")
        """
        ...

    @overload
    def find(
        self,
        prefix: str = ...,
        *,
        remote: bool = True,
    ) -> List[Group]:
        """Find groups from a remote authentication provider (LDAP).

        Parameters
        ----------
        prefix : str, optional
            Filter by group name prefix, by default None
        remote : bool, optional
            Use a remote provider, by default True

        Returns
        -------
        List[Group]

        Examples
        --------
        >>> find(remote=True)
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
            params = {"name": args[0], **kwargs}
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
        self,
        prefix: str = ...,
    ) -> Group | None:
        """Find a group.

        Parameters
        ----------
        prefix : str, optional
            Filter by group name prefix, by default None

        Returns
        -------
        Group | None

        Examples
        --------
        >>> find_one()
        >>> find_one(prefix="example")
        """
        ...

    @overload
    def find_one(
        self,
        prefix: str = ...,
        *,
        remote: bool = True,
    ) -> Group | None:
        """Find a group from a remote authentication provider (LDAP).

        Parameters
        ----------
        prefix : str, optional
            Filter by group name prefix, by default None
        remote : bool, optional
            Use a remote provider, by default True

        Returns
        -------
        Group | None

        Examples
        --------
        >>> find_one(remote=True)
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
        >>> find_one(remote=True)
        >>> find_one("example", remote=True)
        >>> find_one(remote=True, prefix="example")
        """
        if len(args) == 1 and isinstance(args[0], str):
            params = {"name": args[0], **kwargs}
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

    def count(self) -> int:
        """Count the number of groups.

        Returns
        -------
        int
        """
        path = "v1/groups"
        url = urls.append(self.config.url, path)
        response: requests.Response = self.session.get(
            url, params={"page_size": 1}
        )
        result: dict = response.json()
        return result["total"]
