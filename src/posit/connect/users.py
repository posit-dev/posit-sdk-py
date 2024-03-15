from __future__ import annotations
from typing import Any, Callable, List

from requests import Session


from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator
from .resources import Resources


class User(dict):

    @property
    def guid(self) -> str:
        return self["guid"]

    @property
    def email(self) -> str:
        return self["email"]

    @property
    def username(self) -> str:
        return self["username"]

    @property
    def first_name(self) -> str:
        return self["first_name"]

    @property
    def last_name(self) -> str:
        return self["last_name"]

    @property
    def user_role(self) -> str:
        return self["user_role"]

    @property
    def created_time(self) -> str:
        return self["created_time"]

    @property
    def updated_time(self) -> str:
        return self["updated_time"]

    @property
    def active_time(self) -> str:
        return self["active_time"]

    @property
    def confirmed(self) -> bool:
        return self["confirmed"]

    @property
    def locked(self) -> bool:
        return self["locked"]

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Cannot set attributes: use update() instead.")

    def update(self, **kwargs):
        self["session"].patch(self["url"], json=kwargs)
        super().update(kwargs)


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
