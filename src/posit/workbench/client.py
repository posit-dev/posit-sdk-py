"""Client connection for Posit Workbench."""
import os
from typing import Optional, Union

from .auth import Auth, CookieReader
from .oauth import OAuth
from .context import Context, ContextManager, requires

from requests import Session, Response

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
    POSIT_PRODUCT : str
        Must be set to "WORKBENCH" to use this client
    RS_SERVER_ADDRESS : str
        The Workbench server address
    REQUESTS_CA_BUNDLE : str, optional
        Path to CA bundle file for SSL verification (used if verify=None)
    CURL_CA_BUNDLE : str, optional
        Alternative CA bundle path (used if REQUESTS_CA_BUNDLE not set and verify=None)

    Examples
    --------
    Basic usage (uses system certificates):
    >>> client = Client()

    Use a custom CA bundle:
    >>> client = Client(verify="/path/to/ca-bundle.crt")

    Disable SSL verification (not recommended):
    >>> client = Client(verify=False)
    """

    def __init__(self, verify: Optional[Union[bool, str]] = None) -> None:
        if not os.getenv("POSIT_PRODUCT") == "WORKBENCH":
            raise EnvironmentError(
                "POSIT_PRODUCT environment variable not set. Workbench client can only be used within Posit Workbench sessions.",
            )
        self.session = Session()
        self.session.auth = Auth(CookieReader())

        # Configure SSL certificate verification
        if verify is None:
            # Check environment variables for CA bundle
            ca_bundle = os.getenv("REQUESTS_CA_BUNDLE") or os.getenv("CURL_CA_BUNDLE")
            if ca_bundle:
                self.session.verify = ca_bundle
        else:
            self.session.verify = verify

        server_url = os.getenv("RS_SERVER_ADDRESS")
        if not server_url:
            raise EnvironmentError(
                "RS_SERVER_ADDRESS environment variable not set. Cannot determine Posit Workbench server address. Contact your server administrator to ensure that launcher-sessions-callback-address is configured correctly.",
            )
        self.server_url: str = server_url
        self._ctx = Context(self)

    def get(self, path: str, **kwargs) -> Response:
        url = self.server_url + path
        return self.session.get(url, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        url = self.server_url + path
        return self.session.post(url, **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        url = self.server_url + path
        return self.session.put(url, **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        url = self.server_url + path
        return self.session.patch(url, **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        url = self.server_url + path
        return self.session.delete(url, **kwargs)

    @property
    @requires(version="2025.11.0")
    def oauth(self) -> OAuth:
        """Access the OAuth resource manager.

        Returns
        -------
            OAuth
        """
        return OAuth(self._ctx)
