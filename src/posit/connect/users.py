from __future__ import annotations

import os

from datetime import datetime
from requests import Session
from typing import Iterator, List, Optional, TypedDict

from .config import Config
from .endpoints import get_users
from .errors import ClientError

_MAX_PAGE_SIZE = 500


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


class Users(Iterator[User]):
    def __init__(
        self, config: Config, session: Session, *, users: Optional[List[User]] = None
    ):
        self._config = config
        self._session = session

        self._cached_users: List[User] = users or []
        self._exhausted: bool = users is not None
        self._index: int = 0
        self._page_number: int = 0

    def __iter__(self) -> Iterator[User]:
        """
        Initialize the iterator by resetting the index to the beginning of the cached user list.

        Returns:
            Iterator: The initialized iterator object.
        """
        # Reset the index to the beginning of the cached user list.
        self._index = 0
        # Return the iterator object.
        return self

    def __next__(self):
        """Retrieve the next user in the list. If necessary, fetch a new page of users beforehand.

        Raises:
            StopIteration: If the end of the user list is reached.
            StopIteration: If no users are returned for the current page.

        Returns:
            dict: Information about the next user.
        """
        # Check if the current index is greater than or equal to the length of the cached user list.
        if self._index >= len(self._cached_users):
            # Check if the endpoint was exhausted on the previous iteration
            if self._exhausted:
                # Stop iteration if the index is not aligned with page boundaries.
                raise StopIteration
            # Fetch the current page of users.
            results, exhausted = get_users(
                self._config.endpoint, self._session, self._page_number
            )
            # Mark if the endpoint is exhausted for the next iteration
            self._exhausted = exhausted
            # Increment the page counter for the next iteration.
            self._page_number += 1
            # Append the fetched users to the cached user list.
            self._cached_users += [User(**result) for result in results]
            # Check if the fetched results list is empty.
            if not results:
                # Stop iteration if no users are returned for the current page.
                raise StopIteration
        # Get the current user by index.
        user = self._cached_users[self._index]
        # Increment the index for the next iteration.
        self._index += 1
        # Return the current user.
        return user

    def find(self, params: User) -> Users:
        """
        Finds users that match the provided filter conditions.

        Args:
            params (User): Filter conditions.

        Returns:
            Users: A list of users matching the filter conditions.
        """
        found: List[User] = []
        for user in self:
            # Check if the items in params are subset of user's items.
            if params.items() <= user.items():
                # Append the user to the found list.
                found.append(user)
        return Users(self._config, self._session, users=found)

    def find_one(self, params: User) -> Optional[User]:
        """
        Finds one User matching the provided parameters.

        Keyword Arguments:
            params -- Dictionary of filter conditions (default: {}).

        Returns:
            A matching User if found, otherwise None.

        Note:
            This method first checks if 'guid' is present in params. If so, it attempts a direct lookup using self.get().
            If an error with code '4' is encountered (indicating no matching user), it logs a warning and returns None.
            If 'guid' is not provided, it performs a normal search using self.find() and return the first value found.
        """
        # Check if 'guid' is provided in params
        if "guid" in params:
            try:
                # Attempt direct lookup
                self.get(params["guid"])
            except ClientError as e:
                # Check for error code '4' (no matching user)
                if e.error_code == 4:
                    import logging

                    logging.warning(e)
                    # Return None if user not found
                    return None
                raise e

        # If 'guid' not provided perform a normal search
        return next(iter(self.find(params)), None)

    def get(self, guid: str) -> User:
        """Gets a user by guid.

        Arguments:
            guid -- the users guid.

        Returns:
            A :class:`User`.
        """
        endpoint = os.path.join(self._config.endpoint, "v1/users", guid)
        response = self._session.get(endpoint)
        return User(**response.json())

    def to_pandas_data_frame(self):  # noqa
        import pandas as pd

        return pd.DataFrame((user for user in self))
