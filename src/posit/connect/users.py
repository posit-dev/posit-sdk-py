from __future__ import annotations
from typing import List, overload


import requests


from . import me, urls

from .config import Config
from .paginator import Paginator
from .resources import Resource, Resources


class User(Resource):
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

        Returns:
            None
        """
        _me = me.get(self.config, self.session)
        if _me.guid == self.guid and not force:
            raise RuntimeError(
                "You cannot lock your own account. Set force=True to override this behavior."
            )
        url = urls.append_path(self.config.url, f"v1/users/{self.guid}/lock")
        body = {"locked": True}
        self.session.post(url, json=body)
        super().update(locked=True)

    def unlock(self):
        """
        Unlocks the user account.

        Returns:
            None
        """
        url = urls.append_path(self.config.url, f"v1/users/{self.guid}/lock")
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

        Returns:
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

        Returns:
            None
        """
        ...

    def update(self, *args, **kwargs) -> None:
        """
        Update the user.

        Args:
            *args
            **kwargs

        Returns:
            None
        """
        body = dict(*args, **kwargs)
        url = urls.append_path(self.config.url, f"v1/users/{self.guid}")
        response = self.session.put(url, json=body)
        super().update(**response.json())


class Users(Resources[User]):
    def __init__(self, config: Config, session: requests.Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.config = config
        self.session = session

    def find(self) -> List[User]:
        paginator = Paginator(self.session, self.url)
        results = paginator.fetch_results()
        return [
            User(
                config=self.config,
                session=self.session,
                **user,
            )
            for user in results
        ]

    def find_one(self) -> User | None:
        paginator = Paginator(self.session, self.url)
        pages = paginator.fetch_pages()
        results = (result for page in pages for result in page.results)
        users = (
            User(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in results
        )
        return next(users, None)

    def get(self, id: str) -> User:
        url = urls.append_path(self.config.url, f"v1/users/{id}")
        response = self.session.get(url)
        return User(
            config=self.config,
            session=self.session,
            **response.json(),
        )

    def create(self) -> User:
        raise NotImplementedError()

    def update(self) -> User:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def count(self) -> int:
        response: requests.Response = self.session.get(
            self.url, params={"page_size": 1}
        )
        result: dict = response.json()
        return result["total"]
