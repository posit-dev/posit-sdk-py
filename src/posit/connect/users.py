from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Callable, List, Optional

from requests import Session

from . import urls

from .config import Config
from .paginator import _MAX_PAGE_SIZE, Paginator


@dataclass
class User:
    guid: str
    email: str
    username: str
    first_name: str
    last_name: str
    user_role: str
    created_time: datetime
    updated_time: datetime
    active_time: datetime
    confirmed: bool
    is_locked: bool

    asdf: Optional[bool]


    @property
    def locked(self):
        from warnings import warn

        warn("this is a deprecation notice", DeprecationWarning)
        return self.is_locked

    @locked.setter
    def locked(self, value):
        self.locked = value

    @classmethod
    def from_dict(cls, instance: dict) -> User:
        field_names = {"locked": "is_locked"}
        instance = {field_names.get(k, k): v for k, v in instance.items()}
        return cls(**instance)

    def asdict(self) -> dict:
        field_names = {"is_locked": "locked"}
        return {
            **asdict(self),
            **{field_names.get(k, k): v for k, v in asdict(self).items()},
        }


class Users:
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> List[User]:
        results = Paginator(self.session, self.url, page_size=page_size).get_all()
        users = (User.from_dict(result) for result in results)
        return [user for user in users if filter(user)]

    def find_one(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> User | None:
        pager = Paginator(self.session, self.url, page_size=page_size)
        while pager.total is None or pager.seen < pager.total:
            result = pager.get_next_page()
            for u in result:
                user = User.from_dict(u)
                if filter(user):
                    return user
        return None

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return User.from_dict(response.json())
