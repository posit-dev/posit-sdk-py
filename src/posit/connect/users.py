"""User resources."""

from __future__ import annotations

from typing import List, overload

from . import me
from .content import Content
from .paginator import Paginator
from .resources import Resource, ResourceParameters, Resources


class User(Resource):
    @property
    def content(self) -> Content:
        return Content(self.params, owner_guid=self.guid)

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
        url = self.params.url + f"v1/users/{self.guid}/lock"
        body = {"locked": True}
        self.params.session.post(url, json=body)
        super().update(locked=True)

    def unlock(self):
        """
        Unlocks the user account.

        Returns
        -------
            None
        """
        url = self.params.url + f"v1/users/{self.guid}/lock"
        body = {"locked": False}
        self.params.session.post(url, json=body)
        super().update(locked=False)

    @overload
    def update(
        self,
        *args,
        email: str = ...,
        username: str = ...,
        first_name: str = ...,
        last_name: str = ...,
        user_role: str = ...,
        **kwargs,
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
        url = self.params.url + f"v1/users/{self.guid}"
        response = self.params.session.put(url, json=body)
        super().update(**response.json())


class Users(Resources):
    """Users resource."""

    def __init__(self, params: ResourceParameters) -> None:
        super().__init__(params)

    @overload
    def find(
        self,
        *,
        prefix: str = ...,
        user_role: str = ...,
        account_status: str = ...,
    ) -> List[User]: ...

    @overload
    def find(self, **kwargs) -> List[User]: ...

    def find(self, **kwargs) -> List[User]:
        url = self.params.url + "v1/users"
        paginator = Paginator(self.params.session, url, params=kwargs)
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
        *,
        prefix: str = ...,
        user_role: str = ...,
        account_status: str = ...,
    ) -> User | None: ...

    @overload
    def find_one(self, **kwargs) -> User | None: ...

    def find_one(self, **kwargs) -> User | None:
        url = self.params.url + "v1/users"
        paginator = Paginator(self.params.session, url, params=kwargs)
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
        url = self.params.url + f"v1/users/{uid}"
        response = self.params.session.get(url)
        return User(
            self.params,
            **response.json(),
        )

    def count(self) -> int:
        url = self.params.url + "v1/users"
        response = self.params.session.get(url, params={"page_size": 1})
        result: dict = response.json()
        return result["total"]
