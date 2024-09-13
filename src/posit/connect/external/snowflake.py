from typing import Optional

from ..client import Client
from .external import is_local

"""
NOTE: The APIs in this module are provided as a convenience and are subject to breaking changes.
"""


class PositAuthenticator:
    def __init__(
        self,
        local_authenticator: Optional[str] = None,
        client: Optional[Client] = None,
        user_session_token: Optional[str] = None,
    ):
        self._local_authenticator = local_authenticator
        self._client = client
        self._user_session_token = user_session_token

    @property
    def authenticator(self) -> Optional[str]:
        if is_local():
            return self._local_authenticator
        return "oauth"

    @property
    def token(self) -> Optional[str]:
        if is_local():
            return None

        # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
        # user_session_token is required to impersonate the viewer.
        if self._user_session_token is None:
            raise ValueError("The user-session-token is required for viewer authentication.")

        if self._client is None:
            self._client = Client()

        credentials = self._client.oauth.get_credentials(self._user_session_token)
        return credentials.get("access_token")
