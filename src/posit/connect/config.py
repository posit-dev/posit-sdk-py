"""Client configuration."""

import os

from typing_extensions import Optional

from . import urls


def _get_api_key() -> str:
    """Return the system configured api key.

    Reads the environment variable 'CONNECT_API_KEY'.

    Raises
    ------
        ValueError: If CONNECT_API_KEY is not set or invalid

    Returns
    -------
        str
    """
    value = os.environ.get("CONNECT_API_KEY")
    if not value:
        raise ValueError("Invalid value for 'CONNECT_API_KEY': Must be a non-empty string.")
    return value


def _get_url() -> str:
    """Return the system configured url.

    Reads the environment variable 'CONNECT_SERVER'.

    Raises
    ------
        ValueError: If CONNECT_SERVER is not set or invalid

    Returns
    -------
        str
    """
    value = os.environ.get("CONNECT_SERVER")
    if not value:
        raise ValueError("Invalid value for 'CONNECT_SERVER': Must be a non-empty string.")
    return value


class Config:
    """Configuration object."""

    def __init__(self, api_key: Optional[str] = None, url: Optional[str] = None) -> None:
        self.api_key = api_key or _get_api_key()
        self.url = urls.Url(url or _get_url())
