"""User resources."""

from __future__ import annotations

from typing_extensions import (
    TYPE_CHECKING,
    List,
    Literal,
    NotRequired,
    Required,
    TypedDict,
    Unpack,
)

from . import me
from .content import Content
from .paginator import Paginator
from .resources import BaseResource, Resources

if TYPE_CHECKING:
    from .context import Context
    from .groups import Group


class User(BaseResource):
    @property
    def content(self) -> Content:
        return Content(self._ctx, owner_guid=self["guid"])

    def lock(self, *, force: bool = False):
        """
        Lock the user account.

        You cannot unlock your own account unless you have administrative privileges. Once an account is locked, only an admin can unlock it.

        Parameters
        ----------
        force : bool, optional
            If `True`, overrides lock protection allowing a user to lock their own account. Default is `False`.

        Returns
        -------
        None

        Examples
        --------
        Lock another user's account:

        >>> user.lock()

        Attempt to lock your own account (will raise `RuntimeError` unless `force` is set to `True`):

        >>> user.lock(force=True)

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/users/-guid-/lock
        """
        _me = me.get(self._ctx)
        if _me["guid"] == self["guid"] and not force:
            raise RuntimeError(
                "You cannot lock your own account. Set force=True to override this behavior.",
            )
        body = {"locked": True}
        self._ctx.client.post(f"v1/users/{self['guid']}/lock", json=body)
        super().update(locked=True)

    def unlock(self):
        """
        Unlock the user account.

        This method unlocks the specified user's account. You must have administrative privileges to unlock accounts other than your own.

        Returns
        -------
        None

        Examples
        --------
        Unlock a user's account:

        >>> user.unlock()

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/users/-guid-/lock
        """
        body = {"locked": False}
        self._ctx.client.post(f"v1/users/{self['guid']}/lock", json=body)
        super().update(locked=False)

    class UpdateUser(TypedDict):
        """Update user request."""

        email: NotRequired[str]
        username: NotRequired[str]
        first_name: NotRequired[str]
        last_name: NotRequired[str]
        user_role: NotRequired[Literal["administrator", "publisher", "viewer"]]

    def update(
        self,
        **kwargs: Unpack[UpdateUser],
    ) -> None:
        """
        Update the user's attributes.

        Parameters
        ----------
        email : str, not required
            The new email address for the user. Default is `None`.
        username : str, not required
            The new username for the user. Default is `None`.
        first_name : str, not required
            The new first name for the user. Default is `None`.
        last_name : str, not required
            The new last name for the user. Default is `None`.
        user_role : Literal["administrator", "publisher", "viewer"], not required
            The new role for the user. Options are `'administrator'`, `'publisher'`, `'viewer'`. Default is `None`.

        Returns
        -------
        None

        Examples
        --------
        Update the user's email and role:

        >>> user.update(email="newemail@example.com", user_role="publisher")

        Update the user's first and last name:

        >>> user.update(first_name="Jane", last_name="Smith")

        See Also
        --------
        * https://docs.posit.co/connect/api/#put-/v1/users/-guid-
        """
        response = self._ctx.client.put(f"v1/users/{self['guid']}", json=kwargs)
        super().update(**response.json())

    @property
    def groups(self) -> UserGroups:
        """
        Retrieve the groups to which the user belongs.

        Returns
        -------
        UserGroups
            Helper class that returns the groups of which the user is a member.

        Examples
        --------
        Retrieve the groups to which the user belongs:

        ```python
        user = client.users.get("USER_GUID_HERE")
        groups = user.groups.find()
        ```
        """
        return UserGroups(self._ctx, self["guid"])


