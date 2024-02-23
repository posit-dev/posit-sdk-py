from __future__ import annotations

from datetime import datetime
from typing import Callable, List

from requests import Session

from . import urls

from .config import Config
from .resources import Resource

# The maximum page size supported by the API.
_MAX_PAGE_SIZE = 500


class User(Resource, total=False):
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


class PaginatedRequester:

    def __init__(self, session, url, start_page=1, page_size=_MAX_PAGE_SIZE):
        self.session = session
        self.url = url
        self.page_number = start_page
        self.page_size = page_size
        # The API response will tell us how many total entries there are,
        # but we don't know yet.
        self.total = None
        self.seen = 0

    def get_all(self) -> List[dict]:
        # Do the first page, which will tell us how many results there are
        result = self.get_next_page()
        while self.seen < self.total:
            self.page_number += 1
            result += self.get_next_page()
        return result

    def get_next_page(self) -> List[dict]:
        # Define query parameters for pagination.
        params = {"page_number": self.page_number, "page_size": self.page_size}
        # Send a GET request to the endpoint with the specified parameters.
        response = self.session.get(self.url, params=params).json()
        # On our first request, we won't have set the total yet, so do it
        if self.total is None:
            self.total = response["total"]
        results = response["results"]
        self.seen += len(results)
        return results
