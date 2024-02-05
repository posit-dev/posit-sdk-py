from __future__ import annotations

import os

from dataclasses import dataclass, asdict
from datetime import datetime
from requests import Session
from typing import Optional


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
    locked: bool

    def to_dict(self) -> dict:
        return asdict(self)


class Users(list[User]):
    """An extension of :class:`list[User]` with additional fetch methods."""

    _endpoint: str
    _session: Session

    def __init__(self, endpoint: str, session: Session):
        self._endpoint = endpoint
        self._session = session

    def find(self, params: dict = {}) -> Users:
        """Finds any :class:`User` that matches the provided filter conditions

        Keyword Arguments:
            params -- filter conditions (default: {{}})

        Returns:
            `self`
        """
        self.clear()
        endpoint = os.path.join(self._endpoint, "__api__/v1/users")
        response = self._session.get(endpoint)
        data = response.json()
        for user in data["results"]:
            if all(user.get(k) == v for k, v in params.items()):
                self.append(User(**user))
        # todo - implement paging and caching
        return self

    def find_one(self, params: dict = {}) -> Optional[User]:
        """Finds one :class:`User`

        Keyword Arguments:
            params -- filter conditions (default: {{}})

        Returns:
            A matching :class:`User`.
        """
        if "guid" in params:
            # Use the user details API if a 'guid' is provided.
            # This is an example of how we can use different API endpoints to optimize execution time.
            endpoint = os.path.join(self._endpoint, "__api__/v1/users", params["guid"])
            response = self._session.get(endpoint)
            return User(**response.json())

        # Otherwise, perform a normal search.
        return next(iter(self.find(params)), None)
