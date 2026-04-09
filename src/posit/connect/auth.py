"""Provides authentication functionality."""

from requests import PreparedRequest
from requests.auth import AuthBase

from .config import Config


class Auth(AuthBase):
    """Handles authentication for API requests."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Add authorization header to the request."""
        r.headers["Authorization"] = f"Key {self._config.api_key}"
        return r


class BootstrapAuth(AuthBase):
    """Handles bootstrap authentication for initial server setup.

    Used with the ``v1/experimental/bootstrap`` endpoint to perform first-time
    server configuration. After bootstrapping, use the returned API key with
    the standard :class:`Auth` class.

    Parameters
    ----------
    token : str
        The bootstrap JWT token.
    """

    def __init__(self, token: str) -> None:
        self._token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Add bootstrap authorization header to the request."""
        r.headers["Authorization"] = f"Connect-Bootstrap {self._token}"
        return r

    def __repr__(self) -> str:
        """Return a representation that does not expose the bootstrap token."""
        return "BootstrapAuth(token=***)"

    def __str__(self) -> str:
        """Return a string that does not expose the bootstrap token."""
        return self.__repr__()
