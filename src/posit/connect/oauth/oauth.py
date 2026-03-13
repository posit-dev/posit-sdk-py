from __future__ import annotations

import logging
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


logger = logging.getLogger(__name__)


def _get_content_session_token() -> Optional[str]:
    """Return the content session token, if available.

    Reads the token from the file specified by the environment variable
    'CONNECT_CONTENT_SESSION_TOKEN_FILE' if set, otherwise falls back to the
    environment variable 'CONNECT_CONTENT_SESSION_TOKEN'.

    Returns
    -------
    Optional[str]
        The content session token, or None if not available.
    """
    token_file = os.environ.get("CONNECT_CONTENT_SESSION_TOKEN_FILE")
    if token_file:
        try:
            with open(token_file) as f:
                value = f.read().strip()
            if value:
                return value
            logger.warning(
                "CONNECT_CONTENT_SESSION_TOKEN_FILE is set to '%s', but the file is empty.",
                token_file,
            )
        except FileNotFoundError:
            pass

    return os.environ.get("CONNECT_CONTENT_SESSION_TOKEN")


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

    def has_content_credentials(self) -> bool:
        """Check whether OAuth content credentials are available.

        Returns True if a content session token is present in the environment,
        indicating that this code is running on Posit Connect with OAuth
        content credentials configured.

        Returns
        -------
        bool
        """
        return _get_content_session_token() is not None

    def get_content_credentials(
        self,
        content_session_token: Optional[str] = None,
        requested_token_type: Optional[str | types.OAuthTokenType] = None,
        audience: Optional[str] = None,
    ) -> Optional[Credentials]:
        """Perform an oauth credential exchange with a content-session-token.

        Parameters
        ----------
        content_session_token : str, optional
            The content session token to use for the exchange. If not provided, the function will attempt to read the token from the file specified by the environment variable 'CONNECT_CONTENT_SESSION_TOKEN_FILE', falling back to the environment variable 'CONNECT_CONTENT_SESSION_TOKEN'.
        requested_token_type : str or OAuthTokenType, optional
            The type of token being requested. This can be one of the predefined types in `OAuthTokenType` or a custom string.
        audience : str, optional
            The intended audience for the token. This must be a valid integration GUID.

        Returns
        -------
        Optional[Credentials]
            The credentials obtained from the exchange, or None if no content
            session token is available.
        """
        token = content_session_token or _get_content_session_token()
        if token is None:
            return None

        # craft a credential exchange request
        data = {}
        data["grant_type"] = types.GRANT_TYPE
        data["subject_token_type"] = types.OAuthTokenType.CONTENT_SESSION_TOKEN
        data["subject_token"] = token
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
