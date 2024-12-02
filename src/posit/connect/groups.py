"""Group resources."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, overload

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
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")
        group_users = group.members.find()

        # Get count of group members
        group_user_count = group.members.count()
        ```

        """
        return GroupMembers(self._ctx, group_guid=self["guid"])

    def delete(self) -> None:
        """Delete the group.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")

        # Delete the group
        group.delete()
        ```
        """
        path = f"v1/groups/{self['guid']}"
        url = self._ctx.url + path
        self._ctx.session.delete(url)


class GroupMembers(Resources):
    def __init__(self, ctx: Context, group_guid: str) -> None:
        super().__init__(ctx.client.resource_params)
        self._group_guid = group_guid
        self._ctx: Context = ctx

    @overload
    def add(self, *args: User) -> None: ...
    @overload
    def add(self, *, user_guid: str) -> None: ...

    def add(self, *args: User, user_guid: Optional[str] = None) -> None:
        """Add a user to the group.

        Parameters
        ----------
        *args : User
            User objects to add to the group.
        user_guid : str
            The user GUID.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")
        user = client.users.get("USER_GUID_HERE")

        # Add a user to the group
        group.members.add(user)

        # Add multiple users to the group
        users = client.users.find()
        group.members.add(*users)

        # Add a user to the group by GUID
        group.members.add(user_guid="USER_GUID_HERE")
        ```
        """
        if len(args) > 0:
            from .users import User

            if user_guid:
                raise ValueError("Only one of `*args` or `user_guid=` should be provided.")
            for i, user in enumerate(args):
                if not isinstance(user, User):
                    raise ValueError(f"args[{i}] is not a User object.")

            for user in args:
                self.add(user_guid=user["guid"])

            return

        if not isinstance(user_guid, str):
            raise TypeError("`user_guid=` should be a string.")
        if not user_guid:
            raise ValueError("`user_guid=` should not be empty")

        path = f"v1/groups/{self._group_guid}/members"
        url = self._ctx.url + path
        self._ctx.session.post(url, json={"user_guid": user_guid})

    @overload
    def delete(self, *args: User) -> None: ...
    @overload
    def delete(self, *, user_guid: str) -> None: ...

    def delete(self, *args: User, user_guid: Optional[str] = None) -> None:
        """Remove a user from the group.

        Parameters
        ----------
        *args : User
            User objects to remove from the group.
        user_guid : str
            The user GUID.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")

        # Remove a user from the group
        first_user = group.members.find()[0]
        group.members.delete(first_user)

        # Remove multiple users from the group
        group_users = group.members.find()[:2]
        group.members.delete(*group_users)

        # Remove a user from the group by GUID
        group.members.delete(user_guid="USER_GUID_HERE")
        ```

        """
        if len(args) > 0:
            from .users import User

            if user_guid:
                raise ValueError("Only one of `*args` or `user_guid=` should be provided.")
            for i, user in enumerate(args):
                if not isinstance(user, User):
                    raise TypeError(f"`args[{i}]` is not a `User` object.")

            for user in args:
                self.delete(user_guid=user["guid"])

            return

        if not isinstance(user_guid, str):
            raise TypeError("`user_guid=` should be a string.")
        if not user_guid:
            raise ValueError("`user_guid=` should not be empty")

        path = f"v1/groups/{self._group_guid}/members/{user_guid}"
        url = self._ctx.url + path
        self._ctx.session.delete(url)

    def find(self) -> list[User]:
        """Find group members.

        Returns
        -------
        list[User]
            All the users in the group.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")

        # Find all users in the group
        group_users = group.members.find()
        ```
        """
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

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")

        # Get count of group members
        group_user_count = group.members.count()
        ```
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
