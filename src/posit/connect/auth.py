"""Provides authentication functionality."""

import requests

from . import config


class Auth(requests.auth.AuthBase):
    """Handles authentication for API requests."""

    def __init__(self, config: config.Config) -> None:
        self.config = config

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Add authorization header to the request."""
        r.headers["Authorization"] = f"Key {self.config.api_key}"
        return r
