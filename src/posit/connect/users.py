from __future__ import annotations

from datetime import datetime
from typing import Callable, List, TypedDict

from requests import Session

from . import urls

from .config import Config
from .paginator import Paginator


class User(TypedDict, total=False):
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
    locked: bool


class Users:
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/users")
        self.paginator = Paginator(session, self.url, page_size=config.page_size)
        self.config = config
        self.session = session

    def find(self, filter: Callable[[User], bool] = lambda _: True) -> List[User]:
        return [User(**user) for user in self.paginator if filter(User(**user))]

    def find_one(self, filter: Callable[[User], bool] = lambda _: True) -> User | None:
        return next(
            (User(**user) for user in self.paginator if filter(User(**user))), None
        )

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return User(**response.json())

    def __iter__(self):
        return iter(self.paginator)

    def __len__(self):
        return len(self.paginator)
