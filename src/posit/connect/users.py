"""User resources."""

from __future__ import annotations

from typing import List, Literal, overload

from typing_extensions import NotRequired, Required, TypedDict, Unpack

from . import me
from ._active import ActiveDict
from ._api_call import ApiCallMixin
from ._types_context import ContextP
from .content import Content
from .context import Context
from .paginator import Paginator


class UserContext(Context):
    user_guid: str

    def __init__(self, ctx: Context, /, *, user_guid: str) -> None:
        super().__init__(ctx.session, ctx.url)
        self.user_guid = user_guid


class User(ActiveDict[UserContext]):
    # @classmethod
    # def _api_path(cls) -> str:
    #     return "v1/users"

    # @classmethod
    # def _create(
    #     cls,
    #     ctx: Context,
    #     /,
    #     # **attrs: Unpack[ContentItemRepository._Attrs],
    #     **attrs,
    # ) -> User:
    #     from ._api_call import put_api

    #     # todo - use the 'context' module to inspect the 'authentication' object and route to POST (local) or PUT (remote).
    #     result = put_api(ctx, cls._api_path(), json=cast(JsonifiableDict, attrs))

    #     return User(
    #         ctx,
    #         **result,
    #     )

    class _Attrs(TypedDict, total=False):
        guid: str
        """The user's GUID, or unique identifier, in UUID [RFC4122](https://www.rfc-editor.org/rfc/rfc4122) format"""
        email: str
        """The user's email"""
        username: str
        """The user's username"""
        first_name: str
        """The user's first name"""
        last_name: str
        """The user's last name"""
        user_role: Literal["administrator", "publisher", "viewer"]
        """The user's role"""
        created_time: str
        """
        Timestamp (in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format) indicating when
        the user was created in the Posit Connect server.
        """
        updated_time: str
        """
        Timestamp (in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format) indicating when
        information about this user was last updated in the Posit Connect server.
        """
        active_time: str
        """
        Timestamp (in [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) format) indicating
        approximately when the user was last active. Highly active users only receive periodic updates.
        """
        confirmed: bool
        """
        When `false`, the created user must confirm their account through an email. This feature is unique to password authentication.
        """
        locked: bool
        """Whether or not the user is locked"""

    @overload
    def __init__(self, ctx: Context, /, *, guid: str) -> None: ...

    @overload
    def __init__(
        self,
        ctx: Context,
        /,
        # By default, the `attrs` will be retrieved from the API if no `attrs` are supplied.
        **attrs: Unpack[_Attrs],
    ) -> None: ...
    def __init__(
        self,
        ctx: Context,
        /,
        **attrs: Unpack[_Attrs],
    ) -> None:
        """User resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        guid : str
            The GUID of the user
        **attrs : ActiveDict
            Attributes for the user. If not supplied, the attributes will be
            retrieved from the API upon initialization
        """
        user_guid = attrs.get("guid")
        assert isinstance(user_guid, str), f"User `guid` must be a string. Got: {user_guid}"
        assert user_guid, "User `guid` must not be empty."

        user_ctx = UserContext(ctx, user_guid=user_guid)
        path = f"v1/users/{user_guid}"
        # Only fetch data if `guid` is the only attr
        get_data = len(attrs) == 1
        super().__init__(user_ctx, path, get_data, **attrs)

    @property
    def content(self) -> Content:
        return Content(self._ctx, owner_guid=self["guid"])

    def lock(self, *, force: bool = False) -> User:
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
        _me = me.get(self._ctx)
        if _me["guid"] == self["guid"] and not force:
            raise RuntimeError(
                "You cannot lock your own account. Set force=True to override this behavior.",
            )
        # Ignore result
        self._post_api("lock", json={"locked": True})

        # Return updated user
        attrs = dict(self)
        attrs["locked"] = True

        return User(self._ctx, **attrs)

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
        # Ignore result
        self._post_api("lock", json={"locked": False})

        # Return updated user
        attrs = dict(self)
        attrs["locked"] = False

        return User(self._ctx, **attrs)

    class _UpdateUser(TypedDict, total=False):
        """Update user request."""

        email: NotRequired[str]
        username: NotRequired[str]
        first_name: NotRequired[str]
        last_name: NotRequired[str]
        user_role: NotRequired[Literal["administrator", "publisher", "viewer"]]

    def update(
        self,
        **kwargs: Unpack[_UpdateUser],
    ) -> User:
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
        result = self._put_api(json=kwargs)
        assert result is not None, "User update failed."

        return User(self._ctx, **result)


class Users(ApiCallMixin, ContextP[Context]):
    """Users resource."""

    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = "v1/users"

    class _CreateUser(TypedDict):
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

    def create(self, **attributes: Unpack[_CreateUser]) -> User:
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
        result = self._post_api(json=attributes)
        assert result is not None, "User creation failed."
        return User(self._ctx, **result)

    class _FindUser(TypedDict):
        """Find user request."""

        prefix: NotRequired[str]
        user_role: NotRequired[Literal["administrator", "publisher", "viewer"] | str]
        account_status: NotRequired[Literal["locked", "licensed", "inactive"] | str]

    def find(self, **conditions: Unpack[_FindUser]) -> List[User]:
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
        url = self._ctx.url + "v1/users"
        paginator = Paginator(self._ctx.session, url, params={**conditions})
        results = paginator.fetch_results()
        return [
            User(
                self._ctx,
                **user,
            )
            for user in results
        ]

    def find_one(self, **conditions: Unpack[_FindUser]) -> User | None:
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
        url = self._ctx.url + self._path
        paginator = Paginator(self._ctx.session, url, params={**conditions})
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
        """
        result = self._get_api(uid)
        return User(
            self._ctx,
            **result,
        )

    def count(self) -> int:
        """
        Return the total number of users.

        Returns
        -------
        int
        """
        result: dict = self._get_api(params={"page_size": 1})
        return result["total"]
