from __future__ import annotations
from typing import Any, Callable, List, Optional

from requests import Session


from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator
from .resources import Resources


class User(dict):

    @property
    def guid(self) -> str:
        return self.get("guid")

    @property
    def email(self) -> str:
        return self.get("email")

    @property
    def username(self) -> str:
        return self.get("username")

    @property
    def first_name(self) -> str:
        return self.get("first_name")

    @property
    def last_name(self) -> str:
        return self.get("last_name")

    @property
    def user_role(self) -> str:
        return self.get("user_role")

    @property
    def created_time(self) -> str:
        return self.get("created_time")

    @property
    def updated_time(self) -> str:
        return self.get("updated_time")

    @property
    def active_time(self) -> str:
        return self.get("active_time")

    @property
    def confirmed(self) -> bool:
        return self.get("confirmed")

    @property
    def locked(self) -> bool:
        return self.get("locked")

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Cannot set attributes: use update() instead.")

    def _update(self, body):
        self.get("session").patch(self.get("url"), json=body)
        # If the request is successful, update the local object
        # TODO: that patch request returns a payload on success,
        # so we could update the local object with that payload
        # (includes updated_time)
        super().update(body)

    def update(
        self,
        # Not all properties are settable, so we enumerate them here
        # (also for type-hinting purposes)
        email: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        user_role: Optional[str] = None,
        # TODO: in the API, this goes via POST /v1/users/{guid}/lock
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
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> List[User]:
        results = Paginator(self.session, self.url, page_size=page_size).get_all()
        return [
            User(
                **user,
                session=self.session,
                url=urls.append_path(self.url, user["guid"]),
            )
            for user in results
            if filter(User(**user))
        ]

    def find_one(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> User | None:
        pager = Paginator(self.session, self.url, page_size=page_size)
        while pager.total is None or pager.seen < pager.total:
            result = pager.get_next_page()
            for u in result:
                user = User(
                    **u,
                    session=self.session,
                    url=urls.append_path(self.url, u["guid"]),
                )
                if filter(user):
                    return user
        return None

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        raw_user = response.json()
        return User(
            **raw_user,
            session=self.session,
            url=urls.append_path(self.url, raw_user["guid"]),
        )

    def create(self) -> User:
        raise NotImplementedError()

    def update(self) -> User:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()
