from __future__ import annotations

import requests

from datetime import datetime
from typing import Callable, Optional, TypedDict

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


_MAX_PAGE_SIZE = 500


class Users(Paginator):
    """A class for users.

    This class is also a paginator, so it can be iterated over to fetch all users iteratively.

    example:
    ```python

    from posit.connect import Users

    users = Users(config, session)
    for user in users:
        print(user)
    ```

    Attributes:
        config (Config): A configuration instance.
        session (requests.Session): A session instance.

    Methods:
        find: Returns all users that match a filter.
        find_one: Returns the first user that matches a filter.
        get: Returns a user by ID.
    """

    def __init__(self, config: Config, session: requests.Session) -> None:
        super().__init__(
            session, urls.append_path(config.url, "v1/users"), page_size=_MAX_PAGE_SIZE
        )
        self.config = config
        self.session = session

    # todo - replace with query parameter based filtering.
    # reason - the current implementation is a fill in for actual implementation
    def find(
        self,
        filter: Callable[[User], bool] = lambda user: True,
        *,
        page_size: int = _MAX_PAGE_SIZE,
    ) -> list[User]:
        url = urls.append_path(self.config.url, "v1/users")
        paginator = Paginator(self.session, url, page_size=page_size)
        users = (User(**user) for user in paginator)
        return [user for user in users if filter(user)]

    # todo - replace with query parameter based filtering.
    # reason - the current implementation is a fill in for actual implementation
    def find_one(
        self,
        filter: Callable[[User], bool] = lambda user: True,
        *,
        page_size: int = _MAX_PAGE_SIZE,
    ) -> Optional[User]:
        # You may be tempted to to use self.find(filter, page_size) and return the first element.
        # This is less efficient as it will fetch all the users and then filter them.
        # Instead, we use the paginator directly to fetch the first user that matches the filter.
        # Since the paginator fetches the users in pages, it will stop fetching subsequent pages once a match is found.
        url = urls.append_path(self.config.url, "v1/users")
        paginator = Paginator(self.session, url, page_size=page_size)
        users = (User(**user) for user in paginator)
        users = (user for user in users if filter(user))
        return next(users, None)

    def get(self, id: str) -> User:
        url = urls.append_path(self.config.url, "v1/users", id)
        response = self.session.get(url)
        return User(**response.json())
