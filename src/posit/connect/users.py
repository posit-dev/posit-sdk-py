from __future__ import annotations
from typing import List, Optional


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

    def _update(self, body):
        if len(body) == 0:
            return
        url = urls.append_path(self.config.url, f"v1/users/{self.guid}")
        response = self.session.put(url, json=body)
        super().update(**response.json())

    def update(  # type: ignore
        self,
        # Not all properties are settable, so we enumerate them here
        # (also for type-hinting purposes)
        email: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_role: Optional[str] = None,
        # TODO(#100): in the API, this goes via POST /v1/users/{guid}/lock
        # accept it here and make that request? Or add a .lock() method?
        # locked: Optional[bool] = None,
    ) -> None:
        kwargs = {}
        if email is not None:
            kwargs["email"] = email
        if username is not None:
            kwargs["username"] = username
        if first_name is not None:
            kwargs["first_name"] = first_name
        if last_name is not None:
            kwargs["last_name"] = last_name
        if user_role is not None:
            kwargs["user_role"] = user_role
        # if locked is not None:
        #     kwargs["locked"] = locked
        self._update(kwargs)


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
