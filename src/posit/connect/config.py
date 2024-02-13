import os

from typing import Optional


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


def _format_endpoint(endpoint: str) -> str:
    # todo - format endpoint url and ake sure it ends with __api__
    return endpoint


class Config:
    """Derived configuration properties"""

    api_key: str
    endpoint: str

    def __init__(
        self, api_key: Optional[str] = None, endpoint: Optional[str] = None
    ) -> None:
        self.api_key = api_key or _get_api_key()
        self.endpoint = _format_endpoint(endpoint or _get_endpoint())
