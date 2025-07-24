from __future__ import annotations

import os

from typing_extensions import TYPE_CHECKING, Optional, TypedDict

from ..oauth import types
from ..resources import Resources
from .integrations import Integrations
from .sessions import Sessions

if TYPE_CHECKING:
    from ..context import Context

# Adding constants for backwards compatibility
# Moving these could break existing code that imports them directly
GRANT_TYPE = types.GRANT_TYPE

OAuthTokenType = types.OAuthTokenType


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
        user_session_token: str,
        requested_token_type: Optional[str | types.OAuthTokenType] = None,
        audience: Optional[str] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a user-session-token.

        Parameters
        ----------
        user_session_token : str
            The user session token to use for the exchange.
        requested_token_type : str or OAuthTokenType, optional
            The type of token being requested. This can be one of the predefined types in `OAuthTokenType` or a custom string.
        audience : str, optional
            The intended audience for the token. This must be a valid integration GUID.

        Returns
        -------
        Credentials
            The credentials obtained from the exchange.
        """
        # craft a credential exchange request
        data = {}
        data["grant_type"] = types.GRANT_TYPE
        data["subject_token_type"] = types.OAuthTokenType.USER_SESSION_TOKEN
        data["subject_token"] = user_session_token
        if requested_token_type:
            data["requested_token_type"] = requested_token_type
        if audience:
            data["audience"] = audience

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())

    def get_content_credentials(
        self,
        content_session_token: Optional[str] = None,
        requested_token_type: Optional[str | types.OAuthTokenType] = None,
        audience: Optional[str] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a content-session-token.

        Parameters
        ----------
        content_session_token : str, optional
            The content session token to use for the exchange. If not provided, the function will attempt to read the token from the environment variable 'CONNECT_CONTENT_SESSION_TOKEN'.
        requested_token_type : str or OAuthTokenType, optional
            The type of token being requested. This can be one of the predefined types in `OAuthTokenType` or a custom string.
        audience : str, optional
            The intended audience for the token. This must be a valid integration GUID.

        Returns
        -------
        Credentials
            The credentials obtained from the exchange.

        """
        # craft a credential exchange request
        data = {}
        data["grant_type"] = types.GRANT_TYPE
        data["subject_token_type"] = types.OAuthTokenType.CONTENT_SESSION_TOKEN
        data["subject_token"] = content_session_token or _get_content_session_token()
        if requested_token_type:
            data["requested_token_type"] = requested_token_type
        if audience:
            data["audience"] = audience

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
