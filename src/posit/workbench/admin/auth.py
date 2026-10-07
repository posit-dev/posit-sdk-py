"""Authentication for the Bearer-token Workbench launcher API client."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from requests.auth import AuthBase

if TYPE_CHECKING:
    from requests import PreparedRequest

    from .config import Config


class Auth(AuthBase):
    """Attaches a Workbench API bearer token to outgoing requests."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Add the Authorization header to the request."""
        r.headers["Authorization"] = f"Bearer {self._config.api_key}"
        return r
