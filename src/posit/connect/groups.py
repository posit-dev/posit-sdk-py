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
    def owner_guid(self) -> str:
        return self.get("owner_guid")  # type: ignore

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
    def create(self, name: str, unique_id: str | None) -> Group:
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
    def create(self, *args, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group
        """
        ...

    def create(self, *args, **kwargs) -> Group:
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
        body = dict(*args, **kwargs)
        path = "v1/groups"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json=body)
        return Group(self.config, self.session, **response.json())

    @overload
    def find(
        self,
        prefix: str = ...,
    ) -> List[Group]: ...

    @overload
    def find(self, *args, **kwargs) -> List[Group]: ...

    def find(self, *args, **kwargs):
        """Find groups.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        List[Group]
        """
        params = dict(*args, **kwargs)
        path = "v1/groups"
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
    ) -> Group | None: ...

    @overload
    def find_one(self, *args, **kwargs) -> Group | None: ...

    def find_one(self, *args, **kwargs) -> Group | None:
        """Find one group.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        Group | None
        """
        params = dict(*args, **kwargs)
        path = "v1/groups"
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
