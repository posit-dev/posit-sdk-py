from __future__ import annotations

from contextlib import contextmanager
import os
from requests import Session
from typing import Generator, Optional

from . import hooks

from .auth import Auth
from .config import Config
from .users import User, Users, CachedUsers


@contextmanager
def create_client(
    api_key: Optional[str] = None, endpoint: Optional[str] = None
) -> Generator[Client, None, None]:
    """Creates a new :class:`Client` instance

    Keyword Arguments:
        api_key -- an api_key for authentication (default: {None})
        endpoint -- a base api endpoint (url) (default: {None})

    Returns:
        A :class:`Client` instance
    """
    client = Client(api_key=api_key, endpoint=endpoint)
    try:
        yield client
    finally:
        del client


class Client:
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """
        Initialize the Client instance.

        Args:
            api_key (str, optional): API key for authentication. Defaults to None.
            endpoint (str, optional): API endpoint URL. Defaults to None.
        """
        # Create a Config object.
        config = Config(api_key=api_key, endpoint=endpoint)
        # Create a Session object for making HTTP requests.
        session = Session()
        # Authenticate the session using the provided Config.
        session.auth = Auth(config=config)
        # Add error handling hooks to the session.
        session.hooks["response"].append(hooks.handle_errors)

        # Store the Config and Session objects.
        self._config = config
        self._session = session

        # Internal properties for storing public resources
        self._current_user: Optional[User] = None
        self._users: Optional[CachedUsers] = None


    @property
    def me(self) -> User:
        if self._current_user is None:
            endpoint = os.path.join(self._config.endpoint, "v1/user")
            response = self._session.get(endpoint)
            self._current_user = User(**response.json())
        return self._current_user


    @property
    def users(self) -> CachedUsers:
        if self._users is None:
            self._users = Users(client=self)
        return self._users


    def __del__(self):
        """
        Close the session when the Client instance is deleted.
        """
        self._session.close()
