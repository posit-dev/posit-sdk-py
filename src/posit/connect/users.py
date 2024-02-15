from __future__ import annotations

import os

from datetime import datetime
from typing import Iterator, Callable, List

from requests import Session

from .config import Config
from .resources import LazyResources, Resource, Resources

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


class Users(Resources[User]):
    def find(self, filter: Callable[[User], bool] = lambda _: True) -> Users:
        return Users([user for user in self if filter(user)])

    def find_one(self, filter: Callable[[User], bool] = lambda _: True) -> User | None:
        return next((user for user in self if filter(user)), None)

    def get(self, id: str) -> User:
        user = next((user for user in self if user["guid"] == id), None)
        if user is None:
            raise RuntimeError(f"failed to get user with id '{id}'")
        return user


class LazyUsers(Users, LazyResources[User]):
    def __init__(
        self, config: Config, session: Session, *, page_size=_MAX_PAGE_SIZE
    ) -> None:
        super().__init__()
        self.config = config
        self.session = session
        self.page_size = page_size

    def fetch(self, index) -> tuple[Iterator[User] | None, bool]:
        # Check if index is a multiple of page_size.
        if (index % self.page_size) != 0:
            #
            raise ValueError(
                f"index ({index}) must be a multiple of page size ({self.page_size})"
            )
        # Construct the endpoint URL.
        endpoint = os.path.join(self.config.endpoint, "v1/users")
        # Define the page number using 1-based indexing.
        page_number = int(index / self.page_size) + 1
        # Define query parameters for pagination.
        params = {"page_number": page_number, "page_size": self.page_size}
        # Send a GET request to the endpoint with the specified parameters.
        response = self.session.get(endpoint, params=params)
        # Convert response to dict
        json: dict = dict(response.json())
        # Parse the JSON response and extract the results.
        results: List[dict] = json["results"]
        # Mark exhausted if the result size is less than the maximum page size.
        exhausted = len(results) < self.page_size
        # Create User objects from the results and return them as a list.
        users: Iterator[User] = iter(User(**result) for result in results)
        return (users, exhausted)

    def get(self, id: str) -> User:
        endpoint = os.path.join(self.config.endpoint, "v1/users", id)
        response = self.session.get(endpoint)
        return User(**response.json())
