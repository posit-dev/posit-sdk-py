import os

from requests import Session
from typing import Optional

from . import hooks

from .auth import Auth
from .users import Users


def _get_api_key() -> str:
    """Gets the API key from the environment variable 'CONNECT_API_KEY'.

    Raises:
        ValueError: if CONNECT_API_KEY is not set or invalid

    Returns:
        The API key
    """
    value = os.environ.get("CONNECT_API_KEY")
    if value is None or value == "":
        raise ValueError(
            "Invalid value for 'CONNECT_API_KEY': Must be a non-empty string."
        )
    return value


def _get_endpoint() -> str:
    """Gets the endpoint from the environment variable 'CONNECT_SERVER'.

    The `requests` library uses 'endpoint' instead of 'server'. We will use 'endpoint' from here forward for consistency.

    Raises:
        ValueError: if CONNECT_SERVER is not set or invalid.

    Returns:
        The endpoint.
    """
    value = os.environ.get("CONNECT_SERVER")
    if value is None or value == "":
        raise ValueError(
            "Invalid value for 'CONNECT_SERVER': Must be a non-empty string."
        )
    return value


class Client:
    users: Users

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or _get_api_key()
        self._endpoint = endpoint if endpoint else _get_endpoint()
        self._session = Session()
        self._session.hooks["response"].append(hooks.handle_errors)
        self._session.auth = Auth(self._api_key)
        self.users = Users(self._endpoint, self._session)
