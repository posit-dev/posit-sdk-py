"""Provides authentication functionality back to Posit Workbench."""

from requests import PreparedRequest
from requests.auth import AuthBase

from .cookie_reader import CookieReader


class Auth(AuthBase):
    """Authentication handler for Posit Workbench RPC requests."""

    def __init__(self, cookie_reader: CookieReader) -> None:
        self._cookie_reader = cookie_reader

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Add RPC cookie to the request headers."""
        cookie = self._cookie_reader.get_cookie()
        if cookie:
            r.headers["X-RS-Session-Server-RPC-Cookie"] = cookie
        return r
