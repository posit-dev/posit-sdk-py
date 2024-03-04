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
        """
        Find and return the first user that matches the given filter.

        Args:
            filter: A callable that takes a User object as input and returns a boolean value indicating whether the user matches the filter criteria. Defaults to a lambda function that always returns True.
            page_size: The number of users to fetch per page. Defaults to the maximum page size.

        Returns:
            The first User object that matches the filter, or None if no match is found.

        Note:
            This method uses the paginator to fetch users from the server in pages. It stops fetching subsequent pages once a match is found, making it more efficient than fetching all users and then filtering them.
            The filter function should take a User object as input and return True if the user matches the filter criteria, or False otherwise.
        """
        url = urls.append_path(self.config.url, "v1/users")
        paginator = Paginator(self.session, url, page_size=page_size)
        # Create a generator using comprehension syntax.
        users = (User(**user) for user in paginator if filter(User(**user)))
        # Evaluate the generator to find the first User matching the provided filter, or return None.
        # The generator is more memory efficient than a list since the paginator supports lazy-loading users on demand.
        # Once a match is found, the iteration is stopped, skipping any subsequent pages fetched by the paginator.
        # If the paginator is exhausted and no matching results are found, None is returned.
        # Runtime is reduced when a match occurs before all pages are fetched from the server.
        # If users was instead defined as `users = [User(**user) for user in paginator if filter(User(**user))]`, then all users are evaluated through the filter before next is called.
        # In other words, next(users, None) becomes a head operation on the in-memory list.
        return next(users, None)

    def get(self, id: str) -> User:
        url = urls.append_path(self.config.url, "v1/users", id)
        response = self.session.get(url)
        return User(**response.json())
