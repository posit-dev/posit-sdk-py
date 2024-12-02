from __future__ import annotations

import os
from typing import Optional

from typing_extensions import TypedDict

from ..resources import ResourceParameters, Resources
from .integrations import Integrations
from .sessions import Sessions

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"
USER_SESSION_TOKEN_TYPE = "urn:posit:connect:user-session-token"
CONTENT_SESSION_TOKEN_TYPE = "urn:posit:connect:content-session-token"

def _get_content_session_token() -> str:
    """Return the content session token.

    Reads the environment variable 'CONNECT_CONTENT_SESSION_TOKEN'.

    Raises
    ------
        ValueError: If CONNECT_CONTENT_SESSION_TOKEN is not set or invalid

    Returns
    -------
        str
    """
    value = os.environ.get("CONNECT_CONTENT_SESSION_TOKEN")
    if not value:
        raise ValueError("Invalid value for 'CONNECT_CONTENT_SESSION_TOKEN': Must be a non-empty string.")
    return value

class OAuth(Resources):
    def __init__(self, params: ResourceParameters, api_key: str) -> None:
        super().__init__(params)
        self.api_key = api_key

    def _get_credentials_url(self) -> str: 
        return self.params.url + "v1/oauth/integrations/credentials"

    @property
    def integrations(self):
        return Integrations(self.params)

    @property
    def sessions(self):
        return Sessions(self.params)

    def get_credentials(self, user_session_token: Optional[str] = None) -> Credentials:
        """Perform an oauth credential exchange with a user-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = USER_SESSION_TOKEN_TYPE
        if user_session_token:
            data["subject_token"] = user_session_token

        response = self.params.session.post(self._get_credentials_url(), data=data)
        return Credentials(**response.json())

    def get_content_credentials(self, content_session_token: Optional[str] = None) -> Credentials:
        """Perform an oauth credential exchange with a content-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = CONTENT_SESSION_TOKEN_TYPE
        data["subject_token"] = content_session_token or _get_content_session_token() 

        response = self.params.session.post(self._get_credentials_url(), data=data)
        return Credentials(**response.json())

class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
