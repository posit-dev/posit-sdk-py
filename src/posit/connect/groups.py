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
    guid: str | None
        The unique identifier (guid) for the group. If None, the group only exists on the remote authentication server. Use `groups.create(temp_ticket=group.temp_ticket)` to create the group on the Connect server.
    name: str
        A human readable name for the group.
    owner_guid: str | None
        The unique identifier (guid) of the user who owns the group. Always None when retrieved from a remote authentication provider.
    temp_ticket: str | None
        A temporary ticket provided by the remote authentication server for the group. Use to groups.create to create (activate) the group on the Connect server.
    """

    @property
    def guid(self) -> str | None:
        return self.get("guid")

    @property
    def name(self) -> str:
        return self.get("name")  # type: ignore

    @property
    def owner_guid(self) -> str | None:
        return self.get("owner_guid")

    @property
    def temp_ticket(self) -> str | None:
        return self.get("temp_ticket")

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
    def create(self, *, name: str = ..., unique_id: str | None = ...) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str
            The unique identifier field

        Returns
        -------
        Group

        Examples
        --------
        >>> create(name="example)
        >>> create(name="example", unique_id="string")
        """
        ...

    @overload
    def create(self, *, temp_ticket: str) -> Group:
        """Create a group from a remote authentication provider (LDAP).

        Create a group after obtaining a temporary ticket from `remote`.

        Parameters
        ----------
        temp_ticket: str
            The temporary ticket provided by the remote authentication provider.

        Returns
        -------
        Group

        Examples
        --------
        >>> group = find_one(name="example", remote=True)
        >>> create(temp_ticket=group.temp_ticket)
        """
        ...

    @overload
    def create(self, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group
        """
        ...

    def create(self, **kwargs) -> Group:
        """Create a group.

        Create a group using provided information or using a remote
        authentication provider.

        Servers using a remote authentication provider must obtain a temporary
        ticket using the `find` or `find_one` method with `remote` set to `True`.

        Parameters
        ----------
        **kwargs
            Keyword arguments. Can accept:
            - (name: str, unique_id: str | None)
                name: str
                unique_id: str | None
                    The unique identifier field, by default None
            - (temp_ticket: str)
                temp_ticket: str

        Returns
        -------
        Group

        Examples
        --------
        >>> create(name="example)
        >>> create(name="example", unique_id="string")

        Using a remote authentication provider.
        >>> group = find_one(name="example", remote=True)
        >>> create(temp_ticket=group.temp_ticket)
        """
        ...
        method = "POST"
        if "temp_ticket" in kwargs:
            method = "PUT"

        path = "v1/groups"
        url = urls.append(self.config.url, path)
        response = self.session.request(method, url, json=kwargs)
        return Group(self.config, self.session, **response.json())

    @overload
    def find(
        self, *, prefix: str | None = ..., remote: bool = False
    ) -> List[Group]:
        """Find groups.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior. Groups returned by the remote
        authentication provider include a `temp_ticket` field. This field is
        used to create the group on the Connect server.

        Parameters
        ----------
        prefix : str | None, optional
            Filter by group name prefix, by default ...
        remote: bool, optional
            Find a group provided by the remote authentication server, by default False

        Returns
        -------
        List[Group]

        Examples
        --------
        Find groups on the server.
        >>> find()
        >>> find(prefix="example")
        >>> find(prefix="example", remote=False)

        Find groups provided by the remote authentication server.
        >>> find(remote=True)
        >>> find(prefix="example", remote=True)
        """
        ...

    @overload
    def find(self, *, remote: bool = False, **kwargs) -> List[Group]: ...

    def find(self, *, remote: bool = False, **kwargs) -> List[Group]:
        """Find groups.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior. Groups returned by the remote
        authentication provider include a `temp_ticket` field. This field is
        used to create the group on the Connect server.

        Parameters
        ----------
        remote: bool, optional
            Find groups provided by the remote authentication server, by default False
        **kwargs
            Keyword arguments. Can accept:
            - prefix : str | None, optional
                Filter by group name prefix, by default ...

        Returns
        -------
        List[Group]

        Examples
        --------
        Find groups on the server.
        >>> find()
        >>> find(prefix="example")
        >>> find(prefix="example", remote=False)

        Find groups provided by the remote authentication server.
        >>> find(remote=True)
        >>> find(prefix="example", remote=True)
        """
        # set path to 'v1/groups/remote' if remote is True
        path = "v1/groups" if not remote else "v1/groups/remote"
        url = urls.append(self.config.url, path)
        paginator = Paginator(self.session, url, params=kwargs)
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
        self, *, prefix: str = ..., remote: bool = False
    ) -> Group | None:
        """Find a group.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior. Groups returned by the remote
        authentication provider include a `temp_ticket` field. This field is
        used to create the group on the Connect server.

        Parameters
        ----------
        prefix : str | None, optional
            Filter by group name prefix, by default ...
        remote: bool, optional
            Find a group provided by the remote authentication server, by default False

        Returns
        -------
        Group | None

        Examples
        --------
        Find a group on the server.
        >>> find_one()
        >>> find_one(prefix="example")
        >>> find_one(prefix="example", remote=False)

        Find a group provided by the remote authentication server.
        >>> find_one(remote=True)
        >>> find_one(prefix="example", remote=True)
        """
        ...

    @overload
    def find_one(self, *, remote: bool = False, **kwargs) -> Group | None: ...

    def find_one(self, *, remote: bool = False, **kwargs) -> Group | None:
        """Find a group.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior. Groups returned by the remote
        authentication provider include a `temp_ticket` field. This field is
        used to create the group on the Connect server.

        Parameters
        ----------
        remote: bool, optional
            Find a group provided by the remote authentication server, by default False
        **kwargs
            Keyword arguments. Can accept:
            - prefix : str | None, optional
                Filter by group name prefix, by default ...

        Returns
        -------
        Group | None

        Examples
        --------
        Find a group on the server.
        >>> find_one()
        >>> find_one(prefix="example")
        >>> find_one(prefix="example", remote=False)

        Find a group provided by the remote authentication server.
        >>> find_one(remote=True)
        >>> find_one(prefix="example", remote=True)
        """
        # set path to 'v1/groups/remote' if remote is True
        path = "v1/groups" if not remote else "v1/groups/remote"
        url = urls.append(self.config.url, path)
        paginator = Paginator(self.session, url, params=kwargs)
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
    def count(self, *, prefix: str = ..., remote: bool = False) -> int:
        """Cound the number of groups.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior.

        Parameters
        ----------
        prefix : str | None, optional
                Filter by group name prefix, by default ...
        remote: bool, optional
            Count groups provided by the remote authentication server, by default False

        Returns
        -------
        int

        Examples
        --------
        Find a group on the server.
        >>> count()
        >>> count(prefix="example")
        >>> count(prefix="example", remote=False)

        Find a group provided by the remote authentication server.
        >>> count(remote=True)
        >>> count(prefix="example", remote=True)
        """
        ...

    @overload
    def count(self, remote: bool = False, **kwargs) -> int: ...

    def count(self, remote: bool = False, **kwargs) -> int:
        """Cound the number of groups.

        Connect servers configured with a remote authentication provider may
        search against the remote provider via the `remote` argument. Set
        remote=True to enable this behavior.

        Parameters
        ----------
        remote: bool, optional
            Count groups provided by the remote authentication server, by default False
        **kwargs
            Keyword arguments. Can accept:
            - prefix : str | None, optional
                Filter by group name prefix, by default ...

        Returns
        -------
        int

        Examples
        --------
        Find a group on the server.
        >>> count()
        >>> count(prefix="example")
        >>> count(prefix="example", remote=False)

        Find a group provided by the remote authentication server.
        >>> count(remote=True)
        >>> count(prefix="example", remote=True)
        """
        # set path to 'v1/groups/remote' if remote is True
        path = "v1/groups" if not remote else "v1/groups/remote"
        url = urls.append(self.config.url, path)
        params = {**kwargs, "page_size": 1}
        response = self.session.get(url, params=params)
        result = response.json()
        return result["total"]
