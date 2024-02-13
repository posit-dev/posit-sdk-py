from __future__ import annotations

from contextlib import contextmanager
from requests import Session
from typing import Generator, Optional

from . import hooks

from .auth import Auth
from .config import Config
<<<<<<< HEAD
from .users import LazyUsers, Users
=======
from .users import Users
>>>>>>> b5d8a18 (feat: adds users implementation with lazy server-side fetching)


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

        # Initialize the Users instance.
        self.users: Users = LazyUsers(config=config, session=session)
        # Store the Session object.
        self._session = session

    def __del__(self):
        """
        Close the session when the Client instance is deleted.
        """
        self._session.close()
