"""Provides authentication functionality."""

import requests

from . import config


class Auth(requests.auth.AuthBase):
    """Handles authentication for API requests."""

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Add authorization header to the request."""
        c = config.Config()
        r.headers["Authorization"] = f"Key {c.api_key}"
        return r
