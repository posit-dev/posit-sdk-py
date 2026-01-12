"""Client connection for Posit Workbench."""

import os

from requests import Response, Session
from typing_extensions import Optional, Union

from .auth import Auth, CookieReader
from .context import Context, ContextManager
from .oauth import OAuth
from .urls import Url


class Client(ContextManager):
    """Client for interacting with Posit Workbench APIs.

    Parameters
    ----------
    verify : bool, str, or None, optional
        Controls SSL certificate verification:
        - True (default): Verify SSL certificates using the default certificate bundle
        - False: Disable SSL certificate verification (not recommended for production)
        - str: Path to a CA bundle file or directory of certificates
        - None: Use environment variables (REQUESTS_CA_BUNDLE, CURL_CA_BUNDLE) or system defaults

    Environment Variables
    ---------------------
    REQUESTS_CA_BUNDLE : str, optional
        Path to CA bundle file for SSL verification (used if verify=None)
    CURL_CA_BUNDLE : str, optional
        Alternative CA bundle path (used if REQUESTS_CA_BUNDLE not set and verify=None)
    """

    def __init__(self, verify: Optional[Union[bool, str]] = None) -> None:
        # Fall back to RS_SERVER_ADDRESS for backward compatibility
        # TODO: Remove RS_SERVER_ADDRESS fallback when Workbench 2025.09 falls out of support
        posit_product = os.getenv("POSIT_PRODUCT")
        server_url = os.getenv("RS_SERVER_ADDRESS")

        if posit_product != "WORKBENCH" and not server_url:
            raise EnvironmentError(
                "POSIT_PRODUCT environment variable not set. Workbench client can only be used within Posit Workbench sessions.",
            )
        self.session = Session()
        self.session.auth = Auth(CookieReader())

        # Configure SSL certificate verification
        if verify is not None:
            self.session.verify = verify

        if not server_url:
            raise EnvironmentError(
                "RS_SERVER_ADDRESS environment variable not set. Cannot determine Posit Workbench server address. Contact your server administrator to ensure that launcher-sessions-callback-address is configured correctly.",
            )
        self.server_url = Url(server_url)
        self._ctx = Context(self)

    def get(self, path: str, **kwargs) -> Response:
        """Send a GET request."""
        url = self.server_url.append(path)
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        """Send a POST request."""
        url = self.server_url.append(path)
        return self.session.post(url, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        """Send a PUT request."""
        url = self.server_url.append(path)
        return self.session.put(url, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        """Send a PATCH request."""
        url = self.server_url.append(path)
        return self.session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        """Send a DELETE request."""
        url = self.server_url.append(path)
        return self.session.delete(url, **kwargs)

    @property
    def oauth(self) -> OAuth:
        """Access the OAuth resource manager.

        Returns
        -------
            OAuth
        """
        return OAuth(self._ctx)