class UserGroups(Resources):
    def __init__(self, ctx: Context, user_guid: str) -> None:
        super().__init__(ctx)
        self._ctx: Context = ctx
        self._user_guid: str = user_guid

    def add(self, group: str | Group) -> None:
        """
        Add the user to the specified group.

        Parameters
        ----------
        group : str | Group
            The group guid or `Group` object to which the user will be added.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")
        user = client.users.get("USER_GUID_HERE")

        # Add the user to the group
        user.groups.add(group)

        # Add the user to multiple groups
        groups = [
            client.groups.get("GROUP_GUID_1"),
            client.groups.get("GROUP_GUID_2"),
        ]
        for group in groups:
            user.groups.add(group)

        # Add the user to a group by GUID
        user.groups.add("GROUP_GUID_HERE")
        ```

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/groups/-group_guid-/members
        """
        from .groups import Group

        if isinstance(group, Group):
            group.members.add(user_guid=self._user_guid)
            return

        if not isinstance(group, str):
            raise TypeError(f"`group=` must be a `str | Group`. Received {group}")
        if not group:
            raise ValueError("`group=` must not be empty.")

        group_obj = self._ctx.client.groups.get(group)
        group_obj.members.add(user_guid=self._user_guid)

    def delete(self, group: str | Group) -> None:
        """
        Remove the user from the specified group.

        Parameters
        ----------
        group : str | Group
            The group to which the user will be added.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        group = client.groups.get("GROUP_GUID_HERE")
        user = client.users.get("USER_GUID_HERE")

        # Remove the user from the group
        user.groups.delete(group)

        # Remove the user from multiple groups
        groups = [
            client.groups.get("GROUP_GUID_1"),
            client.groups.get("GROUP_GUID_2"),
        ]
        for group in groups:
            user.groups.delete(group)

        # Remove the user from a group by GUID
        user.groups.delete("GROUP_GUID_HERE")
        ```

        See Also
        --------
        * https://docs.posit.co/connect/api/#delete-/v1/groups/-group_guid-/members/-user_guid-
        """
        from .groups import Group

        if isinstance(group, Group):
            group.members.delete(user_guid=self._user_guid)
            return

        if not isinstance(group, str):
            raise TypeError(f"`group=` must be a `str | Group`. Received {group}")
        if not group:
            raise ValueError("`group=` must not be empty.")

        group_obj = self._ctx.client.groups.get(group)
        group_obj.members.delete(user_guid=self._user_guid)

    def find(self) -> List[Group]:
        """
        Retrieve the groups to which the user belongs.

        Returns
        -------
        List[Group]
            A list of groups to which the user belongs.

        Examples
        --------
        ```python
        from posit.connect import Client

        client = Client("https://posit.example.com", "API_KEY")

        user = client.users.get("USER_GUID_HERE")
        groups = user.groups.find()
        ```

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/groups/-group_guid-/members
        """
        self_groups: list[Group] = []
        for group in self._ctx.client.groups.find():
            group_users = group.members.find()
            for group_user in group_users:
                if group_user["guid"] == self._user_guid:
                    self_groups.append(group)

        return self_groups


