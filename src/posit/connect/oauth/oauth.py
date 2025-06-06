from __future__ import annotations

import os
from enum import Enum

from typing_extensions import TYPE_CHECKING, Optional, TypedDict

from ..resources import Resources
from .integrations import Integrations
from .sessions import Sessions

if TYPE_CHECKING:
    from ..context import Context

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"


class OAuthTokenType(str, Enum):
    ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
    AWS_CREDENTIALS = "urn:ietf:params:aws:token-type:credentials"
    API_KEY = "urn:posit:connect:api-key"
    CONTENT_SESSION_TOKEN = "urn:posit:connect:content-session-token"
    USER_SESSION_TOKEN = "urn:posit:connect:user-session-token"


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
        raise ValueError(
            "Invalid value for 'CONNECT_CONTENT_SESSION_TOKEN': Must be a non-empty string."
        )
    return value


class OAuth(Resources):
    def __init__(self, ctx: Context, api_key: str) -> None:
        super().__init__(ctx)
        self.api_key = api_key
        self._path = "v1/oauth/integrations/credentials"

    @property
    def integrations(self):
        return Integrations(self._ctx)

    @property
    def sessions(self):
        return Sessions(self._ctx)

    def get_credentials(
        self,
        user_session_token: Optional[str] = None,
        requested_token_type: Optional[str | OAuthTokenType] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a user-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = OAuthTokenType.USER_SESSION_TOKEN
        if user_session_token:
            data["subject_token"] = user_session_token
        if requested_token_type:
            data["requested_token_type"] = requested_token_type

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())

    def get_content_credentials(
        self,
        content_session_token: Optional[str] = None,
        requested_token_type: Optional[str | OAuthTokenType] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a content-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = OAuthTokenType.CONTENT_SESSION_TOKEN
        data["subject_token"] = content_session_token or _get_content_session_token()
        if requested_token_type:
            data["requested_token_type"] = requested_token_type

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
