"""User resources."""

from __future__ import annotations

from typing import List, overload

from . import me
from .content import Content
from .paginator import Paginator
from .resources import Resource, ResourceParameters, Resources


class User(Resource):
    """User resource.

    Attributes
    ----------
    content: Content
        A content resource scoped to this user.
    guid : str
    email : str
    username : str
    first_name : str
    last_name : str
    user_role : str
    created_time : str
    updated_time : str
    active_time : str
    confirmed : bool
        Whether the user has confirmed their email address.
    locked : bool
        Whether the user is locked.
    """

    @property
    def content(self) -> Content:
        return Content(self.params, owner_guid=self.guid)

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def email(self) -> str:
        return self.get("email")  # type: ignore

    @property
    def username(self) -> str:
        return self.get("username")  # type: ignore

    @property
    def first_name(self) -> str:
        return self.get("first_name")  # type: ignore

    @property
    def last_name(self) -> str:
        return self.get("last_name")  # type: ignore

    @property
    def user_role(self) -> str:
        return self.get("user_role")  # type: ignore

    @property
    def created_time(self) -> str:
        return self.get("created_time")  # type: ignore

    @property
    def updated_time(self) -> str:
        return self.get("updated_time")  # type: ignore

    @property
    def active_time(self) -> str:
        return self.get("active_time")  # type: ignore

    @property
    def confirmed(self) -> bool:
        return self.get("confirmed")  # type: ignore

    @property
    def locked(self) -> bool:
        return self.get("locked")  # type: ignore

    def lock(self, *, force: bool = False):
        """
        Locks the user account.

        .. warning:: You cannot unlock your own account. Once an account is locked, only an admin can unlock it.

        Args:
            force (bool, optional): If set to True, overrides lock protection allowing a user to lock their own account. Defaults to False.

        Returns
        -------
            None
        """
        _me = me.get(self.params)
        if _me.guid == self.guid and not force:
            raise RuntimeError(
                "You cannot lock your own account. Set force=True to override this behavior."
            )
        url = self.url + f"v1/users/{self.guid}/lock"
        body = {"locked": True}
        self.session.post(url, json=body)
        super().update(locked=True)

    def unlock(self):
        """
        Unlocks the user account.

        Returns
        -------
            None
        """
        url = self.url + f"v1/users/{self.guid}/lock"
        body = {"locked": False}
        self.session.post(url, json=body)
        super().update(locked=False)

    @overload
    def update(
        self,
        email: str = ...,
        username: str = ...,
        first_name: str = ...,
        last_name: str = ...,
        user_role: str = ...,
    ) -> None:
        """
        Update the user.

        Args:
            email (str): The email address for the user.
            username (str): The username for the user.
            first_name (str): The first name for the user.
            last_name (str): The last name for the user.
            user_role (str): The role for the user.

        Returns
        -------
            None
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """
        Update the user.

        Args:
            *args
            **kwargs

        Returns
        -------
            None
        """
        ...

    def update(self, *args, **kwargs) -> None:
        """
        Update the user.

        Args:
            *args
            **kwargs

        Returns
        -------
            None
        """
        body = dict(*args, **kwargs)
        url = self.url + f"v1/users/{self.guid}"
        response = self.session.put(url, json=body)
        super().update(**response.json())


class Users(Resources):
    """Users resource."""

    def __init__(self, params: ResourceParameters) -> None:
        super().__init__(params)

    @overload
    def find(
        self,
        prefix: str = ...,
        user_role: str = ...,
        account_status: str = ...,
    ) -> List[User]: ...

    @overload
    def find(self, *args, **kwargs) -> List[User]: ...

    def find(self, *args, **kwargs):
        url = self.params.url + "v1/users"
        params = dict(*args, **kwargs)
        paginator = Paginator(self.session, url, params=params)
        results = paginator.fetch_results()
        return [
            User(
                self.params,
                **user,
            )
            for user in results
        ]

    @overload
    def find_one(
        self,
        prefix: str = ...,
        user_role: str = ...,
        account_status: str = ...,
    ) -> User | None: ...

    @overload
    def find_one(self, *args, **kwargs) -> User | None: ...

    def find_one(self, *args, **kwargs) -> User | None:
        url = self.params.url + "v1/users"
        params = dict(*args, **kwargs)
        paginator = Paginator(self.session, url, params=params)
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

    def get(self, id: str) -> User:
        url = self.url + f"v1/users/{id}"
        response = self.session.get(url)
        return User(
            self.params,
            **response.json(),
        )

    def count(self) -> int:
        url = self.params.url + "v1/users"
        response = self.session.get(url, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