class Users(Resources):
    """Users resource."""

    class CreateUser(TypedDict):
        """Create user request."""

        username: Required[str]
        # Authentication Information
        password: NotRequired[str]
        user_must_set_password: NotRequired[bool]
        # Profile Information
        email: NotRequired[str]
        first_name: NotRequired[str]
        last_name: NotRequired[str]
        # Role and Permissions
        user_role: NotRequired[Literal["administrator", "publisher", "viewer"]]
        unique_id: NotRequired[str]

    def create(self, **attributes: Unpack[CreateUser]) -> User:
        """
        Create a new user with the specified attributes.

        Applies when server setting 'Authentication.Provider' is set to 'ldap', 'oauth2', 'pam', 'password', 'proxy', or 'saml'.

        Parameters
        ----------
        username : str, required
            The user's desired username.
        password : str, not required
            Applies when server setting 'Authentication.Provider="password"'. Cannot be set when `user_must_set_password` is `True`.
        user_must_set_password : bool, not required
            If `True`, the user is prompted to set their password on first login. When `False`, the `password` parameter is used. Default is `False`. Applies when server setting 'Authentication.Provider="password"'.
        email : str, not required
            The user's email address.
        first_name : str, not required
            The user's first name.
        last_name : str, not required
            The user's last name.
        user_role : Literal["administrator", "publisher", "viewer"], not required
            The user role.  Options are `'administrator'`, `'publisher'`, `'viewer'`. Falls back to server setting 'Authorization.DefaultUserRole'.
        unique_id : str, maybe required
            Required when server is configured with SAML or OAuth2 (non-Google) authentication. Applies when server setting `ProxyAuth.UniqueIdHeader` is set.

        Returns
        -------
        User
            The newly created user.

        Examples
        --------
        Create a user with a predefined password:

        >>> user = client.create(
        ...     username="jdoe",
        ...     email="jdoe@example.com",
        ...     first_name="John",
        ...     last_name="Doe",
        ...     password="s3cur3p@ssword",
        ...     user_role="viewer",
        ... )

        Create a user who must set their own password:

        >>> user = client.create(
        ...     username="jdoe",
        ...     email="jdoe@example.com",
        ...     first_name="John",
        ...     last_name="Doe",
        ...     user_must_set_password=True,
        ...     user_role="viewer",
        ... )

        See Also
        --------
        * https://docs.posit.co/connect/api/#post-/v1/users
        """
        # todo - use the 'context' module to inspect the 'authentication' object and route to POST (local) or PUT (remote).
        response = self._ctx.client.post("v1/users", json=attributes)
        return User(self._ctx, **response.json())

    class FindUser(TypedDict):
        """Find user request."""

        prefix: NotRequired[str]
        user_role: NotRequired[Literal["administrator", "publisher", "viewer"] | str]
        account_status: NotRequired[Literal["locked", "licensed", "inactive"] | str]

    def find(self, **conditions: Unpack[FindUser]) -> List[User]:
        """
        Find users matching the specified conditions.

        Parameters
        ----------
        prefix : str, not required
            Filter users by prefix (username, first name, or last name). The filter is case-insensitive.
        user_role : Literal["administrator", "publisher", "viewer"], not required
            Filter by user role. Options are `'administrator'`, `'publisher'`, `'viewer'`. Use `'|'` to represent logical OR (e.g., `'viewer|publisher'`).
        account_status : Literal["locked", "licensed", "inactive"], not required
            Filter by account status. Options are `'locked'`, `'licensed'`, `'inactive'`. Use `'|'` to represent logical OR. For example, `'locked|licensed'` includes users who are either locked or licensed.

        Returns
        -------
        List[User]
            A list of users matching the specified conditions.

        Examples
        --------
        Find all users with a username, first name, or last name starting with 'jo':

        >>> users = client.find(prefix="jo")

        Find all users who are either viewers or publishers:

        >>> users = client.find(user_role="viewer|publisher")

        Find all users who are locked or licensed:

        >>> users = client.find(account_status="locked|licensed")

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/users
        """
        path = "v1/users"
        paginator = Paginator(self._ctx, path, params={**conditions})
        results = paginator.fetch_results()
        return [
            User(
                self._ctx,
                **user,
            )
            for user in results
        ]

    def find_one(self, **conditions: Unpack[FindUser]) -> User | None:
        """
        Find a user matching the specified conditions.

        Parameters
        ----------
        prefix : str, optional
            Filter users by prefix (username, first name, or last name). The filter is case-insensitive. Default is `None`.
        user_role : Literal["administrator", "publisher", "viewer"], optional
            Filter by user role. Options are `'administrator'`, `'publisher'`, `'viewer'`. Use `'|'` to represent logical OR (e.g., `'viewer|publisher'`). Default is `None`.
        account_status : Literal["locked", "licensed", "inactive"], optional
            Filter by account status. Options are `'locked'`, `'licensed'`, `'inactive'`. Use `'|'` to represent logical OR. For example, `'locked|licensed'` includes users who are either locked or licensed. Default is `None`.

        Returns
        -------
        User or None
            The first user matching the specified conditions, or `None` if no user is found.

        Examples
        --------
        Find a user with a username, first name, or last name starting with 'jo':

        >>> user = client.find_one(prefix="jo")

        Find a user who is either a viewer or publisher:

        >>> user = client.find_one(user_role="viewer|publisher")

        Find a user who is locked or licensed:

        >>> user = client.find_one(account_status="locked|licensed")

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/users
        """
        path = "v1/users"
        paginator = Paginator(self._ctx, path, params={**conditions})
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        users = (
            User(
                self._ctx,
                **result,
            )
            for result in results
        )
        return next(users, None)

    def get(self, uid: str) -> User:
        """
        Retrieve a user by their unique identifier (guid).

        Parameters
        ----------
        uid : str
            The unique identifier (guid) of the user to retrieve.

        Returns
        -------
        User

        Examples
        --------
        >>> user = client.get("123e4567-e89b-12d3-a456-426614174000")

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/users
        """
        response = self._ctx.client.get(f"v1/users/{uid}")
        return User(
            self._ctx,
            **response.json(),
        )

    def count(self) -> int:
        """
        Return the total number of users.

        Returns
        -------
        int

        See Also
        --------
        * https://docs.posit.co/connect/api/#get-/v1/users
        """
        response = self._ctx.client.get("v1/users", params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
