"""Group resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, overload

from .paginator import Paginator
from .resources import Resource, Resources

if TYPE_CHECKING:
    import requests


class Group(Resource):
    def delete(self) -> None:
        """Delete the group."""
        path = f"v1/groups/{self['guid']}"
        url = self.params.url + path
        self.params.session.delete(url)


class Groups(Resources):
    """Groups resource."""

    @overload
    def create(self, *, name: str, unique_id: str | None) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None

        Returns
        -------
        Group
        """

    @overload
    def create(self, **kwargs) -> Group:
        """Create a group.

        Returns
        -------
        Group
        """

    def create(self, **kwargs) -> Group:
        """Create a group.

        Parameters
        ----------
        name: str
        unique_id: str | None

        Returns
        -------
        Group
        """
        path = "v1/groups"
        url = self.params.url + path
        response = self.params.session.post(url, json=kwargs)
        return Group(self.params, **response.json())

    @overload
    def find(
        self,
        *,
        prefix: str = ...,
    ) -> List[Group]: ...

    @overload
    def find(self, **kwargs) -> List[Group]: ...

    def find(self, **kwargs):
        """Find groups.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        List[Group]
        """
        path = "v1/groups"
        url = self.params.url + path
        paginator = Paginator(self.params.session, url, params=kwargs)
        results = paginator.fetch_results()
        return [
            Group(
                self.params,
                **result,
            )
            for result in results
        ]

    @overload
    def find_one(
        self,
        *,
        prefix: str = ...,
    ) -> Group | None: ...

    @overload
    def find_one(self, **kwargs) -> Group | None: ...

    def find_one(self, **kwargs) -> Group | None:
        """Find one group.

        Parameters
        ----------
        prefix: str
            Filter by group name prefix. Casing is ignored.

        Returns
        -------
        Group | None
        """
        path = "v1/groups"
        url = self.params.url + path
        paginator = Paginator(self.params.session, url, params=kwargs)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        groups = (
            Group(
                self.params,
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
        url = self.params.url + f"v1/groups/{guid}"
        response = self.params.session.get(url)
        return Group(
            self.params,
            **response.json(),
        )

    def count(self) -> int:
        """Count the number of groups.

        Returns
        -------
        int
        """
        path = "v1/groups"
        url = self.params.url + path
        response: requests.Response = self.params.session.get(url, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
