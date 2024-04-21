"""Provides authentication functionality."""

from requests import PreparedRequest
from requests.auth import AuthBase

from .config import Config


class Auth(AuthBase):
    """Handles authentication for API requests."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Add authorization header to the request."""
        r.headers["Authorization"] = f"Key {self.api_key}"
        return r
