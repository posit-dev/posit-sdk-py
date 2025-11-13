"""Client connection for Posit Workbench."""
import os

from .auth import Auth, CookieReader
from .oauth import OAuth
from .context import Context, ContextManager, requires

from requests import Session, Response

class Client(ContextManager):

    def __init__(self) -> None:
        if not os.getenv("POSIT_PRODUCT") == "WORKBENCH":
            raise EnvironmentError(
                "POSIT_PRODUCT environment variable not set. Workbench client can only be used within Posit Workbench sessions.",
            )
        self.session = Session()
        self.session.auth = Auth(CookieReader())
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
