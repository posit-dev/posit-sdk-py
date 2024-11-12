"""User resources."""

from __future__ import annotations

from typing import List, Literal

from typing_extensions import NotRequired, Required, TypedDict, Unpack

from . import me
from .content import Content
from .paginator import Paginator
from .resources import Resource, ResourceParameters, Resources


class User(Resource):
    @property
    def content(self) -> Content:
        return Content(self.params, owner_guid=self["guid"])

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
        """
        _me = me.get(self.params)
        if _me["guid"] == self["guid"] and not force:
            raise RuntimeError(
                "You cannot lock your own account. Set force=True to override this behavior.",
            )
        url = self.params.url + f"v1/users/{self['guid']}/lock"
        body = {"locked": True}
        self.params.session.post(url, json=body)
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
        """
        url = self.params.url + f"v1/users/{self['guid']}/lock"
        body = {"locked": False}
        self.params.session.post(url, json=body)
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
        """
        url = self.params.url + f"v1/users/{self['guid']}"
        response = self.params.session.put(url, json=kwargs)
        super().update(**response.json())


class Users(Resources):
    """Users resource."""

    def __init__(self, params: ResourceParameters) -> None:
        super().__init__(params)

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
        """
        # todo - use the 'context' module to inspect the 'authentication' object and route to POST (local) or PUT (remote).
        url = self.params.url + "v1/users"
        response = self.params.session.post(url, json=attributes)
        return User(self.params, **response.json())

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
        """
        url = self.params.url + "v1/users"
        paginator = Paginator(self.params.session, url, params={**conditions})
        results = paginator.fetch_results()
        return [
            User(
                self.params,
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
        """
        url = self.params.url + "v1/users"
        paginator = Paginator(self.params.session, url, params={**conditions})
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        users = (
            User(
                self.params,
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
        """
        url = self.params.url + f"v1/users/{uid}"
        response = self.params.session.get(url)
        return User(
            self.params,
            **response.json(),
        )

    def count(self) -> int:
        """
        Return the total number of users.

        Returns
        -------
        int
        """
        url = self.params.url + "v1/users"
        response = self.params.session.get(url, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
