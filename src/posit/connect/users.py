from __future__ import annotations

from datetime import datetime
from typing import Callable, List, TypedDict

from requests import Session

from . import urls

from .config import Config
from .pagination import _MAX_PAGE_SIZE, PaginatedRequester


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
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> List[User]:
        results = PaginatedRequester(
            self.session, self.url, page_size=page_size
        ).get_all()
        return [User(**user) for user in results if filter(user)]

    def find_one(
        self, filter: Callable[[User], bool] = lambda _: True, page_size=_MAX_PAGE_SIZE
    ) -> User | None:
        pager = PaginatedRequester(self.session, self.url, page_size=page_size)
        result = pager.get_next_page()
        while pager.total is None or pager.seen < pager.total:
            for user in result:
                if filter(user):
                    return User(**user)
        return None

    def get(self, id: str) -> User:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return User(**response.json())
