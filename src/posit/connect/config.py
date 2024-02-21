import os

from typing import Optional

from . import urls


def _get_api_key() -> str:
    """Gets the API key from the environment variable 'CONNECT_API_KEY'.

    Raises:
        ValueError: if CONNECT_API_KEY is not set or invalid

    Returns:
        The API key
    """
    value = os.environ.get("CONNECT_API_KEY")
    if not value:
        raise ValueError(
            "Invalid value for 'CONNECT_API_KEY': Must be a non-empty string."
        )
    return value


def _get_url() -> str:
    """Gets the endpoint from the environment variable 'CONNECT_SERVER'.

    The `requests` library uses 'endpoint' instead of 'server'. We will use 'endpoint' from here forward for consistency.

    Raises:
        ValueError: if CONNECT_SERVER is not set or invalid.

    Returns:
        The endpoint.
    """
    value = os.environ.get("CONNECT_SERVER")
    if not value:
        raise ValueError(
            "Invalid value for 'CONNECT_SERVER': Must be a non-empty string."
        )
    return value


class Config:
    """Derived configuration properties"""

    def __init__(
        self, api_key: Optional[str] = None, url: Optional[str] = None
    ) -> None:
        self.api_key = api_key or _get_api_key()
        self.url = urls.server_to_api_url(url or _get_url())
        urls.validate(self.url)
