"""Group resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, overload

from .paginator import Paginator
from .resources import Resource, Resources

if TYPE_CHECKING:
    import requests

    from posit.connect.context import Context

    from .users import User


class Group(Resource):
    def __init__(self, ctx: Context, **kwargs) -> None:
        super().__init__(ctx.client.resource_params, **kwargs)
        self._ctx: Context = ctx

    @property
    def members(self) -> GroupMembers:
        """Get the group members.

        Returns
        -------
        GroupMembers
            All the users in the group.

        Examples
        --------
        ```python
        group = client.groups.get("GROUP_GUID_HERE")
        group_users = group.members.find()
        group_user_count = group.members.count()
        ```

        """
        return GroupMembers(self._ctx, group_guid=self["guid"])

    def delete(self) -> None:
        """Delete the group."""
        path = f"v1/groups/{self['guid']}"
        url = self._ctx.url + path
        self._ctx.session.delete(url)


class GroupMembers(Resources):
    def __init__(self, ctx: Context, group_guid: str) -> None:
        super().__init__(ctx.client.resource_params)
        self._group_guid = group_guid
        self._ctx: Context = ctx

    def find(self) -> list[User]:
        # Avoid circular import
        from .users import User

        path = f"v1/groups/{self._group_guid}/members"
        url = self._ctx.url + path
        paginator = Paginator(self._ctx.session, url)
        member_dicts = paginator.fetch_results()

        # For each member in the group
        users = [User(self._ctx, **member_dict) for member_dict in member_dicts]
        return users

    def count(self) -> int:
        """Count the number of group members.

        Returns
        -------
        int
        """
        path = f"v1/groups/{self._group_guid}/members"
        url = self._ctx.url + path
        response = self._ctx.session.get(url, params={"page_size": 1})
        result = response.json()
        return result["total"]


class Groups(Resources):
    """Groups resource."""

    def __init__(self, ctx: Context) -> None:
        super().__init__(ctx.client.resource_params)
        self._ctx: Context = ctx

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
        url = self._ctx.url + path
        response = self._ctx.session.post(url, json=kwargs)
        return Group(self._ctx, **response.json())

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
        url = self._ctx.url + path
        paginator = Paginator(self._ctx.session, url, params=kwargs)
        results = paginator.fetch_results()
        return [
            Group(
                self._ctx,
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
        url = self._ctx.url + path
        paginator = Paginator(self._ctx.session, url, params=kwargs)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        groups = (
            Group(
                self._ctx,
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
        url = self._ctx.url + f"v1/groups/{guid}"
        response = self._ctx.session.get(url)
        return Group(
            self._ctx,
            **response.json(),
        )

    def count(self) -> int:
        """Count the number of groups.

        Returns
        -------
        int
        """
        path = "v1/groups"
        url = self._ctx.url + path
        response: requests.Response = self._ctx.session.get(url, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
