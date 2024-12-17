"""Group resources."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, List, Optional, overload

from .paginator import Paginator
from .resources import BaseResource, Resources

if TYPE_CHECKING:
    import requests

    from .context import Context
    from .users import User


class Group(BaseResource):
    def __init__(self, ctx: Context, **kwargs) -> None:
        super().__init__(ctx, **kwargs)
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
        self._ctx.client.delete(f"v1/groups/{self['guid']}")


class GroupMembers(Resources):
    def __init__(self, ctx: Context, group_guid: str) -> None:
        super().__init__(ctx)
        self._group_guid = group_guid

    @overload
    def add(self, user: User, /) -> None: ...
    @overload
    def add(self, /, *, user_guid: str) -> None: ...

    def add(self, user: Optional[User] = None, /, *, user_guid: Optional[str] = None) -> None:
        """Add a user to the group.

        Parameters
        ----------
        user : User
            User object to add to the group. Only one of `user=` or `user_guid=` can be provided.
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
        for user in users:
            group.members.add(user)

        # Add a user to the group by GUID
        group.members.add(user_guid="USER_GUID_HERE")
        ```

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/groups/-group_guid-/members
        """
        if user is not None:
            from .users import User

            if user_guid:
                raise ValueError("Only one of `user=` or `user_guid=` should be provided.")
            if not isinstance(user, User):
                raise TypeError(f"`user=` is not a `User` object. Received {user}")

            user_guid = user["guid"]

        if not isinstance(user_guid, str):
            raise TypeError(f"`user_guid=` should be a string. Received {user_guid}")
        if not user_guid:
            raise ValueError("`user_guid=` should not be empty.")

        self._ctx.client.post(
            f"v1/groups/{self._group_guid}/members",
            json={"user_guid": user_guid},
        )

    @overload
    def delete(self, user: User, /) -> None: ...
    @overload
    def delete(self, /, *, user_guid: str) -> None: ...

    def delete(self, user: Optional[User] = None, /, *, user_guid: Optional[str] = None) -> None:
        """Remove a user from the group.

        Parameters
        ----------
        user : User
            User object to add to the group. Only one of `user=` or `user_guid=` can be provided.
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
        for group_user in group_users:
            group.members.delete(group_user)

        # Remove a user from the group by GUID
        group.members.delete(user_guid="USER_GUID_HERE")
        ```

        See Also
        --------
        * https://docs.posit.co/connect/api/#delete-/v1/groups/-group_guid-/members/-user_guid-
        """
        if user is not None:
            from .users import User

            if user_guid:
                raise ValueError("Only one of `user=` or `user_guid=` should be provided.")
            if not isinstance(user, User):
                raise TypeError(f"`user=` is not a `User` object. Received {user}")

            user_guid = user["guid"]

        if not isinstance(user_guid, str):
            raise TypeError(f"`user_guid=` should be a string. Received {user_guid}")
        if not user_guid:
            raise ValueError("`user_guid=` should not be empty.")

        self._ctx.client.delete(f"v1/groups/{self._group_guid}/members/{user_guid}")

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

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups/-group_guid-/members
        """
        # Avoid circular import
        from .users import User

        path = f"v1/groups/{self._group_guid}/members"
        paginator = Paginator(self._ctx, path)
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

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups/-group_guid-/members
        """
        response = self._ctx.client.get(
            f"v1/groups/{self._group_guid}/members",
            params={"page_size": 1},
        )
        result = response.json()
        return result["total"]


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

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/groups
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
        response = self._ctx.client.post("v1/groups", json=kwargs)
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

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups
        """
        path = "v1/groups"
        paginator = Paginator(self._ctx, path, params=kwargs)
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

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups
        """
        path = "v1/groups"
        paginator = Paginator(self._ctx, path, params=kwargs)
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

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups
        """
        response = self._ctx.client.get(f"v1/groups/{guid}")
        return Group(
            self._ctx,
            **response.json(),
        )

    def count(self) -> int:
        """Count the number of groups.

        Returns
        -------
        int

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups
        """
        path = "v1/groups"
        response: requests.Response = self._ctx.client.get(path, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
